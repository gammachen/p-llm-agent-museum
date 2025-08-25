from typing import Dict, Any, Optional
from agentscope.agent import AgentBase
from agentscope.formatter import OllamaChatFormatter
from agentscope.memory import InMemoryMemory
from agentscope.model import OllamaChatModel
from agentscope.tool import Toolkit
from utils.agent_tools import (
    execute_museum_service,
    search_collection_info,
    get_collection_environment_data,
    create_exhibition_loan_request,
    send_museum_email
)
from agentscope.message import Msg

class CollectionManagementAgent(AgentBase):
    """博物馆藏品管理智能体"""
    
    def __init__(self):
        # 初始化工具集
        toolkit = Toolkit()
        toolkit.register_tool_function(execute_museum_service)
        toolkit.register_tool_function(search_collection_info)
        toolkit.register_tool_function(get_collection_environment_data)
        toolkit.register_tool_function(create_exhibition_loan_request)
        toolkit.register_tool_function(send_museum_email)
        
        self.model = OllamaChatModel(
            model_name="qwen2:latest",
            enable_thinking=False,
            stream=True,
        )
        
        self.formatter = OllamaChatFormatter()
        self.toolkit = toolkit
        self.memory = InMemoryMemory()
        self.name = "CollectionManagementAgent"
    
    async def reply(self, x: Any = None, **kwargs) -> Msg:
        """处理藏品管理相关的请求"""
        if x is None:
            return Msg(name=self.name, content="您好！我是博物馆的藏品管理助手，请问有什么可以帮助您的？")
        
        # 从输入中提取信息
        user_message = x.content if isinstance(x, Msg) else str(x)
        
        # 分析用户意图并调用相应功能
        if any(keyword in user_message for keyword in ["藏品列表", "所有藏品", "藏品概览"]):
            response = await self._get_collection_list(user_message)
        elif any(keyword in user_message for keyword in ["藏品详情", "藏品信息", "查看藏品"]):
            response = await self._get_collection_detail(user_message)
        elif any(keyword in user_message for keyword in ["环境监测", "温湿度", "保存环境"]):
            response = await self._get_environment_data(user_message)
        elif any(keyword in user_message for keyword in ["借展申请", "外借展品", "展品借出"]):
            response = await self._handle_loan_request(user_message)
        elif any(keyword in user_message for keyword in ["搜索藏品", "查找藏品"]):
            response = await self._search_collection(user_message)
        else:
            response = "请问您需要查询藏品列表、获取藏品详情、查看环境监测数据，还是处理借展申请？"
        
        # 将结果添加到记忆中
        self.memory.add(x)
        self.memory.add(Msg(name=self.name, content=response))
        
        # 返回响应
        return Msg(name=self.name, content=response)
    
    async def _get_collection_list(self, user_message: str) -> str:
        """获取藏品列表"""
        # 调用服务获取藏品列表
        result = execute_museum_service(endpoint="/api/internal/collection/list")
        
        if result.get("status") == "success":
            collections = result.get("data", [])
            if not collections:
                return "暂无藏品记录。"
            
            response = "藏品列表：\n"
            for collection in collections[:10]:  # 只显示前10个藏品
                response += f"- ID: {collection.get('collection_id', '')}, 名称: {collection.get('name', '')}, " \
                          f"年代: {collection.get('era', '不详')}\n"
            return response
        else:
            return f"获取失败：{result.get('message', '未知错误')}"
    
    async def _get_collection_detail(self, user_message: str) -> str:
        """获取藏品详情"""
        # 模拟从用户消息中提取藏品ID或名称
        # 在实际应用中，这里可以使用NLP技术更精确地提取信息
        collection_id = self._extract_collection_id(user_message)
        if not collection_id:
            return "请提供藏品的ID或名称，我可以为您查询详情。"
        
        # 调用服务获取藏品详情
        result = execute_museum_service(
            endpoint=f"/api/internal/collection/detail",
            params={"collection_id": collection_id}
        )
        
        if result.get("status") == "success":
            collection = result.get("data", {})
            return f"藏品详情：\n" \
                   f"ID: {collection.get('collection_id', '')}\n" \
                   f"名称: {collection.get('name', '')}\n" \
                   f"年代: {collection.get('era', '不详')}\n" \
                   f"来源: {collection.get('source', '不详')}\n" \
                   f"尺寸: {collection.get('dimensions', '不详')}\n" \
                   f"材质: {collection.get('material', '不详')}\n" \
                   f"描述: {collection.get('description', '暂无描述')}\n" \
                   f"当前位置: {collection.get('current_location', '不详')}\n" \
                   f"保存状态: {collection.get('conservation_status', '不详')}"
        else:
            return f"获取失败：{result.get('message', '未知错误')}"
    
    async def _get_environment_data(self, user_message: str) -> str:
        """获取环境监测数据"""
        # 模拟从用户消息中提取藏品ID或展厅位置
        # 在实际应用中，这里可以使用NLP技术更精确地提取信息
        location = self._extract_location(user_message)
        if not location:
            location = "默认展厅"  # 使用默认值
        
        # 调用服务获取环境监测数据
        result = get_collection_environment_data(location)
        
        if result.get("status") == "success":
            env_data = result.get("data", {})
            return f"{location}的环境监测数据：\n" \
                   f"温度: {env_data.get('temperature', '未知')}°C\n" \
                   f"湿度: {env_data.get('humidity', '未知')}%\n" \
                   f"光照: {env_data.get('light_intensity', '未知')} lux\n" \
                   f"空气质量: {env_data.get('air_quality', '未知')}\n" \
                   f"监测时间: {env_data.get('timestamp', '未知')}"
        else:
            return f"获取失败：{result.get('message', '未知错误')}"
    
    async def _handle_loan_request(self, user_message: str) -> str:
        """处理借展申请"""
        # 模拟从用户消息中提取借展信息
        # 在实际应用中，这里可以使用NLP技术更精确地提取信息
        loan_data = {
            "exhibition_name": "临时特展",  # 默认值，实际应用中应从用户输入提取
            "requesting_institution": "合作博物馆",  # 默认值，实际应用中应从用户输入提取
            "contact_person": "联系人",  # 默认值，实际应用中应从用户输入提取
            "contact_phone": "13800138000",  # 默认值，实际应用中应从用户输入提取
            "start_date": "2025-10-01",  # 默认值，实际应用中应从用户输入提取
            "end_date": "2025-12-31",  # 默认值，实际应用中应从用户输入提取
            "collection_ids": ["COL001"],  # 默认值，实际应用中应从用户输入提取
            "purpose": "文化交流"
        }
        
        # 调用服务创建借展申请
        result = create_exhibition_loan_request(loan_data)
        
        if result.get("status") == "success":
            loan_info = result.get("data", {})
            
            # 发送邮件通知相关人员
            email_content = f"新的借展申请已提交：\n" \
                          f"申请编号：{loan_info.get('loan_id', '')}\n" \
                          f"展览名称：{loan_info.get('exhibition_name', '')}\n" \
                          f"申请机构：{loan_info.get('requesting_institution', '')}\n" \
                          f"请及时处理。"
            send_museum_email(
                to="curator@museum.example.com",
                subject="新的借展申请通知",
                content=email_content
            )
            
            return f"借展申请已提交成功！申请编号是{loan_info.get('loan_id', '')}，我们会尽快处理您的申请。"
        else:
            return f"借展申请提交失败：{result.get('message', '未知错误')}"
    
    async def _search_collection(self, user_message: str) -> str:
        """搜索藏品"""
        # 模拟从用户消息中提取搜索关键词
        # 在实际应用中，这里可以使用NLP技术更精确地提取信息
        keywords = self._extract_keywords(user_message)
        if not keywords:
            return "请提供搜索关键词，我可以帮您查找相关藏品。"
        
        # 调用服务搜索藏品
        result = search_collection_info(keywords)
        
        if result.get("status") == "success":
            collections = result.get("data", [])
            if not collections:
                return f"未找到与'{keywords}'相关的藏品。"
            
            response = f"找到 {len(collections)} 件与'{keywords}'相关的藏品：\n"
            for collection in collections[:5]:  # 只显示前5个结果
                response += f"- ID: {collection.get('collection_id', '')}, 名称: {collection.get('name', '')}, " \
                          f"年代: {collection.get('era', '不详')}\n"
            return response
        else:
            return f"搜索失败：{result.get('message', '未知错误')}"
    
    def _extract_collection_id(self, text: str) -> str:
        """从文本中提取藏品ID"""
        # 这里是一个简单的ID提取示例
        # 在实际应用中，可以使用正则表达式或更复杂的NLP技术
        import re
        match = re.search(r'COL\d+', text)
        if match:
            return match.group(0)
        return ""
    
    def _extract_location(self, text: str) -> str:
        """从文本中提取位置信息"""
        # 这里是一个简单的位置提取示例
        # 在实际应用中，可以使用更复杂的NLP技术
        locations = ["一层", "二层", "三层", "东厅", "西厅", "南厅", "北厅", "中厅"]
        for loc in locations:
            if loc in text:
                return loc
        return ""
    
    def _extract_keywords(self, text: str) -> str:
        """从文本中提取关键词"""
        # 这里是一个简单的关键词提取示例
        # 在实际应用中，可以使用更复杂的NLP技术
        stop_words = ["搜索", "查找", "关于", "的", "有", "什么", "哪些", "吗", "是"]
        for word in stop_words:
            text = text.replace(word, "")
        
        # 移除多余的空格
        text = " ".join(text.split()).strip()
        return text