#!/usr/bin/env python
# coding: utf-8

# ## Intro
# 
# This is an example notebook for demonstrating how the new [autogen>=0.4](https://github.com/microsoft/autogen) can utilize the LLMs hosted on [IBM® watsonx.ai™](https://www.ibm.com/products/watsonx-ai) by using the [autogen-watsonx-client](https://github.com/tsinggggg/autogen-watsonx-client)
# 
# ### prerequisites
# 
# - pip install --upgrade autogen-watsonx-client
# - pip install --upgrade autogen-agentchat>=0.4.1
# - access to a watsonx.ai instance, setting up environment variables `WATSONX_API_KEY`, one of `WATSONX_SPACE_ID` or `WATSONX_PROJECT_ID`, optionally `WATSONX_URL`

# In[1]:


import os
import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
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
if __name__ == "__main__":
    asyncio.run(main())



