from typing import Optional

from typing_extensions import TypedDict


"""
see https://ibm.github.io/watsonx-ai-python-sdk/fm_model_inference.html
"""


class WatsonxCreateArguments(TypedDict, total=False):
    """
    ignored arguments from wx client:
    logprobs(boolean): whether to return logprobs
    n(int): number of choices to return
    response_format: keeping as default json_object
    time_limit(int)
    top_logprobs(int)
    """
    frequency_penalty: Optional[float]
    max_tokens: Optional[int]
    presence_penalty: Optional[float]
    temperature: Optional[float]
    top_p: Optional[float]


class WatsonxClientConfiguration(WatsonxCreateArguments, total=False):
    model_id: str
    api_key: str
    url: Optional[str]
    space_id: Optional[str]
    project_id: Optional[str]
