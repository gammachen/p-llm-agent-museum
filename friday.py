# -*- coding: utf-8 -*-
"""The main entry point of the ReAct agent example."""
import asyncio
import os

from agentscope.agent import ReActAgent, UserAgent
from agentscope.formatter import DashScopeChatFormatter
from agentscope.formatter import OllamaChatFormatter
from agentscope.memory import InMemoryMemory
from agentscope.model import DashScopeChatModel
from agentscope.model import OllamaChatModel
from agentscope.tool import (
    Toolkit,
    execute_shell_command,
    execute_python_code,
    view_text_file,
)


async def main() -> None:
    """The main entry point for the ReAct agent example."""
    toolkit = Toolkit()
    toolkit.register_tool_function(execute_shell_command)
    toolkit.register_tool_function(execute_python_code)
    toolkit.register_tool_function(view_text_file)

    agent = ReActAgent(
        name="Friday",
        sys_prompt="You are a helpful assistant named Friday.",
        model=OllamaChatModel(
            # api_key="ollama",
            model_name="qwen2:latest",
            enable_thinking=False,
            stream=True,
        ),
        # formatter=DashScopeChatFormatter(),
        formatter=OllamaChatFormatter(),
        toolkit=toolkit,
        memory=InMemoryMemory(),
    )
    user = UserAgent("Bob")

    msg = None
    while True:
        msg = await user(msg)
        if msg.get_text_content() == "exit":
            break
        msg = await agent(msg)


asyncio.run(main())

