import sys
import asyncio

sys.path.append('/Users/shhaofu/Code/cursor-projects/p-llm-agent-museum')
from agents.qa_agent import QAAgent
from agentscope.message import Msg

async def test_qa_agent():
    # 初始化智能体
    agent = QAAgent()
    
    # 创建测试消息
    msg = Msg(name='user', content='博物馆有哪些展览？', role='user')
    
    # 调用reply方法
    response = await agent.reply(msg)
    
    # 输出结果
    print(f'测试成功! 响应: {response.content[:50]}...')

if __name__ == "__main__":
    asyncio.run(test_qa_agent())