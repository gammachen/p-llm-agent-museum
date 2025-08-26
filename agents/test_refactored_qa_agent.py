#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
重构后的QAAgent测试文件
"""

import asyncio
import logging

from agents.qa_agent import QAAgent
from agentscope.message import Msg

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """测试重构后的QAAgent"""
    logger.info("开始测试重构后的QAAgent...")
    
    # 创建QAAgent实例
    qa_agent = QAAgent()
    
    # 测试用例
    test_cases = [
        "博物馆的开放时间是什么时候？",
        # "我想了解一下青铜鼎这件藏品的信息",
        # "最近有什么特展吗？",
        # "博物馆的票价是多少？",
        # "如何前往博物馆？"
    ]
    
    for i, question in enumerate(test_cases, 1):
        logger.info(f"\n=== 测试用例 {i}: {question} ===")
        
        # 构造用户消息
        user_msg = Msg(name="user", content=question, role="user")
        
        # 调用QAAgent处理
        response = await qa_agent(user_msg)
        
        # 输出结果
        logger.info(f"回答: {response.content}")
    
    logger.info("\n测试完成!")

if __name__ == "__main__":
    asyncio.run(main())
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
        Msg(name="user", content="你好，博物馆的公众人物都有哪些？", role="user"),  # 常见问题
        Msg(name="user", content="你好，博物馆的供应商都有哪些？", role="user"),  # 常见问题
        Msg(name="user", content="你好，博物馆的建筑格局是什么样的？", role="user"),  # 常见问题
        Msg(name="user", content="你好，博物馆的历史信息", role="user"),  # 常见问题
        # Msg(name="user", content="当前有什么特别的展览吗？", role="user"),  # 展览查询
        # Msg(name="user", content="馆内有哪些珍贵的文物藏品？", role="user"),  # 藏品查询
        # Msg(name="user", content="请介绍一下博物馆的历史背景", role="user")  # 一般咨询
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