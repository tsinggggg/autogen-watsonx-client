import asyncio
from typing import Mapping, Optional, Sequence, Any, Union, AsyncGenerator
from dataclasses import asdict

from autogen_core import CancellationToken
from autogen_core import FunctionCall, Image
from autogen_core.tools import Tool, ToolSchema
from typing_extensions import Unpack

from autogen_core.models import (
    ChatCompletionClient, RequestUsage, LLMMessage, CreateResult, SystemMessage, AssistantMessage, UserMessage,
    FunctionExecutionResultMessage, ModelCapabilities, ModelInfo
)
from ibm_watsonx_ai.foundation_models import ModelInference

from autogen_watsonx_client.config import WatsonxClientConfiguration


def _add_usage(usage1: RequestUsage, usage2: RequestUsage) -> RequestUsage:
    return RequestUsage(
        prompt_tokens=usage1.prompt_tokens + usage2.prompt_tokens,
        completion_tokens=usage1.completion_tokens + usage2.completion_tokens,
    )


def _autogen_message_to_watsonx_message(message: LLMMessage):
    if isinstance(message, SystemMessage):
        return {
            "role": "system",
            "content": message.content
        }
    elif isinstance(message, AssistantMessage):
        converted_msg = {
            "role": "assistant",
        }
        if isinstance(message.content, str):
            converted_msg["content"] = message.content
            return converted_msg
        elif isinstance(message.content, list) and len(message.content) > 0 :
            if isinstance(message.content[0], FunctionCall):
                func_calls = [
                    {
                        "id": func_call.id,
                        "type": "function",
                        "function": {
                            "name": func_call.name,
                            "arguments": func_call. arguments,
                        }
                    }
                    for func_call in message.content
                ]
                converted_msg["tool_calls"] = func_calls
                return converted_msg

    elif isinstance(message, UserMessage):
        converted_msg = {
            "role": "user",
        }
        if isinstance(message.content, str):
            converted_msg["content"] = [
                {
                    "type": "text",
                    "text": message.content,
                }
            ]
            return converted_msg
        elif isinstance(message.content, list) and len(message.content) > 0:
            if isinstance(message.content[0], str):
                converted_msg["content"] = [
                    {
                        "type": "text",
                        "text": msg_content,
                    } for msg_content in message.content
                ]
                return converted_msg
            elif isinstance(message.content[0], Image):
                converted_msg["content"] = [
                    {
                        "type": "image_url",
                        "image_url": msg_content.data_uri,
                    } for msg_content in message.content
                ]
                return converted_msg

    elif isinstance(message, FunctionExecutionResultMessage):
        # for wx.ai, tool message is for only 1 tool call, see https://github.com/IBM/watsonx-ai-node-sdk/blob/d02db1884476331be576bf48d77ceb846e88a6c6/watsonx-ai-ml/vml_v1.ts#L6456-L6463
        return [
            {
                "role": "tool",
                "content": content.content,
                "tool_call_id": content.call_id
            }
            for content in message.content
        ]
    raise ValueError(
        f"error converting autogen message {asdict(message)}"
    )


def _autogen_tool_schema_to_watsonx_tool(tool: ToolSchema):
    ret = {
        "type": "function",
        "function": {
            "name": tool["name"],
        }
    }
    if "description" in tool:
        ret["function"]["description"] = tool["description"]

    if "parameters" in tool:
        params = tool["parameters"]
        ret["function"]["parameters"] = {
            "type": params["type"],
            "properties": params["properties"]
        }
        if "required" in params:
            ret["function"]["parameters"]["required"] = params["required"]
    return ret


def _autogen_tool_to_watsonx_tool(tool: Tool | ToolSchema):
    if isinstance(tool, dict): # typeddict does not support type check
        return _autogen_tool_schema_to_watsonx_tool(tool)
    elif isinstance(tool, Tool):
        return _autogen_tool_schema_to_watsonx_tool(tool.schema)


