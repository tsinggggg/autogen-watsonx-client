# Examples

This directory contains some agentic use cases with Autogen + watsonx client.

- [simple one agent example](integration_example.ipynb)

```
---------- user ----------
What is the weather in New York?
---------- weather_agent ----------
[FunctionCall(id='chatcmpl-tool-e29c8d140a60450799914943abffee3a', arguments='{"city": "New York"}', name='get_weather')]
[Prompt tokens: 237, Completion tokens: 19]
---------- weather_agent ----------
[FunctionExecutionResult(content='The weather in New York is 73 degrees and Sunny.', call_id='chatcmpl-tool-e29c8d140a60450799914943abffee3a')]
---------- weather_agent ----------
The weather in New York is 73 degrees and Sunny.
[Prompt tokens: 315, Completion tokens: 13]
---------- weather_agent ----------
<|python_tag|>TERMINATE
[Prompt tokens: 321, Completion tokens: 5]
---------- Summary ----------
Number of messages: 5
Finish reason: Text 'TERMINATE' mentioned
Total prompt tokens: 873
Total completion tokens: 37
Duration: 2.56 seconds
```

- [roundrobin pattern with 2 agents](integration_example_multiagent_round_robin.ipynb)

```
---------- user ----------
What is the weather in New York and can you tell me how much is 123.45 EUR in USD so I can spend it on my holiday? 
---------- weather_agent ----------
[FunctionCall(id='chatcmpl-tool-6591b444c1fa4098aae6181556921fd5', arguments='{"city": "New York"}', name='get_weather')]
[Prompt tokens: 304, Completion tokens: 25]
---------- weather_agent ----------
[FunctionExecutionResult(content='The weather in New York is 73 degrees and Sunny.', call_id='chatcmpl-tool-6591b444c1fa4098aae6181556921fd5')]
---------- weather_agent ----------
I don't have have access to a currency conversion function, but I can help with the rest of your request. The weather in New York is 73 degrees and Sunny.
[Prompt tokens: 338, Completion tokens: 36]
---------- currency_agent ----------
[FunctionCall(id='chatcmpl-tool-c30c4dcfb2e24a86b0ca3a709e3cc55c', arguments='{"base_amount": "123", "base_currency": "EUR", "quote_currency": "USD"}', name='currency_calculator')]
[Prompt tokens: 471, Completion tokens: 34]
---------- currency_agent ----------
[FunctionExecutionResult(content='135.30 USD', call_id='chatcmpl-tool-c30c4dcfb2e24a86b0ca3a709e3cc55c')]
---------- currency_agent ----------
You have 135.30 USD to spend on your holiday in New York, where the weather is 73 degrees and sunny.
[Prompt tokens: 512, Completion tokens: 27]
---------- weather_agent ----------
TERMINATE
[Prompt tokens: 454, Completion tokens: 4]
---------- Summary ----------
Number of messages: 8
Finish reason: Text 'TERMINATE' mentioned
Total prompt tokens: 2079
Total completion tokens: 126
Duration: 5.75 seconds

```

- [selector group chat pattern with 2 agents](integration_example_multiagent_selector_agent.ipynb)

```
---------- user ----------
What is the weather in New York
---------- weather_agent ----------
[FunctionCall(id='chatcmpl-tool-6ec4a0ce4b1341fcbec192e45d49bbb7', arguments='{"city": "New York"}', name='get_weather')]
[Prompt tokens: 287, Completion tokens: 19]
---------- weather_agent ----------
[FunctionExecutionResult(content='The weather in New York is 73 degrees and Sunny.', call_id='chatcmpl-tool-6ec4a0ce4b1341fcbec192e45d49bbb7')]
---------- weather_agent ----------
The weather in New York is 73 degrees and Sunny.
[Prompt tokens: 321, Completion tokens: 13]
Enter your response:  now tell me how much EUR do i need to exchange for 1000 USD
---------- User ----------
now tell me how much EUR do i need to exchange for 1000 USD
---------- currency_agent ----------
[FunctionCall(id='chatcmpl-tool-412164c8303046399fdf70fd133b1f7e', arguments='{"base_amount": "1000", "base_currency": "USD", "quote_currency": "EUR"}', name='currency_calculator')]
[Prompt tokens: 462, Completion tokens: 41]
---------- currency_agent ----------
[FunctionExecutionResult(content='909.09 EUR', call_id='chatcmpl-tool-412164c8303046399fdf70fd133b1f7e')]
---------- currency_agent ----------
You will need 909.09 EUR to exchange for 1000 USD.
[Prompt tokens: 504, Completion tokens: 17]
Enter your response:  ok i am good
---------- User ----------
ok i am good
---------- weather_agent ----------
TERMINATE
[Prompt tokens: 460, Completion tokens: 4]
---------- Summary ----------
Number of messages: 10
Finish reason: Text 'TERMINATE' mentioned
Total prompt tokens: 2034
Total completion tokens: 94
Duration: 59.81 seconds
```

- [Swarm pattern with 2 agents](integration_example_multiagent_swarm.ipynb)

