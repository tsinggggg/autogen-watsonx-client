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