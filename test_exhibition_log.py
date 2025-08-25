import sys
import asyncio

sys.path.append('/Users/shhaofu/Code/cursor-projects/p-llm-agent-museum')
from agents.qa_agent import QAAgent
from agentscope.message import Msg

async def test_exhibition_query():
    # 初始化智能体
    print("初始化QAAgent...")
    agent = QAAgent()
    
    # 创建测试消息 - 展览查询
    print("\n测试展览查询功能...")
    exhibition_msg = Msg(name='user', content='博物馆当前有哪些特别展览？', role='user')
    
    # 调用reply方法
    print("调用reply方法处理请求...")
    response = await agent.reply(exhibition_msg)
    
    # 输出结果
    print(f'\n测试完成! 响应内容: {response.content[:100]}...')

if __name__ == "__main__":
    print("开始测试QAAgent的展览查询日志功能...")
    asyncio.run(test_exhibition_query())