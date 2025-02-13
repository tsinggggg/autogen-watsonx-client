#!/usr/bin/env python
# coding: utf-8

# ## Intro
# 
# This is an example notebook for demonstrating how the new [autogen>=0.4](https://github.com/microsoft/autogen) can utilize the LLMs hosted on [IBM® watsonx.ai™](https://www.ibm.com/products/watsonx-ai) by using the [autogen-watsonx-client](https://github.com/tsinggggg/autogen-watsonx-client)
# 
# ### prerequisites
# 
# - pip install --upgrade autogen-watsonx-client
# - pip install --upgrade autogen-agentchat>=0.4.6
# - access to a watsonx.ai instance, setting up environment variables `WATSONX_API_KEY`, one of `WATSONX_SPACE_ID` or `WATSONX_PROJECT_ID`, optionally `WATSONX_URL`

# In[1]:


import os
import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.ui import Console
from autogen_core import CancellationToken
from autogen_watsonx_client.config import WatsonxClientConfiguration
from autogen_watsonx_client.client import WatsonXChatCompletionClient


# In[2]:


wx_config = WatsonxClientConfiguration(
    model_id="meta-llama/llama-3-3-70b-instruct",  # pick a model you have access to on wx.ai here
    api_key=os.environ.get("WATSONX_API_KEY"),
    url=os.environ.get("WATSONX_URL"),
    space_id=os.environ.get("WATSONX_SPACE_ID"),
    project_id=os.environ.get("WATSONX_PROJECT_ID"),
)

wx_client = WatsonXChatCompletionClient(**wx_config)


# In[3]:


# Define a tool that searches the web for information.
async def web_search(query: str) -> str:
    """Find information on the web"""
    return "AutoGen is a programming framework for building multi-agent applications."


# Define an agent
agent = AssistantAgent(
    name="assistant",
    model_client=wx_client,
    tools=[web_search],
    system_message="Use tools to solve tasks.",
    model_client_stream=True,
)


async def assistant_run_stream() -> None:
    # Option 1: read each message from the stream (as shown in the previous example).
    # async for message in agent.on_messages_stream(
    #     [TextMessage(content="Find information on AutoGen", source="user")],
    #     cancellation_token=CancellationToken(),
    # ):
    #     print(message)

    # Option 2: use Console to print all messages as they appear.
    await Console(
        agent.on_messages_stream(
            [TextMessage(content="Find information on AutoGen", source="user")],
            cancellation_token=CancellationToken(),
        ),
        output_stats=True,  # Enable stats printing.
    )


if __name__ == "__main__":
    asyncio.run(assistant_run_stream())



