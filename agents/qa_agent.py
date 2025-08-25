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

class QAAgent(ReActAgent):
    """博物馆咨询问答智能体"""
    
    def __init__(self):
        # 初始化工具集
        toolkit = Toolkit()
        toolkit.register_tool_function(execute_museum_service)
        toolkit.register_tool_function(search_collection_info)
        toolkit.register_tool_function(search_exhibition_info)
        
        model = OllamaChatModel(
            model_name="qwen2:latest",
            enable_thinking=False,
            stream=True,
        )
        
        formatter = OllamaChatFormatter()
        memory = InMemoryMemory()
        name = "QAAgent"
        sys_prompt = "你是博物馆的咨询助手，负责回答关于博物馆的各种问题，包括开放时间、票价、交通、展览、藏品等信息。"
        
        # 调用父类的初始化方法
        super().__init__(name=name, sys_prompt=sys_prompt, model=model, formatter=formatter, toolkit=toolkit, memory=memory)
        
        # 常见问题的预设答案
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
        """处理用户的咨询问题"""
        if x is None:
            return Msg(name=self.name, content="您好！我是博物馆的咨询助手，请问有什么可以帮助您的？", role="assistant")
        
        # 从输入中提取信息
        user_message = x.content if isinstance(x, Msg) else str(x)
        
        # 检查是否为常见问题
        for key, answer in self.common_answers.items():
            if key in user_message:
                response = answer
                break
        else:
            # 分析用户问题类型并调用相应功能
            if any(keyword in user_message for keyword in ["藏品", "文物", "艺术品", "展品"]):
                response = await self._handle_collection_query(user_message)
            elif any(keyword in user_message for keyword in ["展览", "特展", "主题展"]):
                response = await self._handle_exhibition_query(user_message)
            else:
                # 对于其他问题，使用大模型生成回答
                response = await self._generate_answer(user_message)
        
        # 将结果添加到记忆中
        await self.memory.add(x)
        await self.memory.add(Msg(name=self.name, content=response, role="assistant"))
        
        # 返回响应
        return Msg(name=self.name, content=response, role="assistant")
    
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
        """处理关于展览的查询"""
        # 模拟从用户消息中提取展览关键词
        # 在实际应用中，这里可以使用NLP技术更精确地提取信息
        keywords = self._extract_keywords(user_message)
        if not keywords:
            # 如果没有关键词，获取所有展览信息
            tool_response = execute_museum_service(endpoint="/api/public/qa/exhibitions")
            result = tool_response.metadata
        else:
            # 否则搜索特定展览信息
            tool_response = search_exhibition_info(keywords)
            result = tool_response.metadata
        
        if result.get("status") == "success":
            exhibitions = result.get("data", [])
            if not exhibitions:
                return f"未找到与'{keywords}'相关的展览信息。"
            
            response = ""
            for exhibition in exhibitions[:3]:  # 只显示前3个展览
                response += f"{exhibition.get('name', '')}\n" \
                          f"时间：{exhibition.get('start_date', '不详')} 至 {exhibition.get('end_date', '不详')}\n" \
                          f"地点：{exhibition.get('location', '不详')}\n" \
                          f"简介：{exhibition.get('description', '暂无简介')}\n\n"
            return response.strip()
        else:
            return f"查询失败：{result.get('message', '未知错误')}"
    
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