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

# ### this is an example usage of the round robin group chat pattern with 2 agents

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
    temperature=0.2,
)

wx_client = WatsonXChatCompletionClient(**wx_config)


# In[3]:


# Define a tool
async def get_weather(city: str) -> str:
    return f"The weather in {city} is 73 degrees and Sunny."

# Define another tool
from typing import Literal, Annotated

CurrencySymbol = Literal["USD", "EUR"]

def exchange_rate(base_currency: CurrencySymbol, quote_currency: CurrencySymbol) -> float:
    if base_currency == quote_currency:
        return 1.0
    elif base_currency == "USD" and quote_currency == "EUR":
        return 1 / 1.1
    elif base_currency == "EUR" and quote_currency == "USD":
        return 1.1
    else:
        raise ValueError(f"Unknown currencies {base_currency}, {quote_currency}")
        
async def currency_calculator(
    base_amount: Annotated[float, "Amount of currency in base_currency"],
    base_currency: Annotated[CurrencySymbol, "Base currency"] = "USD",
    quote_currency: Annotated[CurrencySymbol, "Quote currency"] = "EUR",
) -> str:
    quote_amount = exchange_rate(base_currency, quote_currency) * base_amount
    return f"{format(quote_amount, '.2f')} {quote_currency}"


async def main() -> None:
    # Define an agent
    weather_agent = AssistantAgent(
        name="weather_agent",
        model_client=wx_client,
        tools=[get_weather],
        system_message=\
        "You specialize in requests about weather. Solve tasks ONLY by using your tools. "
        "Do what you can, ignore what you can't do."
        "Do NOT comment on your capabilitites."
        "You should always rephrase tool call results with your own language."
        "Do NOT make comments about anything other than weather topics."
        "Reply with 'TERMINATE' when the task has been completed.",
    )

    # Define another agent
    currency_agent = AssistantAgent(
        name="currency_agent",
        model_client=wx_client,
        tools=[currency_calculator],
        system_message=\
        "You specialize in requests about currency. Solve tasks ONLY by using your tools. "
        "Do what you can, ignore what you can't do."
        "Do NOT comment on your capabilitites."
        "You should always rephrase tool call results with your own language."
        "Do NOT make comments about anything other than currency topics."
        "Reply with 'TERMINATE' when the task has been completed.", 
    )

    # Define termination condition
    termination = TextMentionTermination("TERMINATE")

    # Define a team
    agent_team = RoundRobinGroupChat([weather_agent, currency_agent], termination_condition=termination)

    # Run the team and stream messages to the console
    stream = agent_team.run_stream(task="What is the weather in New York and can you tell me how much is 123.45 EUR in USD so I can spend it on my holiday? ")
    await Console(stream)


# NOTE: if running this inside a Python script you'll need to use asyncio.run(main()).
if __name__ == "__main__":
    asyncio.run(main())




