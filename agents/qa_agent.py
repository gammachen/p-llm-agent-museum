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
            enable_thinking=False,
            stream=True,
        )
        logger.info("[咨询问答智能体] 语言模型初始化完成 - 模型名称: qwen2:latest")
        
        # 初始化其他组件
        formatter = OllamaChatFormatter()
        memory = InMemoryMemory()
        name = "QAAgent"
        sys_prompt = "你是博物馆的咨询助手，负责回答关于博物馆的各种问题，包括开放时间、票价、交通、展览、藏品等信息。"
        
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
    
    async def reply(self, x: Any = None, **kwargs) -> Msg:
        """处理用户的咨询问题
        
        Args:
            x: 用户输入，可以是Msg对象或其他类型
            **kwargs: 其他参数
        
        Returns:
            Msg: 包含回答内容的消息对象
        """
        try:
            # 处理初始情况
            if x is None:
                logger.info("[咨询问答智能体] 收到初始请求，返回欢迎消息")
                return Msg(name=self.name, content="您好！我是博物馆的咨询助手，请问有什么可以帮助您的？", role="assistant")
            
            # 从输入中提取信息
            user_id = x.name if hasattr(x, 'name') else "anonymous"
            user_message = x.content if isinstance(x, Msg) else str(x)
            
            logger.info(f"[咨询问答智能体] 收到用户请求 - 用户ID: {user_id}, 请求内容: '{user_message[:100]}...'" if len(user_message) > 100 else f"[咨询问答智能体] 收到用户请求 - 用户ID: {user_id}, 请求内容: '{user_message}'")
            
            # 检查是否为常见问题
            for key, answer in self.common_answers.items():
                if key in user_message:
                    logger.info(f"[咨询问答智能体] 识别为常见问题 - 问题类型: {key}")
                    response = answer
                    break
            else:
                # 分析用户问题类型并调用相应功能
                if any(keyword in user_message for keyword in ["藏品", "文物", "艺术品", "展品"]):
                    logger.info("[咨询问答智能体] 识别为藏品相关查询")
                    response = await self._handle_collection_query(user_message)
                elif any(keyword in user_message for keyword in ["展览", "特展", "主题展"]):
                    logger.info("[咨询问答智能体] 识别为展览相关查询")
                    response = await self._handle_exhibition_query(user_message)
                else:
                    # 对于其他问题，使用大模型生成回答
                    logger.info("[咨询问答智能体] 识别为一般咨询问题，使用大模型生成回答")
                    response = await self._generate_answer(user_message)
            
            # 将结果添加到记忆中
            logger.debug("[咨询问答智能体] 更新记忆 - 添加用户请求和智能体响应")
            await self.memory.add(x)
            await self.memory.add(Msg(name=self.name, content=response, role="assistant"))
            
            # 返回响应
            logger.info(f"[咨询问答智能体] 请求处理完成 - 响应内容长度: {len(response)} 字符")
            return Msg(name=self.name, content=response, role="assistant")
        except Exception as e:
            logger.error(f"[咨询问答智能体] 处理请求时发生错误 - 错误类型: {type(e).__name__}, 错误消息: {str(e)}")
            logger.exception("[咨询问答智能体] 异常详细信息: ")
            # 返回错误响应
            return Msg(name=self.name, content="抱歉，处理您的请求时发生错误，请稍后再试。", role="assistant")
    
    async def _handle_collection_query(self, user_message: str) -> str:
        """处理关于藏品的查询"""
        # 模拟从用户消息中提取藏品关键词
        # 在实际应用中，这里可以使用NLP技术更精确地提取信息
        keywords = self._extract_keywords(user_message)
        if not keywords:
            return "请问您想了解哪件藏品的信息？您可以告诉我藏品的名称或关键词，我会为您查询。"
        
        # 调用服务搜索藏品信息
        tool_response = search_collection_info(keywords)
        result = tool_response.metadata
        
        if result.get("status") == "success":
            collections = result.get("data", [])
            if not collections:
                return f"未找到与'{keywords}'相关的藏品信息。"
            
            # 只返回第一个匹配的藏品信息
            collection = collections[0]
            return f"{collection.get('name', '')}\n" \
                   f"年代：{collection.get('era', '不详')}\n" \
                   f"来源：{collection.get('source', '不详')}\n" \
                   f"描述：{collection.get('description', '暂无详细描述')}"
        else:
            return f"查询失败：{result.get('message', '未知错误')}"
    
    async def _handle_exhibition_query(self, user_message: str) -> str:
        """处理关于展览的查询
        
        Args:
            user_message: 用户的查询消息
        
        Returns:
            str: 包含展览信息的响应字符串
        """
        try:
            logger.info(f"[咨询问答智能体] 开始处理展览查询 - 用户消息: '{user_message[:100]}...'" if len(user_message) > 100 else f"[咨询问答智能体] 开始处理展览查询 - 用户消息: '{user_message}'")
            
            # 从用户消息中提取关键词
            keywords = self._extract_keywords(user_message)
            logger.info(f"[咨询问答智能体] 提取关键词 - 关键词: '{keywords}'")
            
            # 根据关键词决定搜索方式
            if not keywords:
                # 如果没有关键词，获取所有展览信息
                logger.info("[咨询问答智能体] 未提取到关键词，获取所有展览信息")
                tool_response = execute_museum_service(endpoint="/api/public/qa/exhibitions/search")
                result = tool_response.metadata
            else:
                # 否则搜索特定展览信息
                logger.info(f"[咨询问答智能体] 使用关键词搜索展览 - 调用search_exhibition_info工具")
                tool_response = search_exhibition_info(keywords)
                result = tool_response.metadata
            
            logger.debug(f"[咨询问答智能体] 工具调用结果 - 状态: {result.get('status')}, 数据量: {len(result.get('data', [])) if result.get('status') == 'success' else 0}")
            
            # 处理搜索结果
            if result.get("status") == "success":
                exhibitions = result.get("data", [])
                logger.info(f"[咨询问答智能体] 展览搜索成功 - 找到 {len(exhibitions)} 个展览")
                
                if not exhibitions:
                    logger.info(f"[咨询问答智能体] 未找到展览 - 关键词: '{keywords}'")
                    return f"未找到与'{keywords}'相关的展览信息。"
                
                # 构建响应内容
                response = ""
                display_count = min(3, len(exhibitions))  # 只显示前3个展览
                logger.info(f"[咨询问答智能体] 准备响应内容 - 显示 {display_count} 个展览")
                
                for i, exhibition in enumerate(exhibitions[:display_count], 1):
                    exhibition_name = exhibition.get('name', '')
                    logger.debug(f"[咨询问答智能体] 处理展览信息 {i}/{display_count} - 展览名称: '{exhibition_name}'")
                    response += f"{exhibition_name}\n" \
                              f"时间：{exhibition.get('start_date', '不详')} 至 {exhibition.get('end_date', '不详')}\n" \
                              f"地点：{exhibition.get('location', '不详')}\n" \
                              f"简介：{exhibition.get('description', '暂无简介')}\n\n"
                
                logger.info(f"[咨询问答智能体] 展览查询处理完成 - 响应内容长度: {len(response.strip())} 字符")
                return response.strip()
            else:
                error_message = result.get('message', '未知错误')
                logger.error(f"[咨询问答智能体] 展览查询失败 - 错误消息: '{error_message}'")
                return f"查询失败：{error_message}"
        except Exception as e:
            logger.error(f"[咨询问答智能体] 处理展览查询时发生异常 - 错误类型: {type(e).__name__}, 错误消息: {str(e)}")
            logger.exception("[咨询问答智能体] 展览查询异常详细信息: ")
            return "抱歉，处理展览查询时发生错误，请稍后再试。"
    
    async def _generate_answer(self, user_message: str) -> str:
        """使用大模型生成回答"""
        content = [
            {"role": "system", "content": "你是博物馆的咨询助手，负责回答关于博物馆的各种问题，包括但不限于开放时间、票价、交通、展览、藏品等信息。"},
            {"role": "user", "content": user_message}
        ]
        
        # 使用模型生成回答
        model_input = await self.formatter.format(content)
        response = await self.model(model_input)
        model_output = await self.formatter.parse(response)
        
        return model_output.get("content", "抱歉，我暂时无法回答这个问题，请您稍后再试或联系博物馆工作人员。")
    
    def _extract_keywords(self, text: str) -> str:
        """从文本中提取关键词"""
        # 这里是一个简单的关键词提取示例
        # 在实际应用中，可以使用更复杂的NLP技术
        # 移除常见的疑问词和停用词
        stop_words = ["请问", "想了解", "关于", "的", "有", "什么", "哪些", "吗", "是", "了解"]
        for word in stop_words:
            text = text.replace(word, "")
        
        # 移除多余的空格
        text = " ".join(text.split()).strip()
        return text