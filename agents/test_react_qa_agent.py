#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import asyncio
import logging

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("test_react_qa_agent")

# 导入必要的类和函数
from agents.qa_agent import QAAgent
from agentscope.message import Msg

async def test_react_qa_agent():
    """测试重构后的QAAgent是否按照ReAct模式正常工作"""
    logger.info("=== 开始测试重构后的QAAgent (ReAct模式) ===")
    
    try:
        # 初始化QAAgent
        logger.info("初始化QAAgent智能体...")
        qa_agent = QAAgent()
        logger.info("QAAgent智能体初始化成功！")
        
        # 测试用例1：常见问题 - 验证直接回答逻辑
        logger.info("\n=== 测试用例1：常见问题 ===")
        common_question = "博物馆的开放时间是什么时候？"
        logger.info(f"发送常见问题: {common_question}")
        response = await qa_agent.reply(Msg(name="user", content=common_question, role="user"))
        logger.info(f"智能体响应: {response.content}")
        
        # 测试用例2：藏品查询 - 验证ReAct推理和工具调用
        logger.info("\n=== 测试用例2：藏品查询 ===")
        collection_question = "请问有哪些宋代瓷器藏品？"
        logger.info(f"发送藏品查询: {collection_question}")
        response = await qa_agent.reply(Msg(name="user", content=collection_question, role="user"))
        logger.info(f"智能体响应: {response.content}")
        
        # 测试用例3：展览查询 - 验证ReAct推理和工具调用
        logger.info("\n=== 测试用例3：展览查询 ===")
        exhibition_question = "当前有什么特展吗？"
        logger.info(f"发送展览查询: {exhibition_question}")
        response = await qa_agent.reply(Msg(name="user", content=exhibition_question, role="user"))
        logger.info(f"智能体响应: {response.content}")
        
        # 测试用例4：一般咨询 - 验证大模型生成回答
        logger.info("\n=== 测试用例4：一般咨询 ===")
        general_question = "如何规划博物馆参观路线？"
        logger.info(f"发送一般咨询: {general_question}")
        response = await qa_agent.reply(Msg(name="user", content=general_question, role="user"))
        logger.info(f"智能体响应: {response.content}")
        
        # 测试用例5：__call__方法调用
        logger.info("\n=== 测试用例5：__call__方法调用 ===")
        call_question = "博物馆有餐厅吗？"
        logger.info(f"使用__call__方法调用: {call_question}")
        response = await qa_agent(call_question)
        logger.info(f"__call__方法响应: {response.content}")
        
        logger.info("\n=== QAAgent (ReAct模式) 测试完成 ===")
        
    except Exception as e:
        logger.error(f"测试过程中发生错误: {type(e).__name__} - {str(e)}")
        raise

if __name__ == "__main__":
    try:
        # 运行测试
        asyncio.run(test_react_qa_agent())
    except KeyboardInterrupt:
        logger.info("测试被用户中断")
        sys.exit(0)
    except Exception as e:
        logger.error(f"测试失败: {str(e)}")
        sys.exit(1)