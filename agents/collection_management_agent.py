from typing import Dict, Any, Optional
from agentscope.agent import ReActAgent
from agentscope.formatter import OllamaChatFormatter
from agentscope.memory import InMemoryMemory
from agentscope.model import OllamaChatModel
from agentscope.tool import Toolkit
from utils.agent_tools import (
    specific_question_about_the_museum,
    search_collection_info,
    get_collection_environment_data,
    create_exhibition_loan_request,
    send_museum_email
)
from agentscope.message import Msg

import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CollectionManagementAgent(ReActAgent):
    """博物馆藏品管理智能体"""
    
    def __init__(self):
        # 初始化工具集
        toolkit = Toolkit()

        toolkit.register_tool_function(search_collection_info, func_description="搜索藏品信息\n参数说明：\n- keywords: 字符串类型，必填参数，搜索关键词，用于匹配藏品名称、描述等信息")
        toolkit.register_tool_function(get_collection_environment_data, func_description="获取藏品环境监测数据\n参数说明：\n- location: 字符串类型，必填参数，监测位置，如展厅名称或位置标识")
        toolkit.register_tool_function(create_exhibition_loan_request, func_description="创建借展申请\n参数说明：\n- loan_data: 字典类型，必填参数，借展申请数据\n  包含字段：exhibition_name(展览名称)、requesting_institution(申请机构)、contact_person(联系人)、\n            contact_phone(联系电话)、start_date(开始日期)、end_date(结束日期)、collection_ids(藏品ID列表)、\n            purpose(借展目的)")
        toolkit.register_tool_function(send_museum_email, func_description="发送博物馆邮件通知\n参数说明：\n- recipient: 字符串类型，必填参数，收件人邮箱地址\n- subject: 字符串类型，必填参数，邮件主题\n- content: 字符串类型，必填参数，邮件内容")
        
        model = OllamaChatModel(
            model_name="qwen2:latest",
            enable_thinking=False,
            stream=True,
        )
        
        formatter = OllamaChatFormatter()
        memory = InMemoryMemory()
        name = "CollectionManagementAgent"
        sys_prompt = "你是博物馆的藏品管理助手，负责处理藏品相关的各种事务，包括藏品查询、环境监测、借展申请等。"
        
        # 调用父类的初始化方法
        super().__init__(name=name, sys_prompt=sys_prompt, model=model, formatter=formatter, toolkit=toolkit, memory=memory)
    
    async def reply(self, x: Any = None, **kwargs) -> Msg:
        """处理藏品管理相关的请求"""
        if x is None:
            return Msg(name=self.name, content="您好！我是博物馆的藏品管理助手，请问有什么可以帮助您的？", role="assistant")
        
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
        await self.memory.add(x)
        await self.memory.add(Msg(name=self.name, content=response, role="assistant"))
        
        # 返回响应
        return Msg(name=self.name, content=response, role="assistant")
    
    async def _get_collection_list(self, user_message: str) -> str:
        """获取藏品列表"""
        # 调用服务获取藏品列表
        tool_response = specific_question_about_the_museum(endpoint="/api/internal/collection/list")
        result = tool_response.metadata
        
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
        tool_response = specific_question_about_the_museum(
            endpoint=f"/api/internal/collection/detail/{collection_id}"
        )
        result = tool_response.metadata
        
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
        tool_response = get_collection_environment_data(location)
        result = tool_response.metadata
        
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
        tool_response = create_exhibition_loan_request(loan_data)
        result = tool_response.metadata
        
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
        tool_response = search_collection_info(keywords)
        result = tool_response.metadata
        
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
        # 查找完整格式的藏品ID COL2025001
        match = re.search(r'COL\d{7}', text)
        if match:
            return match.group(0)
        # 如果没有找到完整格式，尝试查找COL开头的简短ID COL001
        match = re.search(r'COL\d+', text)
        if match:
            col_id = match.group(0)
            # 如果是COL001这样的格式，转换为数据文件中的格式COL2025001
            if len(col_id) == 6 and col_id.startswith('COL'):
                return f"COL2025{col_id[3:]}"
            return col_id
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