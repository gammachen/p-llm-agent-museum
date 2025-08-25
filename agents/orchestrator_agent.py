import asyncio
import os
from typing import Dict, Any, Optional, List

from agentscope.agent import ReActAgent, AgentBase, UserAgent
from agentscope.formatter import OllamaChatFormatter
from agentscope.memory import InMemoryMemory
from agentscope.model import OllamaChatModel
from agentscope.tool import Toolkit
from agentscope.message import Msg
from utils.agent_tools import (
    execute_museum_service,
    send_museum_email,
    get_museum_booking_info,
    create_museum_booking,
    ask_museum_question,
    submit_museum_feedback
)

# 导入所有专业智能体
from agents.tour_booking_agent import TourBookingAgent
from agents.qa_agent import QAAgent
from agents.collection_management_agent import CollectionManagementAgent

import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OrchestratorAgent(ReActAgent):
    """博物馆智能体系统的核心协调智能体"""
    
    def __init__(self):
        logger.info("[核心协调智能体] 开始初始化...")
        
        # 初始化工具集
        toolkit = Toolkit()
        toolkit.register_tool_function(execute_museum_service)
        toolkit.register_tool_function(send_museum_email)
        toolkit.register_tool_function(get_museum_booking_info)
        toolkit.register_tool_function(create_museum_booking)
        toolkit.register_tool_function(ask_museum_question)
        toolkit.register_tool_function(submit_museum_feedback)
        
        # 设置智能体参数
        name = "OrchestratorAgent"
        sys_prompt = """你是博物馆智能体系统的核心协调智能体，负责：
1. 接收所有内外部请求
2. 进行意图识别
3. 路由给最合适的专业智能体处理
4. 维护整个系统的对话状态和任务上下文

你可以使用工具来调用博物馆服务API获取信息或执行操作。"""
        
        model = OllamaChatModel(
            model_name="qwen2:latest",
            enable_thinking=False,
            stream=True,
        )
        
        formatter = OllamaChatFormatter()
        
        # 调用父类的初始化方法，传递所有必要的参数
        super().__init__(
            name=name,
            sys_prompt=sys_prompt,
            model=model,
            formatter=formatter,
            toolkit=toolkit,
            memory=InMemoryMemory()
        )
        
        # 智能体系统中的其他专业智能体
        self.agents: Dict[str, AgentBase] = {}
        
        # 注册所有专业智能体
        self._register_all_agents()
        
        logger.info("[核心协调智能体] 初始化完成 - 已加载6个工具函数，使用模型: qwen2:latest，注册了{}个专业智能体".format(len(self.agents)))
    
    def _register_all_agents(self) -> None:
        """注册所有可用的专业智能体
        
        此方法会自动创建并注册项目中已实现的所有专业智能体，
        确保核心协调智能体能够正确路由请求到对应的专业智能体。
        """
        logger.info("[核心协调智能体] 开始注册专业智能体...")
        
        # 记录注册前的智能体数量
        initial_count = len(self.agents)
        registered_count = 0
        failed_count = 0
        
        # 创建并注册 TourBookingAgent
        try:
            tour_booking_agent = TourBookingAgent()
            self.register_agent("TourBookingAgent", tour_booking_agent)
            registered_count += 1
        except Exception as e:
            logger.error(f"[核心协调智能体] 注册TourBookingAgent失败: {str(e)}")
            failed_count += 1
        
        # 创建并注册 QAAgent
        try:
            qa_agent = QAAgent()
            self.register_agent("QAAgent", qa_agent)
            registered_count += 1
        except Exception as e:
            logger.error(f"[核心协调智能体] 注册QAAgent失败: {str(e)}")
            failed_count += 1
        
        # 创建并注册 CollectionManagementAgent
        try:
            collection_agent = CollectionManagementAgent()
            self.register_agent("CollectionManagementAgent", collection_agent)
            registered_count += 1
        except Exception as e:
            logger.error(f"[核心协调智能体] 注册CollectionManagementAgent失败: {str(e)}")
            failed_count += 1
        
        # TODO: 未来可以根据需要添加更多智能体的注册
        # 例如: FacilityServiceAgent, FeedbackAgent 等
        
        logger.info(f"[核心协调智能体] 专业智能体注册完成 - 成功: {registered_count}, 失败: {failed_count}, 总计: {len(self.agents)}个智能体")
        
        # 记录已注册的智能体列表
        if self.agents:
            agent_names = ", ".join(self.agents.keys())
            logger.debug(f"[核心协调智能体] 已注册智能体列表: {agent_names}")
    
    def register_agent(self, agent_name: str, agent: AgentBase) -> None:
        """注册一个专业智能体"""
        self.agents[agent_name] = agent
        logger.info(f"[核心协调智能体] 成功注册专业智能体: {agent_name} ({agent.__class__.__name__})")
    
    def get_agent_by_intent(self, intent: str) -> Optional[AgentBase]:
        """根据意图获取对应的专业智能体"""
        # 简单的意图到智能体的映射 TODO 
        intent_to_agent = {
            "tour_booking": "TourBookingAgent",
            "qa": "QAAgent",
            "facility": "FacilityServiceAgent",
            "feedback": "FeedbackAgent",
            "collection": "CollectionManagementAgent",
            "security": "SecurityMonitoringAgent",
            "facility_management": "FacilityManagementAgent",
            "administration": "AdministrativeAssistantAgent",
            "analytics": "DataAnalyticsAgent"
        }
        
        agent_name = intent_to_agent.get(intent)
        
        logger.info(f"[核心协调智能体集合] - {self.agents}")

        agent = self.agents.get(agent_name) if agent_name else None
        
        if agent:
            logger.info(f"[核心协调智能体] 意图映射成功 - 意图: {intent} -> 智能体: {agent_name}")
        else:
            logger.info(f"[核心协调智能体] 未找到匹配的专业智能体 - 意图: {intent}")
        
        return agent
        
    def recognize_intent(self, message: str) -> str:
        """简单的意图识别逻辑，实际项目中可以替换为更复杂的NLP模型 TODO """
        message_lower = message.lower()
        
        # 意图关键词映射
        intent_keywords = {
            "tour_booking": ["预约", "预订", "门票", "参观"],
            "qa": ["展览", "藏品", "历史", "介绍", "开放时间", "青铜鼎", "木乃伊"],
            "facility": ["洗手间", "餐厅", "停车场", "寄存", "无障碍"],
            "feedback": ["投诉", "建议", "评价", "反馈"],
            "collection": ["藏品", "文物", "展品", "收藏"],
            "security": ["安保", "监控", "安全", "丢失"],
            "facility_management": ["维护", "维修", "设备", "设施"],
            "administration": ["审批", "报销", "请假", "会议"],
            "analytics": ["数据", "统计", "客流", "分析"]
        }
        
        # 基于关键词的意图匹配
        for intent, keywords in intent_keywords.items():
            for keyword in keywords:
                if keyword in message_lower:
                    logger.info(f"[核心协调智能体] 意图识别成功 - 消息: '{message[:50]}...' -> 意图: {intent} (匹配关键词: {keyword})")
                    return intent
        
        # 默认返回通用意图
        logger.info(f"[核心协调智能体] 意图识别 - 默认分类为'general' - 消息: '{message[:50]}...'")
        return "general"

    async def route_request(self, message: str, user_id: str) -> Dict[str, Any]:
        """路由请求到合适的智能体"""
        try:
            # 调用核心协调服务进行意图识别
            result = execute_museum_service(
                endpoint="/api/core/orchestrate",
                method="POST",
                data={"user_id": user_id, "message": message}
            )
            
            if result.get("status") == "success":
                intent = result.get("intent")
                target_service = result.get("target_service")
                
                # 尝试找到对应的智能体
                agent = self.get_agent_by_intent(intent)
                if agent:
                    # 构建消息并发送给目标智能体
                    msg = Msg(
                        name=user_id,
                        content=message,
                        role="user"
                    )
                    response = await agent(msg)
                    return {
                        "status": "success",
                        "intent": intent,
                        "handled_by": agent.name,
                        "response": response.content
                    }
                else:
                    # 如果没有对应的智能体，直接调用服务API
                    return {
                        "status": "success",
                        "intent": intent,
                        "handled_by": "service_api",
                        "service_url": target_service,
                        "response": result.get("next_steps", "请调用对应服务继续处理")
                    }
            else:
                return {
                    "status": "error",
                    "message": result.get("message", "意图识别失败")
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"路由请求失败: {str(e)}"
            }
            
    async def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理来自core_orchestrator的请求"""
        try:
            # 提取请求数据
            user_id = request_data.get("user_id")
            message = request_data.get("message")
            context = request_data.get("context", {})
            history = request_data.get("history", [])
            
            # 记录接收到的请求基本信息
            logger.info(f"[核心协调智能体] 收到请求 - 用户ID: {user_id}, 请求数据长度: {len(str(request_data))}字符")
            logger.debug(f"[核心协调智能体] 请求详细信息 - 消息: '{message[:100]}...', 上下文: {context}, 历史记录数量: {len(history)}")
            
            # 1. 进行意图识别
            logger.info(f"[核心协调智能体] 开始意图识别 - 消息: '{message[:50]}...'")
            intent = self.recognize_intent(message)
            
            # 2. 记录识别到的意图
            logger.info(f"[核心协调智能体] 意图识别完成 - 识别意图: {intent}")
            
            # 3. 尝试找到对应的专业智能体
            logger.info(f"[核心协调智能体] 查找匹配的专业智能体 - 意图: {intent}")
            agent = self.get_agent_by_intent(intent)
            
            if agent:
                # 4. 如果有对应的智能体，将请求路由给它
                logger.info(f"[核心协调智能体] 找到匹配的专业智能体 - 智能体名称: {agent.name}, 智能体类型: {agent.__class__.__name__}")
                
                # 构建消息对象
                msg = Msg(
                    name=user_id,
                    content=message,
                    role="user"
                )
                
                # 调用专业智能体处理请求
                logger.info(f"[核心协调智能体] 开始调用专业智能体处理请求 - 智能体: {agent.name}")
                response = await agent(msg)
                
                # 5. 记录智能体响应信息
                logger.info(f"[核心协调智能体] 专业智能体处理完成 - 智能体: {agent.name}, 响应状态: 成功")
                logger.debug(f"[核心协调智能体] 专业智能体响应内容 - {str(response.content)[:100]}...")
                
                # 返回处理结果
                return {
                    "status": "success",
                    "result": {
                        "response": response.content,
                        "intent": intent,
                        "handled_by": agent.name
                    },
                    "agent_info": {
                        "name": agent.name,
                        "type": "specialized"
                    }
                }
            else:
                # 6. 如果没有对应的智能体，使用默认的处理方式
                logger.info(f"[核心协调智能体] 未找到匹配的专业智能体，使用默认处理方式 - 意图: {intent}")
                
                # 根据不同意图返回不同的默认响应
                default_responses = {
                    "tour_booking": "您可以通过博物馆官方网站或微信公众号进行参观预约。",
                    "qa": "感谢您的提问。关于这个问题，我们的专家正在为您准备详细的回答。",
                    "facility": "博物馆内设有洗手间、餐厅、停车场等设施，您可以在参观指南中找到详细信息。",
                    "feedback": "感谢您的反馈，我们会认真对待并不断改进我们的服务。",
                    "collection": "博物馆藏有丰富的文物和艺术品，您可以通过官网搜索特定藏品的详细信息。",
                    "general": "感谢您的咨询，我们会尽快为您提供帮助。"
                }
                
                response_content = default_responses.get(intent, default_responses["general"])
                logger.info(f"[核心协调智能体] 默认处理完成 - 意图: {intent}, 响应内容: '{response_content[:50]}...'")
                
                return {
                    "status": "success",
                    "result": {
                        "response": response_content,
                        "intent": intent,
                        "handled_by": "default_processing"
                    },
                    "agent_info": {
                        "name": "OrchestratorAgent",
                        "type": "default"
                    }
                }
        except Exception as e:
            # 处理异常情况
            logger.error(f"[核心协调智能体] 处理请求时发生错误 - 错误类型: {type(e).__name__}, 错误消息: {str(e)}")
            logger.exception("[核心协调智能体] 异常详细信息: ")
            return {
                "status": "error",
                "code": 500,
                "message": str(e)
            }

async def main() -> None:
    """测试核心协调智能体"""
    # 创建核心协调智能体
    orchestrator = OrchestratorAgent()
    user = UserAgent("Visitor")
    
    logger.info("博物馆智能体系统已启动！输入'exit'退出。")
    
    msg = None
    while True:
        msg = await user(msg)
        if msg.get_text_content() == "exit":
            break
        
        # 处理用户请求
        result = await orchestrator.route_request(msg.get_text_content(), user.name)
        
        # 显示结果
        if result["status"] == "success":
            logger.info(f"\n[系统响应] 意图: {result['intent']}, 处理方: {result['handled_by']}")
            logger.info(f"{result['response']}")
        else:
            logger.info(f"\n[错误] {result['message']}")
        
        logger.info("\n请输入您的问题或需求:")

if __name__ == "__main__":
    asyncio.run(main())