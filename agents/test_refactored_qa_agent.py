import sys
import asyncio
import logging
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).resolve().parent.parent))

from agents.qa_agent import QAAgent, Msg

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_qa_agent")

async def test_qa_agent_refactored():
    """测试重构后的QAAgent类是否正常工作"""
    # 初始化智能体
    logger.info("[测试] 初始化QAAgent...")
    qa_agent = QAAgent()
    logger.info("[测试] QAAgent初始化完成")
    
    # 创建测试消息
    test_messages = [
        Msg(name="user", content="你好，博物馆的开放时间是什么时候？", role="user"),  # 常见问题
        Msg(name="user", content="当前有什么特别的展览吗？", role="user"),  # 展览查询
        Msg(name="user", content="馆内有哪些珍贵的文物藏品？", role="user"),  # 藏品查询
        Msg(name="user", content="请介绍一下博物馆的历史背景", role="user")  # 一般咨询
    ]
    
    # 测试1: 直接调用reply方法
    logger.info("[测试] 测试1: 直接调用reply方法")
    for msg in test_messages:
        logger.info(f"[测试] 发送消息: {msg.content}")
        try:
            response = await qa_agent.reply(msg)
            logger.info(f"[测试] reply方法返回: {response.content}")
        except Exception as e:
            logger.error(f"[测试] reply方法调用失败: {str(e)}")
    
    # 测试2: 使用__call__方法 (框架标准调用方式)
    logger.info("\n[测试] 测试2: 使用__call__方法 (框架标准调用方式)")
    for msg in test_messages:
        logger.info(f"[测试] 发送消息: {msg.content}")
        try:
            # 这是框架标准的调用方式
            response = await qa_agent(msg)
            logger.info(f"[测试] __call__方法返回: {response.content}")
        except Exception as e:
            logger.error(f"[测试] __call__方法调用失败: {str(e)}")
    
    # 测试3: 无参数调用 (初始消息)
    logger.info("\n[测试] 测试3: 无参数调用 (初始消息)")
    try:
        initial_response = await qa_agent()
        logger.info(f"[测试] 无参数调用返回: {initial_response.content}")
    except Exception as e:
        logger.error(f"[测试] 无参数调用失败: {str(e)}")
    
    logger.info("\n[测试] 所有测试完成")

if __name__ == "__main__":
    # 运行测试
    try:
        asyncio.run(test_qa_agent_refactored())
    except KeyboardInterrupt:
        logger.info("[测试] 用户中断测试")
    except Exception as e:
        logger.error(f"[测试] 测试过程中发生未捕获异常: {str(e)}")