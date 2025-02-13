# Examples

This directory contains some agentic use cases with Autogen + watsonx client. All the examples have been converted to python scripts from jupyter notebooks, due to a switch in Autogen from using `sys.stdout` to `aoiconsole`, which doesn't seem to work well with jupyter.

- [simple one agent example](integration_example.py)

```
---------- user ----------
What is the weather in New York?
---------- weather_agent ----------
[FunctionCall(id='chatcmpl-tool-3955614a8267422d81bd99085ebf594f', arguments='{"city": "New York"}', name='get_weather')]
---------- weather_agent ----------
[FunctionExecutionResult(content='The weather in New York is 73 degrees and Sunny.', call_id='chatcmpl-tool-3955614a8267422d81bd99085ebf594f')]
---------- weather_agent ----------
The weather in New York is 73 degrees and Sunny.
---------- weather_agent ----------
TERMINATE
```

- [roundrobin pattern with 2 agents](integration_example_multiagent_round_robin.py)

```
---------- user ----------
What is the weather in New York and can you tell me how much is 123.45 EUR in USD so I can spend it on my holiday? 
---------- weather_agent ----------
[FunctionCall(id='chatcmpl-tool-4a17da3bac3744cd9b6e98dee67970d3', arguments='{"city": "New York"}', name='get_weather')]
---------- weather_agent ----------
[FunctionExecutionResult(content='The weather in New York is 73 degrees and Sunny.', call_id='chatcmpl-tool-4a17da3bac3744cd9b6e98dee67970d3')]
---------- weather_agent ----------
The weather in New York is 73 degrees and Sunny.
---------- currency_agent ----------
[FunctionCall(id='chatcmpl-tool-13c2e66d03fc4c469eb576ad15b87359', arguments='{"base_amount": "123.45", "base_currency": "EUR", "quote_currency": "USD"}', name='currency_calculator')]
---------- currency_agent ----------
[FunctionExecutionResult(content='135.80 USD', call_id='chatcmpl-tool-13c2e66d03fc4c469eb576ad15b87359')]
---------- currency_agent ----------
135.80 USD
---------- weather_agent ----------
TERMINATE
```

- [selector group chat pattern with 2 agents](integration_example_multiagent_selector_agent.py)

```
---------- user ----------
What is the weather in New York
---------- weather_agent ----------
[FunctionCall(id='chatcmpl-tool-778a916f0e2a467b97f5322f4ee3bc5f', arguments='{"city": "New York"}', name='get_weather')]
Enter your response: ---------- weather_agent ----------
[FunctionExecutionResult(content='The weather in New York is 73 degrees and Sunny.', call_id='chatcmpl-tool-778a916f0e2a467b97f5322f4ee3bc5f')]
---------- weather_agent ----------
The weather in New York is 73 degrees and Sunny.
now tell me how much EUR do i need to exchange for 1000 USD
---------- User ----------
now tell me how much EUR do i need to exchange for 1000 USD
---------- currency_agent ----------
[FunctionCall(id='chatcmpl-tool-5040db5755574b6ea7a9564dbddc987f', arguments='{"base_amount": "1000", "base_currency": "USD", "quote_currency": "EUR"}', name='currency_calculator')]
---------- currency_agent ----------
[FunctionExecutionResult(content='909.09 EUR', call_id='chatcmpl-tool-5040db5755574b6ea7a9564dbddc987f')]
---------- currency_agent ----------
909.09 EUR
Enter your response: ok i am good
---------- User ----------
ok i am good
---------- weather_agent ----------
TERMINATE
```

- [Swarm pattern with 2 agents](integration_example_multiagent_swarm.py)

```
---------- user ----------
I need to refund my flight.
---------- travel_agent ----------
[FunctionCall(id='chatcmpl-tool-b9fff4b82986444abd28c2d84f12026e', arguments='{}', name='transfer_to_flights_refunder')]
---------- travel_agent ----------
[FunctionExecutionResult(content='Transferred to flights_refunder, adopting the role of flights_refunder immediately.', call_id='chatcmpl-tool-b9fff4b82986444abd28c2d84f12026e')]
---------- travel_agent ----------
Transferred to flights_refunder, adopting the role of flights_refunder immediately.
---------- flights_refunder ----------
To proceed with refunding your flight, I will need to know the flight ID. Please provide the flight ID, and I will be happy to assist you further.
---------- flights_refunder ----------
[FunctionCall(id='chatcmpl-tool-35f933b1421e44738d38d7d688c46481', arguments='{}', name='transfer_to_user')]
---------- flights_refunder ----------
[FunctionExecutionResult(content='Transferred to user, adopting the role of user immediately.', call_id='chatcmpl-tool-35f933b1421e44738d38d7d688c46481')]
---------- flights_refunder ----------
Transferred to user, adopting the role of user immediately.
User: sure, it's 9527
---------- user ----------
sure, it's 9527
---------- flights_refunder ----------
[FunctionCall(id='chatcmpl-tool-4b7acd67874445eba8535d82bd7cc689', arguments='{"flight_id": "9527"}', name='refund_flight')]
---------- flights_refunder ----------
[FunctionExecutionResult(content='Flight 9527 refunded', call_id='chatcmpl-tool-4b7acd67874445eba8535d82bd7cc689')]
---------- flights_refunder ----------
Flight 9527 refunded
---------- flights_refunder ----------
[FunctionCall(id='chatcmpl-tool-d4783858bd484049b6b3c4c4f9124f37', arguments='{}', name='transfer_to_travel_agent')]
---------- flights_refunder ----------
[FunctionExecutionResult(content='Transferred to travel_agent, adopting the role of travel_agent immediately.', call_id='chatcmpl-tool-d4783858bd484049b6b3c4c4f9124f37')]
---------- flights_refunder ----------
Transferred to travel_agent, adopting the role of travel_agent immediately.
---------- travel_agent ----------
Your flight has been successfully refunded. If you need any further assistance or have any other travel-related inquiries, feel free to ask. Otherwise, we can consider your travel planning complete. TERMINATE
```

- [streaming example](integration_example_streaming.py)

```
---------- assistant ----------
[FunctionCall(id='chatcmpl-tool-2c62f8ac45a44aab96332958be772142', arguments='{"query": "AutoGen"}', name='web_search')]
[Prompt tokens: 0, Completion tokens: 0]
---------- assistant ----------
[FunctionExecutionResult(content='AutoGen is a programming framework for building multi-agent applications.', call_id='chatcmpl-tool-2c62f8ac45a44aab96332958be772142', is_error=False)]
---------- assistant ----------
AutoGen is a programming framework for building multi-agent applications.
---------- Summary ----------
Number of inner messages: 2
Total prompt tokens: 0
Total completion tokens: 0
Duration: 0.75 seconds
```