from typing import Dict, Any, Optional
from agentscope.agent import ReActAgent
from agentscope.formatter import OllamaChatFormatter
from agentscope.memory import InMemoryMemory
from agentscope.model import OllamaChatModel
from agentscope.tool import Toolkit
from utils.agent_tools import (
    execute_museum_service,
    search_collection_info,
    search_exhibition_info
)
from agentscope.message import Msg

import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QAAgent(ReActAgent):
    """博物馆咨询问答智能体
    
    负责回答游客关于博物馆的各种问题，包括但不限于开放时间、票价、
    交通、展览、藏品等信息，为游客提供便捷的咨询服务。
    
    遵循ReActAgent框架的推理-行动-反思设计模式
    """
    def __init__(self):
        logger.info("[咨询问答智能体] 开始初始化...")
        
        # 初始化工具集
        logger.info("[咨询问答智能体] 注册工具函数...")
        toolkit = Toolkit()
        toolkit.register_tool_function(execute_museum_service)
        toolkit.register_tool_function(search_collection_info)
        toolkit.register_tool_function(search_exhibition_info)
        logger.info("[咨询问答智能体] 工具函数注册完成，共注册3个工具")
        
        # 初始化模型
        logger.info("[咨询问答智能体] 初始化语言模型...")
        model = OllamaChatModel(
            model_name="qwen2:latest",
            enable_thinking=True,  # 启用思考功能，支持ReAct模式
            stream=True,
        )
        logger.info("[咨询问答智能体] 语言模型初始化完成 - 模型名称: qwen2:latest")
        
        # 初始化其他组件
        formatter = OllamaChatFormatter()
        memory = InMemoryMemory()
        name = "QAAgent"
        sys_prompt = "你是博物馆的咨询助手，负责回答关于博物馆的各种问题，包括开放时间、票价、交通、展览、藏品等信息。\n"
        sys_prompt += "请遵循推理-行动-反思的思考模式：\n"
        sys_prompt += "1. 首先思考用户的问题属于哪种类型（常见问题、藏品查询、展览查询或其他）\n"
        sys_prompt += "2. 如需使用工具，请在思考后选择合适的工具并提供参数\n"
        sys_prompt += "3. 根据工具返回结果或已有知识生成最终回答"
        
        # 调用父类的初始化方法
        super().__init__(name=name, sys_prompt=sys_prompt, model=model, formatter=formatter, toolkit=toolkit, memory=memory)
        
        # 常见问题的预设答案
        logger.info("[咨询问答智能体] 加载常见问题预设答案...")
        self.common_answers = {
            "开放时间": "博物馆的开放时间为周二至周日 09:00-17:00（16:30停止入场），周一闭馆（法定节假日除外）。",
            "票价": "成人票：60元/人，学生票：30元/人（凭有效学生证），老人票：30元/人（60岁以上凭有效证件），儿童票：20元/人（6-18岁），6岁以下儿童免费。",
            "交通": "您可以乘坐地铁2号线在博物馆站下车，从B出口步行约5分钟即可到达。也可以乘坐公交101、102、103路在博物馆站下车。",
            "停车": "博物馆地下停车场收费标准：小型车5元/小时，大型车10元/小时，当日单次停车最高收费50元。",
            "讲解服务": "博物馆提供免费的定时讲解服务，时间为10:00、13:00、15:00。您也可以租用语音导览器，租金30元/台，押金200元。",
            "寄存": "博物馆入口处提供免费寄存服务，贵重物品请自行保管。",
            "餐饮": "博物馆内设有咖啡厅和餐厅，提供简餐和饮料。",
            "摄影": "除特展外，博物馆内允许拍照，但禁止使用闪光灯和三脚架。"
        }
    
    def _reason(self, message: str) -> str:
        """实现推理过程，判断用户问题类型并决定是否使用工具
        
        Args:
            message: 用户的提问内容
        
        Returns:
            str: 思考过程的文本
        """
        logger.info(f"[咨询问答智能体] 开始推理 - 用户问题: '{message[:100]}...'" if len(message) > 100 else f"[咨询问答智能体] 开始推理 - 用户问题: '{message}'")
        
        # 检查是否为常见问题
        for key in self.common_answers:
            if key in message:
                logger.info(f"[咨询问答智能体] 推理结果: 识别为常见问题 - 问题类型: {key}")
                return f"我识别到用户的问题是关于'{key}'的常见问题，已有预设答案，无需使用工具。"
        
        # 分析用户问题类型
        if any(keyword in message for keyword in ["藏品", "文物", "艺术品", "展品"]):
            logger.info("[咨询问答智能体] 推理结果: 识别为藏品相关查询，需要使用search_collection_info工具")
            keywords = self._extract_keywords(message)
            
            return f"用户问题涉及藏品信息，需要使用search_collection_info工具查询。关键词：{keywords}"
        elif any(keyword in message for keyword in ["展览", "特展", "主题展"]):
            logger.info("[咨询问答智能体] 推理结果: 识别为展览相关查询，需要使用search_exhibition_info工具")
            keywords = self._extract_keywords(message)
            
            return f"用户问题涉及展览信息，需要使用search_exhibition_info工具查询。关键词：{keywords}"
        else:
            logger.info("[咨询问答智能体] 推理结果: 识别为一般咨询问题，可直接回答")
            return "用户问题属于一般咨询，已有的知识可以回答，无需使用工具。"
            
    async def _process_message(self, x: Any = None, **kwargs) -> Msg:
        """内部方法：处理用户的咨询问题，遵循ReAct模式
        
        Args:
            x: 用户输入，可以是Msg对象或其他类型
            **kwargs: 其他参数
        
        Returns:
            str: 处理后的回答内容
        """
        try:
            # 处理初始情况
            if x is None:
                logger.info("[咨询问答智能体] 收到初始请求，返回欢迎消息")
                return "您好！我是博物馆的咨询助手，请问有什么可以帮助您的？"
            
            # 从输入中提取信息
            user_id = x.name if hasattr(x, 'name') else "anonymous"
            user_message = x.content if isinstance(x, Msg) else str(x)
            
            logger.info(f"[咨询问答智能体] 收到用户请求 - 用户ID: {user_id}, 请求内容: '{user_message[:100]}...'" if len(user_message) > 100 else f"[咨询问答智能体] 收到用户请求 - 用户ID: {user_id}, 请求内容: '{user_message}'")
            
            # ReAct模式：1. 推理阶段
            thought = self._reason(user_message)
            logger.info(f"[咨询问答智能体] ReAct推理 - {thought}")
            
            # 检查是否为常见问题
            for key, answer in self.common_answers.items():
                if key in user_message:
                    logger.info(f"[咨询问答智能体] 使用预设答案回答常见问题 - 问题类型: {key}")
                    return answer
            
            # ReAct模式：2. 行动与反思阶段
            # 根据推理结果决定是否使用工具
            if "search_collection_info" in thought:
                # 使用工具搜索藏品信息
                keywords = self._extract_keywords(user_message)
                logger.info(f"[咨询问答智能体] ReAct行动 - 调用search_collection_info工具，关键词: {keywords}")
                
                tool_response = await self._call_tool("search_collection_info", [keywords])
                
                logger.info(f"[咨询问答智能体] ReAct反思 - 工具返回结果，处理藏品信息")
                
                return self._format_collection_response(tool_response)
            elif "search_exhibition_info" in thought:
                # 使用工具搜索展览信息
                keywords = self._extract_keywords(user_message)
                logger.info(f"[咨询问答智能体] ReAct行动 - 调用search_exhibition_info工具，关键词: {keywords}")
                
                tool_response = await self._call_tool("search_exhibition_info", [keywords])
                
                logger.info(f"[咨询问答智能体] ReAct反思 - 工具返回结果，处理展览信息")
                return self._format_exhibition_response(tool_response)
            else:
                # 对于其他问题，使用大模型生成回答
                logger.info("[咨询问答智能体] ReAct行动 - 使用大模型生成回答")
                return await self._generate_answer(user_message)
        except Exception as e:
            logger.error(f"[咨询问答智能体] 处理请求时发生错误 - 错误类型: {type(e).__name__}, 错误消息: {str(e)}")
            logger.exception("[咨询问答智能体] 异常详细信息: ")
            # 返回错误响应
            return "抱歉，处理您的请求时发生错误，请稍后再试。"
    
    async def reply(self, x: Any = None, **kwargs) -> Msg:
        """符合Agentscope框架标准的回复方法
        
        Args:
            x: 输入消息，可以是Msg对象或字符串
            **kwargs: 其他参数
        
        Returns:
            Msg: 包含回复内容的Msg对象
        """
        logger.info("[咨询问答智能体] 进入标准reply方法")
        
        # 处理输入消息
        if isinstance(x, str):
            # 如果输入是字符串，转换为Msg对象
            x = Msg(name="user", content=x, role="user")
        
        # 调用内部处理方法获取响应内容
        response_content = await self._process_message(x, **kwargs)
        
        # 将结果添加到记忆中（如果有输入消息）
        if x is not None:
            logger.debug("[咨询问答智能体] 更新记忆 - 添加用户请求和智能体响应")
            # 确保添加到记忆中的是Msg对象
            await self.memory.add(x)
            await self.memory.add(Msg(name=self.name, content=response_content, role="assistant"))
        
        # 返回符合框架要求的Msg对象
        logger.info(f"[咨询问答智能体] 请求处理完成 - 响应内容长度: {len(response_content)} 字符")
        return Msg(name=self.name, content=response_content, role="assistant")
    
    async def __call__(self, x: Any = None, **kwargs) -> Msg:
        """实现__call__方法，作为框架调用智能体的标准入口
        
        Args:
            x: 用户输入消息
            **kwargs: 其他参数
        
        Returns:
            Msg: 包含回答内容的消息对象
        """
        # 框架调用时，直接转发到reply方法
        return await self.reply(x, **kwargs)
    
    async def _call_tool(self, tool_name: str, tool_args: list) -> Any:
        """调用指定的工具
        
        Args:
            tool_name: 工具名称
            tool_args: 工具参数列表
        
        Returns:
            Any: 工具返回结果
        """
        try:
            logger.info(f"[咨询问答智能体] 调用工具 - 工具名称: {tool_name}, 参数: {tool_args}")
            
            # 根据工具名称直接调用对应的函数，不再通过toolkit获取
            if tool_name == "search_collection_info":
                result = search_collection_info(*tool_args)
            elif tool_name == "search_exhibition_info":
                result = search_exhibition_info(*tool_args)
            elif tool_name == "execute_museum_service":
                result = execute_museum_service(*tool_args)
            else:
                logger.error(f"[咨询问答智能体] 未知的工具名称: {tool_name}")
                return None
            
            logger.info(f"[咨询问答智能体] 工具调用成功 - 工具名称: {tool_name}")
            return result
        except Exception as e:
            logger.error(f"[咨询问答智能体] 工具调用失败 - 工具名称: {tool_name}, 错误: {str(e)}")
            return None
            
    def _format_collection_response(self, tool_response: Any) -> str:
        """格式化藏品查询结果
        
        Args:
            tool_response: 工具返回的原始结果
        
        Returns:
            str: 格式化后的藏品信息
        """
        if not tool_response:
            return "抱歉，查询藏品信息时出现错误，请稍后再试。"
            
        result = tool_response.metadata
        
        if result.get("status") == "success":
            collections = result.get("data", [])
            if not collections:
                # 从原始结果中获取查询的关键词（如果有）
                search_keywords = result.get("params", {}).get("keywords", "")
                return f"未找到相关的藏品信息。"
                
            
            # 只返回第一个匹配的藏品信息
            collection = collections[0]
            return f"{collection.get('name', '')}\n" \
                   f"年代：{collection.get('era', '不详')}\n" \
                   f"来源：{collection.get('source', '不详')}\n" \
                   f"描述：{collection.get('description', '暂无详细描述')}"
        else:
            return f"查询失败：{result.get('message', '未知错误')}"
            
    def _format_exhibition_response(self, tool_response: Any) -> str:
        """格式化展览查询结果
        
        Args:
            tool_response: 工具返回的原始结果
        
        Returns:
            str: 格式化后的展览信息
        """
        if not tool_response:
            return "抱歉，查询展览信息时出现错误，请稍后再试。"
            
        result = tool_response.metadata
        
        if result.get("status") == "success":
            exhibitions = result.get("data", [])
            if not exhibitions:
                return f"未找到相关的展览信息。"
            
            # 构建响应内容
            response = ""
            display_count = min(3, len(exhibitions))  # 只显示前3个展览
            
            for i, exhibition in enumerate(exhibitions[:display_count], 1):
                exhibition_name = exhibition.get('name', '')
                response += f"{exhibition_name}\n" \
                          f"时间：{exhibition.get('start_date', '不详')} 至 {exhibition.get('end_date', '不详')}\n" \
                          f"地点：{exhibition.get('location', '不详')}\n" \
                          f"简介：{exhibition.get('description', '暂无简介')}\n\n"
            
            return response.strip()
        else:
            return f"查询失败：{result.get('message', '未知错误')}"
    
    async def _generate_answer(self, user_message: str) -> str:
        """使用大模型生成回答
        
        Args:
            user_message: 用户的提问
        
        Returns:
            str: 生成的回答
        """
        try:
            logger.info(f"[咨询问答智能体] 使用大模型生成回答 - 用户问题: '{user_message[:100]}...'" if len(user_message) > 100 else f"[咨询问答智能体] 使用大模型生成回答 - 用户问题: '{user_message}'")
            
            # 调用大模型生成回答，使用正确的格式
            # 构建消息列表，符合OllamaChatModel的输入要求
            messages = [
                {"role": "system", "content": self.sys_prompt},
                {"role": "user", "content": user_message}
            ]
            
            # 直接调用模型生成回答
            response = await self.model(messages)
            
            # 从响应中提取回答内容
            if isinstance(response, dict) and "text" in response:
                answer = response["text"]
            elif hasattr(response, "content"):
                answer = response.content
            else:
                answer = "抱歉，我暂时无法为您提供该问题的回答。请稍后再试。"
            
            logger.info(f"[咨询问答智能体] 大模型回答生成完成 - 回答长度: {len(answer)} 字符")
            return answer
        except Exception as e:
            logger.error(f"[咨询问答智能体] 大模型生成回答时发生异常 - 错误类型: {type(e).__name__}, 错误消息: {str(e)}")
            logger.exception("[咨询问答智能体] 大模型生成回答异常详细信息: ")
            return "抱歉，我暂时无法为您提供该问题的回答。请稍后再试。"
    
    def _extract_keywords(self, text: str) -> str:
        """从文本中提取关键词
        
        Args:
            text: 输入文本
        
        Returns:
            str: 提取的关键词
        """
        # 这里是一个简单的关键词提取实现
        # 在实际应用中，可以使用NLP技术进行更精确的关键词提取
        try:
            logger.debug(f"[咨询问答智能体] 提取关键词 - 输入文本: '{text[:100]}...'" if len(text) > 100 else f"[咨询问答智能体] 提取关键词 - 输入文本: '{text}'")
            
            # 简单的关键词提取逻辑
            # 实际应用中可以使用更复杂的NLP技术
            import re
            # 移除停用词
            stop_words = ["的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一", "一个", "上", "也", "很", "到", "说", "要", "去", "你", "会", "着", "没有", "看", "好", "自己", "这"]
            words = re.findall(r'\b\w+\b', text)
            keywords = " ".join([word for word in words if word not in stop_words])
            
            logger.debug(f"[咨询问答智能体] 关键词提取完成 - 提取结果: '{keywords}'")
            return keywords
        except Exception as e:
            logger.error(f"[咨询问答智能体] 关键词提取时发生异常 - 错误类型: {type(e).__name__}, 错误消息: {str(e)}")
            return text