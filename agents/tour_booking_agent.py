from typing import Dict, Any, Optional
from agentscope.agent import ReActAgent
from agentscope.formatter import OllamaChatFormatter
from agentscope.memory import InMemoryMemory
from agentscope.model import OllamaChatModel
from agentscope.tool import Toolkit
from utils.agent_tools import MuseumToolkit
from agentscope.message import Msg

class TourBookingAgent(ReActAgent):
    """博物馆导览与预约智能体"""
    
    def __init__(self):
        # 初始化工具集
        toolkit = Toolkit()
        # 注册MuseumToolkit的方法作为工具
        toolkit.register_tool_function(MuseumToolkit.get_booking_info)
        toolkit.register_tool_function(MuseumToolkit.create_booking)
        toolkit.register_tool_function(MuseumToolkit.call_service)
        
        model = OllamaChatModel(
            model_name="qwen2:latest",
            enable_thinking=False,
            stream=True,
        )
        
        formatter = OllamaChatFormatter()
        memory = InMemoryMemory()
        name = "TourBookingAgent"
        sys_prompt = "你是博物馆的导览与预约助手，负责处理门票预约、参观路线规划等相关事务。"
        
        # 调用父类的初始化方法
        super().__init__(name=name, sys_prompt=sys_prompt, model=model, formatter=formatter, toolkit=toolkit, memory=memory)
    
    async def reply(self, x: Any = None, **kwargs) -> Msg:
        """处理用户的预约请求"""
        if x is None:
            return Msg(name=self.name, content="您好！我是博物馆的导览与预约助手，请问有什么可以帮助您的？")
        
        # 从输入中提取信息
        user_message = x.content if isinstance(x, Msg) else str(x)
        user_id = x.name if isinstance(x, Msg) else "anonymous"
        
        # 分析用户意图
        # 确保每个Msg对象都使用正确的初始化方式（包含name、role和content属性）
        content = [
            Msg(name="system", role="system", content="你是博物馆的导览与预约助手，负责处理门票预约、团队预约，并为用户生成个性化参观路线。"),
            Msg(name=user_id, role="user", content=user_message)
        ]
        
        # 使用模型理解用户意图
        model_input = await self.formatter.format(content)
        response = await self.model(model_input)
        
        # OllamaChatFormatter没有parse方法，直接使用response
        
        # 根据用户意图调用不同的功能
        if any(keyword in user_message for keyword in ["预约", "订票", "门票"]):
            result = await self._handle_booking(user_message, user_id)
        elif any(keyword in user_message for keyword in ["路线", "参观", "导览"]):
            result = await self._generate_route(user_message)
        elif any(keyword in user_message for keyword in ["查询", "查看", "我的"]):
            result = await self._query_booking(user_message)
        elif any(keyword in user_message for keyword in ["时段", "时间", "可用"]):
            result = await self._get_available_slots(user_message)
        else:
            result = "请问您需要预约门票、查询预约信息、了解可用时段，还是需要我为您生成个性化参观路线？"
        
        # 将结果添加到记忆中
        self.memory.add(x)
        self.memory.add(Msg(name=self.name, content=result))
        
        # 返回响应
        return Msg(name=self.name, content=result)
    
    async def _handle_booking(self, user_message: str, user_id: str) -> str:
        """处理预约请求"""
        # 模拟从用户消息中提取预约信息
        # 在实际应用中，这里可以使用NLP技术更精确地提取信息
        booking_data = {
            "visitor_name": "游客",  # 默认值，实际应用中应从用户输入提取
            "visitor_phone": "13800138000",  # 默认值，实际应用中应从用户输入提取
            "visit_date": "2025-08-26",  # 默认值，实际应用中应从用户输入提取
            "visit_time": "09:30-11:30",  # 默认值，实际应用中应从用户输入提取
            "ticket_type": "成人票",  # 默认值，实际应用中应从用户输入提取
            "ticket_count": 1  # 默认值，实际应用中应从用户输入提取
        }
        
        try:
            # 直接调用MuseumToolkit的方法
            result = MuseumToolkit.create_booking(booking_data)
            
            if result.get("status") == "success":
                booking_info = result.get("data", {})
                return f"预约成功！您的预约编号是{booking_info.get('booking_id', '')}，\n" \
                       f"预约日期：{booking_info.get('visit_date', '')}\n" \
                       f"预约时间：{booking_info.get('visit_time', '')}\n" \
                       f"票种：{booking_info.get('ticket_type', '')}\n" \
                       f"数量：{booking_info.get('ticket_count', '')}张\n" \
                       f"请在参观当天凭预约信息到博物馆入口处核销。"
            else:
                return f"预约失败：{result.get('message', '未知错误')}"
        except Exception as e:
            return f"处理预约请求时发生错误：{str(e)}"
    
    async def _generate_route(self, user_message: str) -> str:
        """生成个性化参观路线"""
        # 模拟生成路线
        # 在实际应用中，这里可以根据用户偏好、展览内容等生成更个性化的路线
        return "为您推荐的参观路线：\n" \
               "1. 一层：古埃及文明特展（预计参观时间：45分钟）\n" \
               "2. 二层：中国古代青铜器展（预计参观时间：60分钟）\n" \
               "3. 三层：现代艺术展（预计参观时间：45分钟）\n" \
               "全程预计用时约2小时，您可以根据自己的兴趣和时间调整参观顺序。"
    
    async def _query_booking(self, user_message: str) -> str:
        """查询预约信息"""
        # 模拟从用户消息中提取手机号
        phone = "13800138000"  # 默认值，实际应用中应从用户输入提取
        
        try:
            # 直接调用MuseumToolkit的方法
            result = MuseumToolkit.get_booking_info(phone)
            
            if result.get("status") == "success":
                bookings = result.get("data", [])
                if not bookings:
                    return "未找到您的预约记录，请确认手机号是否正确。"
                
                response = "您的预约记录：\n"
                for booking in bookings:
                    response += f"- 预约编号：{booking.get('booking_id', '')}\n" \
                              f"  预约日期：{booking.get('visit_date', '')}\n" \
                              f"  预约时间：{booking.get('visit_time', '')}\n" \
                              f"  状态：{booking.get('status', '')}\n"
                return response
            else:
                return f"查询失败：{result.get('message', '未知错误')}"
        except Exception as e:
            return f"查询预约信息时发生错误：{str(e)}"
    
    async def _get_available_slots(self, user_message: str) -> str:
        """获取可用时段"""
        try:
            # 直接调用MuseumToolkit的方法
            result = MuseumToolkit.call_service(
                endpoint="/api/public/tour-booking/available-slots",
                method="GET"
            )
            
            if result.get("status") == "success":
                slots = result.get("data", [])
                if not slots:
                    return "暂无可用预约时段。"
                
                response = "近期可用的预约时段：\n"
                for slot in slots[:2]:  # 只显示最近两天的
                    response += f"日期：{slot.get('date', '')}\n"
                    for time_slot in slot.get('time_slots', [])[:3]:  # 只显示前3个时段
                        response += f"  - {time_slot.get('time', '')}（剩余{time_slot.get('available', '')}个名额）\n"
                return response
            else:
                return f"获取失败：{result.get('message', '未知错误')}"
        except Exception as e:
            return f"获取可用时段时发生错误：{str(e)}"