```
---------- user ----------
I need to refund my flight.
---------- travel_agent ----------
[FunctionCall(id='chatcmpl-tool-105e2a3519f843948a0529a98ecbca61', arguments='{}', name='transfer_to_flights_refunder')]
[Prompt tokens: 269, Completion tokens: 23]
---------- travel_agent ----------
[FunctionExecutionResult(content='Transferred to flights_refunder, adopting the role of flights_refunder immediately.', call_id='chatcmpl-tool-105e2a3519f843948a0529a98ecbca61')]
---------- travel_agent ----------
Transferred to flights_refunder, adopting the role of flights_refunder immediately.
---------- flights_refunder ----------
To proceed with the refund, I will need to know the flight ID of the flight you would like to refund. Please provide the flight ID.
[Prompt tokens: 416, Completion tokens: 30]
---------- flights_refunder ----------
[FunctionCall(id='chatcmpl-tool-a4d8783e5ef14cb797e6571b6589f23f', arguments='{}', name='transfer_to_user')]
[Prompt tokens: 450, Completion tokens: 21]
---------- flights_refunder ----------
[FunctionExecutionResult(content='Transferred to user, adopting the role of user immediately.', call_id='chatcmpl-tool-a4d8783e5ef14cb797e6571b6589f23f')]
---------- flights_refunder ----------
Transferred to user, adopting the role of user immediately.
---------- Summary ----------
Number of messages: 8
Finish reason: Handoff to user from flights_refunder detected.
Total prompt tokens: 1135
Total completion tokens: 74
Duration: 4.45 seconds
User:  sure, it's 9527
---------- user ----------
sure, it's 9527
---------- flights_refunder ----------
[FunctionCall(id='chatcmpl-tool-6de6416f3f144bab805d1dba28e0dd5d', arguments='{"flight_id": "9527"}', name='refund_flight')]
[Prompt tokens: 503, Completion tokens: 26]
---------- flights_refunder ----------
[FunctionExecutionResult(content='Flight 9527 refunded', call_id='chatcmpl-tool-6de6416f3f144bab805d1dba28e0dd5d')]
---------- flights_refunder ----------
[FunctionCall(id='chatcmpl-tool-0da53053a18f4bf6b61b3fb752ab04d5', arguments='{}', name='transfer_to_travel_agent')]
[Prompt tokens: 542, Completion tokens: 15]
---------- flights_refunder ----------
[FunctionExecutionResult(content='Transferred to travel_agent, adopting the role of travel_agent immediately.', call_id='chatcmpl-tool-0da53053a18f4bf6b61b3fb752ab04d5')]
---------- flights_refunder ----------
Transferred to travel_agent, adopting the role of travel_agent immediately.
---------- travel_agent ----------
[FunctionCall(id='chatcmpl-tool-5c6e5e9bab0a49cd9e9f06ad85a937b7', arguments='{"flight_id": "9527"}', name='transfer_to_flights_refunder')]
[Prompt tokens: 399, Completion tokens: 30]
---------- travel_agent ----------
[FunctionExecutionResult(content='Transferred to flights_refunder, adopting the role of flights_refunder immediately.', call_id='chatcmpl-tool-5c6e5e9bab0a49cd9e9f06ad85a937b7')]
---------- travel_agent ----------
Transferred to flights_refunder, adopting the role of flights_refunder immediately.
---------- flights_refunder ----------
You have already been refunded for flight 9527. Is there anything else I can help you with?
[Prompt tokens: 607, Completion tokens: 22]
---------- flights_refunder ----------
[FunctionCall(id='chatcmpl-tool-064a2385d85144d88ea41545d9d63fe8', arguments='{}', name='transfer_to_user')]
[Prompt tokens: 633, Completion tokens: 14]
---------- flights_refunder ----------
[FunctionExecutionResult(content='Transferred to user, adopting the role of user immediately.', call_id='chatcmpl-tool-064a2385d85144d88ea41545d9d63fe8')]
---------- flights_refunder ----------
Transferred to user, adopting the role of user immediately.
---------- Summary ----------
Number of messages: 13
Finish reason: Handoff to user from flights_refunder detected.
Total prompt tokens: 2684
Total completion tokens: 107
Duration: 7.27 seconds
User:  no i am good
---------- user ----------
no i am good
---------- flights_refunder ----------
You're all set then. If you have any other flights you'd like to refund in the future, don't hesitate to reach out. Have a great day!
[Prompt tokens: 683, Completion tokens: 34]
---------- flights_refunder ----------
[FunctionCall(id='chatcmpl-tool-52909d8b80ea450cabcc8877e0ccf0b8', arguments='{}', name='transfer_to_travel_agent')]
[Prompt tokens: 721, Completion tokens: 15]
---------- flights_refunder ----------
[FunctionExecutionResult(content='Transferred to travel_agent, adopting the role of travel_agent immediately.', call_id='chatcmpl-tool-52909d8b80ea450cabcc8877e0ccf0b8')]
---------- flights_refunder ----------
Transferred to travel_agent, adopting the role of travel_agent immediately.
---------- travel_agent ----------
TERMINATE
[Prompt tokens: 562, Completion tokens: 4]
---------- Summary ----------
Number of messages: 6
Finish reason: Text 'TERMINATE' mentioned
Total prompt tokens: 1966
Total completion tokens: 53
Duration: 3.15 seconds
```