'''
(agentscope) shhaofu@shhaofudeMacBook-Pro p-llm-agent-agentscope % python friday.py  
Traceback (most recent call last):
  File "/Users/shhaofu/Code/cursor-projects/p-llm-agent-agentscope/friday.py", line 49, in <module>
    asyncio.run(main())
  File "/opt/anaconda3/envs/agentscope/lib/python3.11/asyncio/runners.py", line 190, in run
    return runner.run(main)
           ^^^^^^^^^^^^^^^^
  File "/opt/anaconda3/envs/agentscope/lib/python3.11/asyncio/runners.py", line 118, in run
    return self._loop.run_until_complete(task)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/anaconda3/envs/agentscope/lib/python3.11/asyncio/base_events.py", line 654, in run_until_complete
    return future.result()
           ^^^^^^^^^^^^^^^
  File "/Users/shhaofu/Code/cursor-projects/p-llm-agent-agentscope/friday.py", line 29, in main
    model=OllamaChatModel(
          ^^^^^^^^^^^^^^^^
  File "/opt/anaconda3/envs/agentscope/lib/python3.11/site-packages/agentscope/model/_ollama_model.py", line 79, in __init__
    self.client = ollama.AsyncClient(
                  ^^^^^^^^^^^^^^^^^^^
  File "/opt/anaconda3/envs/agentscope/lib/python3.11/site-packages/ollama/_client.py", line 628, in __init__
    super().__init__(httpx.AsyncClient, host, **kwargs)
  File "/opt/anaconda3/envs/agentscope/lib/python3.11/site-packages/ollama/_client.py", line 93, in __init__
    self._client = client(
                   ^^^^^^^
TypeError: AsyncClient.__init__() got an unexpected keyword argument 'api_key'
(agentscope) shhaofu@shhaofudeMacBook-Pro p-llm-agent-agentscope % python friday.py
User Input: 写一个冒泡排序并执行
Bob: 写一个冒泡排序并执行
Friday: 为了完成这个任务，我们可以创建一个名为`bubble_sort`的函数来实现冒泡排序算法。在Python中编写该函数后，我们可以通过调用`execute_python_code`函数来运行它。

首先，让我们定义冒泡排序算法：

```python
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break
    return arr
```

接下来，我们将定义一个测试数组来执行冒泡排序：

```python
test_array = [64, 34, 25, 12, 22, 11, 90]
sorted_array = bubble_sort(test_array)
print("Sorted array:", sorted_array)
```

现在，我们可以通过调用`execute_python_code`函数来运行这段代码。请将此代码片段作为输入参数传递给该功能。

{
    "type": "tool_use",
    "id": "execute_python_code_0",
    "name": "execute_python_code",
    "input": {
        "code": "def bubble_sort(arr):\n    n = len(arr)\n    for i in range(n):\n        swapped = False\n        for j in range(0, n - i - 1):\n            if arr[j] > arr[j + 1]:\n                arr[j], arr[j + 1] = arr[j + 1], arr[j]\n                swapped = True\n        if not swapped:\n            break\n    return arr\n\n# Test array\ntest_array = [64, 34, 25, 12, 22, 11, 90]\nsorted_array = bubble_sort(test_array)\npd.DataFrame({\"Sorted array\": sorted_array})"
    }
}
system: {
    "type": "tool_result",
    "id": "execute_python_code_0",
    "name": "execute_python_code",
    "output": [
        {
            "type": "text",
            "text": "<returncode>1</returncode><stdout></stdout><stderr>Traceback (most recent call last):\n  File \"/var/folders/9l/kbk_mdlj0x5bcvscm_41pmbm0000gn/T/tmp2xz5aeg8/tmp_QXtCWv2e5gvdcMEczbGsST.py\", line 16, in <module>\n    pd.DataFrame({\"Sorted array\": sorted_array})\n    ^^\nNameError: name 'pd' is not defined. Did you mean: 'id'?\n</stderr>"
        }
    ]
}
Traceback (most recent call last):
  File "/Users/shhaofu/Code/cursor-projects/p-llm-agent-agentscope/friday.py", line 49, in <module>
    asyncio.run(main())
  File "/opt/anaconda3/envs/agentscope/lib/python3.11/asyncio/runners.py", line 190, in run
    return runner.run(main)
           ^^^^^^^^^^^^^^^^
  File "/opt/anaconda3/envs/agentscope/lib/python3.11/asyncio/runners.py", line 118, in run
    return self._loop.run_until_complete(task)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/anaconda3/envs/agentscope/lib/python3.11/asyncio/base_events.py", line 654, in run_until_complete
    return future.result()
           ^^^^^^^^^^^^^^^
  File "/Users/shhaofu/Code/cursor-projects/p-llm-agent-agentscope/friday.py", line 46, in main
    msg = await agent(msg)
          ^^^^^^^^^^^^^^^^
  File "/opt/anaconda3/envs/agentscope/lib/python3.11/site-packages/agentscope/agent/_agent_base.py", line 233, in __call__
    reply_msg = await self.reply(*args, **kwargs)
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/anaconda3/envs/agentscope/lib/python3.11/site-packages/agentscope/agent/_agent_meta.py", line 120, in async_wrapper
    current_output = await original_func(
                     ^^^^^^^^^^^^^^^^^^^^
  File "/opt/anaconda3/envs/agentscope/lib/python3.11/site-packages/agentscope/tracing/_trace.py", line 382, in wrapper
    return await func(self, *args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/anaconda3/envs/agentscope/lib/python3.11/site-packages/agentscope/agent/_react_agent.py", line 246, in reply
    msg_reasoning = await self._reasoning()
                    ^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/anaconda3/envs/agentscope/lib/python3.11/site-packages/agentscope/agent/_agent_meta.py", line 120, in async_wrapper
    current_output = await original_func(
                     ^^^^^^^^^^^^^^^^^^^^
  File "/opt/anaconda3/envs/agentscope/lib/python3.11/site-packages/agentscope/agent/_react_agent.py", line 298, in _reasoning
    res = await self.model(
          ^^^^^^^^^^^^^^^^^
  File "/opt/anaconda3/envs/agentscope/lib/python3.11/site-packages/agentscope/tracing/_trace.py", line 638, in async_wrapper
    return await func(self, *args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/anaconda3/envs/agentscope/lib/python3.11/site-packages/agentscope/model/_ollama_model.py", line 140, in __call__
    response = await self.client.chat(**kwargs)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/anaconda3/envs/agentscope/lib/python3.11/site-packages/ollama/_client.py", line 860, in chat
    messages=list(_copy_messages(messages)),
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/anaconda3/envs/agentscope/lib/python3.11/site-packages/ollama/_client.py", line 1153, in _copy_messages
    yield Message.model_validate(
          ^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/anaconda3/envs/agentscope/lib/python3.11/site-packages/pydantic/main.py", line 705, in model_validate
    return cls.__pydantic_validator__.validate_python(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
pydantic_core._pydantic_core.ValidationError: 1 validation error for Message
tool_calls.0.function.arguments
  Input should be a valid dictionary [type=dict_type, input_value='{"code": "def bubble_sor...ay\\": sorted_array})"}', input_type=str]
    For further information visit https://errors.pydantic.dev/2.11/v/dict_type
'''