class WatsonXChatCompletionClient(ChatCompletionClient):
    def __init__(self, **kwargs: Unpack[WatsonxClientConfiguration]):

        copied_args = dict(kwargs).copy()
        self._raw_config = copied_args

        # url
        url = kwargs.pop("url", "https://us-south.ml.cloud.ibm.com")
        # api key is required
        api_key = kwargs.pop("api_key")
        # one of space_id or project_id should be provided
        space_id = kwargs.pop("space_id", None)
        project_id = kwargs.pop("project_id", None)
        if space_id is None and project_id is None:
            raise ValueError("At least one of space_id and project_id needs to be provided for watsonx client")
        # model id
        model_id = kwargs.pop("model_id")

        # decoding params
        wx_params = dict(kwargs).copy()

        # client
        self._client = ModelInference(
            model_id=model_id,
            credentials={
                "api_key": api_key,
                "url": url,
            },
            space_id=space_id,
            project_id=project_id,
            params=wx_params,
        )

        # usage
        self._total_usage = RequestUsage(prompt_tokens=0, completion_tokens=0)
        self._actual_usage = RequestUsage(prompt_tokens=0, completion_tokens=0)

    async def create(
        self,
        messages: Sequence[LLMMessage],
        tools: Sequence[Tool | ToolSchema] = [],
        json_output: Optional[bool] = None,
        extra_create_args: Mapping[str, Any] = {},
        cancellation_token: Optional[CancellationToken] = None,
    ) -> CreateResult:
        # TODO: support extra_create_args
        if extra_create_args:
            raise ValueError("extra_create_args is not supported for Watsonx client")
        if json_output is not None:
            raise ValueError("Watsonx client only supports json format output, do not provide `json_output`")

        # convert messages
        wx_messages = []
        for m in messages:
            converted_msg = _autogen_message_to_watsonx_message(m)
            if isinstance(converted_msg, list):
                wx_messages.extend(converted_msg)
            else:
                wx_messages.append(converted_msg)
        # convert tools
        converted_tools = [_autogen_tool_to_watsonx_tool(tool) for tool in tools]

        # TODO: update to async version when available
        # TODO: handle cancellation_token
        wx_response = self._client.chat(
            messages=wx_messages,
            tools=converted_tools
        )

        usage = RequestUsage(
            prompt_tokens=wx_response["usage"]["prompt_tokens"],
            completion_tokens=wx_response["usage"]["completion_tokens"],
        )

        # Limited to a single choice currently.
        choice = wx_response["choices"][0]

        # content
        content: str | list[FunctionCall]
        text_content = choice["message"].get("content")
        tool_calls_content = []
        for tool_call in choice["message"].get("tool_calls", []):
            tool_calls_content.append(
                FunctionCall(
                    id=tool_call["id"],
                    arguments=tool_call["function"]["arguments"],
                    name=tool_call["function"]["name"],  # TODO: normalize_name
                )
            )
        content = text_content if text_content is not None else tool_calls_content

        response = CreateResult(
            finish_reason=WatsonXChatCompletionClient.convert_finish_reason(choice["finish_reason"]),
            content=content,
            usage=usage,
            cached=False,
            # TODO: enable logprobs by default to feed them here
        )

        _add_usage(self._actual_usage, usage)
        _add_usage(self._total_usage, usage)

        return response

    async def create_stream(
        self,
        messages: Sequence[LLMMessage],
        tools: Sequence[Tool | ToolSchema] = [],
        json_output: Optional[bool] = None,
        extra_create_args: Mapping[str, Any] = {},
        cancellation_token: Optional[CancellationToken] = None,
    ) -> AsyncGenerator[Union[str, CreateResult], None]:

        # TODO: support extra_create_args
        if extra_create_args:
            raise ValueError("extra_create_args is not supported for Watsonx client")
        if json_output is not None:
            raise ValueError("Watsonx client only supports json format output, do not provide `json_output`")

        # convert messages
        wx_messages = []
        for m in messages:
            converted_msg = _autogen_message_to_watsonx_message(m)
            if isinstance(converted_msg, list):
                wx_messages.extend(converted_msg)
            else:
                wx_messages.append(converted_msg)
        # convert tools
        converted_tools = [_autogen_tool_to_watsonx_tool(tool) for tool in tools]
        # TODO: handle cancellation_token

        stream_future = asyncio.ensure_future(
            self._client.achat_stream(
            messages=wx_messages,
            tools=converted_tools
            )
        )

        stream = await stream_future

        # keep track of results from the chunks for the final CreateResult to yield
        contents = []
        full_tool_calls: dict[int, FunctionCall] = {}

        while True:
            try:
                chunk_future = asyncio.ensure_future(anext(stream))
                chunk = await chunk_future

                choice = chunk["choices"][0]

                # First try to get content (content could be empty string, especially the first delta)
                if "content" in choice["delta"]:
                    content = choice["delta"]["content"]
                    if len(content) > 0:
                        contents.append(content)
                        yield content
                    continue

                # Otherwise, get tool calls
                if "tool_calls" in choice["delta"]:
                    tool_calls = choice["delta"]["tool_calls"]
                    # when does tool_calls contain more than 1 item? it seems even when there are 2 func calls in one turn, they get generated sequentially
                    for tool_call_chunk in tool_calls:
                        idx = tool_call_chunk["index"]
                        if idx not in full_tool_calls:
                            full_tool_calls[idx] = FunctionCall(id="", arguments="", name="")

                        if "id" in tool_call_chunk:
                            full_tool_calls[idx].id += tool_call_chunk["id"]

                        if "function" in tool_call_chunk:
                            function = tool_call_chunk["function"]
                            if "name" in function:
                                full_tool_calls[idx].name += function["name"]
                            if "arguments" in function:
                                full_tool_calls[idx].arguments += function["arguments"]
                # TODO: handle logprobs

            except StopAsyncIteration:
                break

        content: Union[str, list[FunctionCall]]
        if len(contents) > 0:
            content = "".join(contents)
        else:
            content = list(full_tool_calls.values())

        # TODO: achat_stream endpoint doesn't seem to return usage at all...
        usage = RequestUsage(
            prompt_tokens=0,
            completion_tokens=0,
        )

        result = CreateResult(
            finish_reason=WatsonXChatCompletionClient.convert_finish_reason(choice["finish_reason"]),
            content=content,
            usage=usage,
            cached=False,
            # TODO: logprobs and thought
        )

        self._total_usage = _add_usage(self._total_usage, usage)
        self._actual_usage = _add_usage(self._actual_usage, usage)

        yield result

    def actual_usage(self) -> RequestUsage:
        return self._actual_usage

    def total_usage(self) -> RequestUsage:
        return self._total_usage

    def count_tokens(self, messages: Sequence[LLMMessage], tools: Sequence[Tool | ToolSchema] = []) -> int:
        # TODO: proper calculation by calling self._client.tokenize
        return 0

    def remaining_tokens(self, messages: Sequence[LLMMessage], tools: Sequence[Tool | ToolSchema] = []) -> int:
        # TODO: any watsonx api to support this?
        return 1

    @property
    def capabilities(self) -> ModelCapabilities:
        return ModelCapabilities(
            vision=True,
            function_calling=True,
            json_output=True,
        )

    @property
    def model_info(self) -> ModelInfo:
        return ModelInfo(
            vision=True,
            function_calling=True,
            json_output=True,
            family="watsonx",
        )

    # TODO: implement __get_state__ and __set_state__

    FINISH_REASONS = {
        "tool_calls": "function_calls",
        "stop": "stop",
    }

    @staticmethod
    def convert_finish_reason(wx_finish_reason):
        return WatsonXChatCompletionClient.FINISH_REASONS[wx_finish_reason]