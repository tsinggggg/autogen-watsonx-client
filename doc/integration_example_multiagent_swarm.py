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

# ### this is an example usage of the Swarm pattern with 2 agents

# In[1]:


from typing import Any, Dict, List
import os
import asyncio
import aioconsole
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import HandoffTermination, TextMentionTermination
from autogen_agentchat.messages import HandoffMessage
from autogen_agentchat.teams import Swarm
from autogen_agentchat.ui import Console

from autogen_watsonx_client.config import WatsonxClientConfiguration
from autogen_watsonx_client.client import WatsonXChatCompletionClient


# In[2]:


wx_config = WatsonxClientConfiguration(
    model_id="meta-llama/llama-3-3-70b-instruct",  # pick a model you have access to on wx.ai here
    api_key=os.environ.get("WATSONX_API_KEY"),
    url=os.environ.get("WATSONX_URL"),
    space_id=os.environ.get("WATSONX_SPACE_ID"),
    project_id=os.environ.get("WATSONX_PROJECT_ID"),
    temperature=0.2,
)

wx_client = WatsonXChatCompletionClient(**wx_config)


# ### Tools

# In[3]:


def refund_flight(flight_id: int) -> str:
    """Refund a flight"""
    return f"Flight {flight_id} refunded"


# In[4]:


travel_agent = AssistantAgent(
    "travel_agent",
    model_client=wx_client,
    handoffs=["flights_refunder", "user"],
    system_message="""You are a travel agent.
    The flights_refunder is in charge of refunding flights.
    If you need information from the user, you must first send your message, then you can handoff to the user.
    Say TERMINATE in natural language when the travel planning is complete.""",
)

flights_refunder = AssistantAgent(
    "flights_refunder",
    model_client=wx_client,
    handoffs=["travel_agent", "user"],
    tools=[refund_flight],
    system_message="""You are an agent specialized in refunding flights.
    You have the ability to refund a flight using the refund_flight tool. Only make one tool call at a time.
    Do NOT make up arguments. Always ask user in natural language to provide the arguments, then handoff to user.
    Extremely important: Do NOT handoff to user without sending your message.
    When the transaction is complete, handoff to the travel agent to finalize.""",
)


# In[5]:


termination = HandoffTermination(target="user") | TextMentionTermination("TERMINATE")
team = Swarm([travel_agent, flights_refunder], termination_condition=termination)


# In[6]:


task = "I need to refund my flight."


async def run_team_stream() -> None:
    task_result = await Console(team.run_stream(task=task))
    last_message = task_result.messages[-1]

    while isinstance(last_message, HandoffMessage) and last_message.target == "user":
        user_message = await aioconsole.ainput("User: ")

        task_result = await Console(
            team.run_stream(task=HandoffMessage(source="user", target=last_message.source, content=user_message))
        )
        last_message = task_result.messages[-1]


if __name__ == "__main__":
    asyncio.run(run_team_stream())
