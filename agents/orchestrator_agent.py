import asyncio
import os
from typing import Dict, Any, Optional, List

from agentscope.agent import ReActAgent, AgentBase, UserAgent
from agentscope.formatter import OllamaChatFormatter
from agentscope.memory import InMemoryMemory
from agentscope.model import OllamaChatModel
from agentscope.tool import Toolkit
from utils.agent_tools import (
    execute_museum_service,
    send_museum_email,
    get_museum_booking_info,
    create_museum_booking,
    ask_museum_question,
    submit_museum_feedback
)

class OrchestratorAgent(ReActAgent):
    """博物馆智能体系统的核心协调智能体"""
    
    def __init__(self):
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
    
    def register_agent(self, agent_name: str, agent: AgentBase) -> None:
        """注册一个专业智能体"""
        self.agents[agent_name] = agent
    
    def get_agent_by_intent(self, intent: str) -> Optional[AgentBase]:
        """根据意图获取对应的专业智能体"""
        # 简单的意图到智能体的映射
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
        return self.agents.get(agent_name) if agent_name else None

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
                    from agentscope.message import Msg
                    msg = Msg(
                        name=user_id,
                        content=message,
                        role="user",
                        content_blocks=[{"type": "text", "text": message}]
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

async def main() -> None:
    """测试核心协调智能体"""
    # 创建核心协调智能体
    orchestrator = OrchestratorAgent()
    user = UserAgent("Visitor")
    
    print("博物馆智能体系统已启动！输入'exit'退出。")
    
    msg = None
    while True:
        msg = await user(msg)
        if msg.get_text_content() == "exit":
            break
        
        # 处理用户请求
        result = await orchestrator.route_request(msg.get_text_content(), user.name)
        
        # 显示结果
        if result["status"] == "success":
            print(f"\n[系统响应] 意图: {result['intent']}, 处理方: {result['handled_by']}")
            print(f"{result['response']}")
        else:
            print(f"\n[错误] {result['message']}")
        
        print("\n请输入您的问题或需求:")

if __name__ == "__main__":
    asyncio.run(main())