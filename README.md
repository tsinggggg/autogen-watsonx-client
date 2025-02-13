# autogen-watsonx-client
This is an autogen>=0.4 extension for watsonx client integration.


## Disclaimer
- This is a community extension for the [Autogen](https://github.com/microsoft/autogen) project, specifically for the new [Autogen >= 0.4](https://microsoft.github.io/autogen/0.2/blog/2024/10/02/new-autogen-architecture-preview) architecture. The goal is to support IBM Watsonx.ai hosted LLMs in the Autogen framework.
- This project is still in a very early stage under development, please create issues in this github repo for bug reports.
- This project is a personal endeavor and is not affiliated with, endorsed by, or connected to any organization/employer in any way. The views, ideas, and opinions expressed in this project are solely my own and do not reflect those of others.


## Announcements
- 2025-02-13: `create_stream` is now implemented!
- 2025-01-13: the version requirement on Autogen has been updated to `>=0.4.1`, the integration examples have been updated accordingly, see [here](doc/README.md).

## Usage

### Prerequisites
- create a python environment with version `3.10` or above
- `pip install --upgrade autogen-watsonx-client`
- `pip install --upgrade autogen-agentchat>=0.4.1`
- access to a watsonx.ai instance, setting up environment variables `WATSONX_API_KEY`, one of `WATSONX_SPACE_ID` or `WATSONX_PROJECT_ID`, optionally `WATSONX_URL`


### code snippets

Importing dependencies:

```python
import os

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_watsonx_client.config import WatsonxClientConfiguration
from autogen_watsonx_client.client import WatsonXChatCompletionClient
```

Create a watsonx client

```python
wx_config = WatsonxClientConfiguration(
    model_id="meta-llama/llama-3-2-90b-vision-instruct",  # pick a model you have access to on wx.ai here
    api_key=os.environ.get("WATSONX_API_KEY"),
    url=os.environ.get("WATSONX_URL"),
    space_id=os.environ.get("WATSONX_SPACE_ID"),
    project_id=os.environ.get("WATSONX_PROJECT_ID"),
)

wx_client = WatsonXChatCompletionClient(**wx_config)
```

Define an agent using the watsonx client and register a dummy tool for querying weather

```python
# Define a tool
async def get_weather(city: str) -> str:
    return f"The weather in {city} is 73 degrees and Sunny."


async def main() -> None:
    # Define an agent
    weather_agent = AssistantAgent(
        name="weather_agent",
        model_client=wx_client,
        tools=[get_weather],
    )

    # Define termination condition
    termination = TextMentionTermination("TERMINATE")

    # Define a team
    agent_team = RoundRobinGroupChat([weather_agent], termination_condition=termination)

    # Run the team and stream messages to the console
    stream = agent_team.run_stream(task="What is the weather in New York?")
    await Console(stream)


# NOTE: if running this inside a Python script you'll need to use asyncio.run(main()).
await main()
```

Refer to [here](doc/README.md) for more detailed examples.