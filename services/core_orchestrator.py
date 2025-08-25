from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import json
import re
import logging
from fastapi import APIRouter, HTTPException
import httpx

# 导入核心协调智能体
from agents.orchestrator_agent import OrchestratorAgent

# 创建全局的核心协调智能体实例
orchestrator_agent = OrchestratorAgent()

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/core", tags=["Core Services"])

class RequestMessage(BaseModel):
    user_id: str
    message: str
    context: Optional[Dict[str, Any]] = None
    history: Optional[List[Dict[str, str]]] = None

# 增强的意图识别映射表 - 按照重要性分组
INTENT_MAPPING = {
    # 高优先级意图（更具体的关键词）
    "tour_booking": [
        "预约参观", "预订门票", "预约导览", "购买门票", "团体预约", 
        "特别活动预约"
    ],
    # 中优先级意图
    "qa": [
        "展览介绍", "藏品信息", "历史背景", "艺术家介绍", "作品解析", 
        "博物馆历史", "开放时间", "闭馆信息", "节假日安排", "常见问题",
        "门票价格", "参观时间", "参观指南", "青铜鼎", "木乃伊", "埃及"
    ],
    "facility": [
        "洗手间位置", "餐厅位置", "无障碍设施", "寄存服务", "停车场信息", 
        "电梯位置", "休息区", "商店位置", "轮椅借用", "导览设备"
    ],
    # 普通优先级意图
    "feedback": [
        "投诉建议", "服务评价", "体验反馈", "意见提交", "问题反映", 
        "环境问题", "温度不适", "噪音问题", "清洁问题"
    ],
    "collection": [
        "藏品管理", "藏品查询", "文物详情", "展品搜索", "藏品数据", 
        "文物保护", "藏品修复", "展品借展", "馆藏信息"
    ],
    "security": [
        "安保监控", "安全检查", "紧急情况", "丢失物品", "人员走失", 
        "安全事件", "消防设施", "应急预案"
    ],
    "facility_management": [
        "设备维护", "设施管理", "维修请求", "设备故障", "系统维护", 
        "环境监测", "能源管理", "设备更新"
    ],
    "administration": [
        "审批流程", "报销申请", "请假申请", "工作报告", "会议安排", 
        "文档管理", "人事管理", "财务管理"
    ],
    "analytics": [
        "数据分析", "参观统计", "客流分析", "展览效果", "运营数据", 
        "用户行为", "收入统计", "成本分析"
    ]
}

# 服务路由映射 - 包含更详细的子路径
SERVICE_ROUTING = {
    "tour_booking": "/api/public/tour-booking",
    "qa": "/api/public/qa",
    "facility": "/api/public/facility-services",
    "feedback": "/api/public/feedback",
    "collection": "/api/internal/collection",
    "security": "/api/internal/security",
    "facility_management": "/api/internal/facility",
    "administration": "/api/internal/administration",
    "analytics": "/api/internal/analytics",
    "general": "/api/public/qa"  # general意图默认路由到QA服务
}

# 子意图映射 - 用于更精细的路由
SUB_INTENT_MAPPING = {
    # 预约相关子意图
    "booking_info": ["查询预约", "预约状态", "我的预约", "取消预约"],
    "new_booking": ["新预约", "创建预约", "预约门票", "预约导览"],
    "booking_modify": ["修改预约", "更改时间", "调整预约"],
    # 藏品相关子意图
    "collection_detail": ["藏品详情", "展品介绍", "文物信息"],
    "collection_search": ["搜索藏品", "查找展品", "查询文物"],
    # QA相关子意图
    "exhibition_info": ["展览信息", "当前展览", "特别展览"],
    "museum_info": ["博物馆信息", "开放时间", "门票价格", "参观指南"]
}

# 为测试目的添加的重定向路径，处理简单路径调用
SIMPLE_PATH_REDIRECTS = {
    "/booking": "/api/public/tour-booking/bookings",
    "/hours": "/api/public/qa",
    "/collections": "/api/internal/collection/list",
    "/search/collections": "/api/internal/collection/search"
}

# 简化的内部请求函数，用于向其他服务发送请求
async def send_request(service_url: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """发送请求到指定服务并返回结果"""
    try:
        # 使用 httpx 发送 HTTP POST 请求到指定服务
        async with httpx.AsyncClient() as client:
            # 构建完整的 URL（假设服务运行在 localhost:8001）
            full_url = f"http://localhost:8000{service_url}"
            
            # 发送 POST 请求并等待响应
            response = await client.post(full_url, json=params)
            
            # 检查响应状态码
            if response.status_code == 200:
                # 尝试解析 JSON 响应
                try:
                    return {
                        "status": "success",
                        "data": response.json()
                    }
                except json.JSONDecodeError:
                    return {
                        "status": "success",
                        "data": {
                            "message": "请求成功，但无法解析响应内容",
                            "raw_content": response.text
                        }
                    }
            else:
                # 处理非 200 状态码的响应
                logger.error(f"服务 {service_url} 返回非成功状态码: {response.status_code}")
                return {
                    "status": "error",
                    "code": response.status_code,
                    "message": f"服务请求失败: {response.reason_phrase}"
                }
    except httpx.RequestError as e:
        logger.error(f"发送请求到服务 {service_url} 网络错误: {str(e)}")
        return {
            "status": "error",
            "code": 503,
            "message": f"服务不可用: {str(e)}"
        }
    except Exception as e:
        logger.error(f"发送请求到服务 {service_url} 未知错误: {str(e)}")
        return {
            "status": "error",
            "code": 500,
            "message": f"服务调用失败: {str(e)}"
        }

def recognize_intent(message: str, history: Optional[List[Dict[str, str]]] = None) -> str:
    """增强的意图识别函数"""
    # 转换为小写进行匹配
    message_lower = message.lower()
    
    # 记录匹配的意图和得分
    intent_scores = {}
    
    # 1. 基于关键词的意图匹配
    for intent, keywords in INTENT_MAPPING.items():
        score = 0
        for keyword in keywords:
            if keyword.lower() in message_lower:
                # 关键词越长，权重越高
                score += len(keyword) / len(message_lower)
        
        if score > 0:
            intent_scores[intent] = score
    
    # 2. 基于正则表达式的特殊模式匹配
    # 例如，识别藏品ID格式
    if re.search(r"col\d+", message_lower):
        intent_scores["collection"] = intent_scores.get("collection", 0) + 0.5
    
    # 3. 基于上下文的意图推断（如果有历史记录）
    if history:
        recent_intents = []
        for i, h in enumerate(reversed(history[-3:])):  # 考虑最近3条历史记录
            # 简单的假设：如果用户之前询问过某个服务，可能会继续相关问题
            for intent, keywords in INTENT_MAPPING.items():
                for keyword in keywords:
                    if keyword.lower() in h.get("content", "").lower():
                        # 越近的历史记录权重越高
                        intent_scores[intent] = intent_scores.get(intent, 0) + 0.2 / (i + 1)
                        break
    
    # 选择得分最高的意图
    if intent_scores:
        return max(intent_scores, key=intent_scores.get)
    
    # 如果没有匹配到任何意图，返回通用意图
    return "general"

def recognize_sub_intent(message: str, main_intent: str) -> Optional[str]:
    """识别子意图"""
    message_lower = message.lower()
    
    # 根据主意图确定可能的子意图范围
    relevant_sub_intents = {
        "tour_booking": ["booking_info", "new_booking", "booking_modify"],
        "collection": ["collection_detail", "collection_search"],
        "qa": ["exhibition_info", "museum_info"]
    }
    
    # 获取与主意图相关的子意图
    possible_sub_intents = relevant_sub_intents.get(main_intent, [])
    
    # 匹配子意图
    for sub_intent in possible_sub_intents:
        for keyword in SUB_INTENT_MAPPING.get(sub_intent, []):
            if keyword.lower() in message_lower:
                return sub_intent
    
    return None

@router.post("/orchestrate")
async def orchestrate_request(request: RequestMessage) -> Dict[str, Any]:
    """处理协调请求，调用核心协调智能体进行内部agent调度"""
    try:
        # 1. 记录接收到的请求
        logger.info(f"收到请求: user_id={request.user_id}, message={request.message[:100]}...")
        
        # 2. 构建请求数据，传递给核心协调智能体
        request_data = {
            "user_id": request.user_id,
            "message": request.message,
            "context": request.context,
            "history": request.history
        }
        
        # 3. 调用核心协调智能体处理请求
        logger.info(f"调用核心协调智能体处理请求")
        agent_response = await orchestrator_agent.process_request(request_data)
        
        # 4. 处理核心协调智能体返回的结果
        if agent_response.get("status") == "success":
            # 成功响应
            logger.info(f"核心协调智能体处理成功，返回结果")
            return {
                "status": "success",
                "data": {
                    "orchestration_result": agent_response.get("result", {}),
                    "agent_info": agent_response.get("agent_info", {})
                }
            }
        else:
            # 处理智能体返回的错误
            error_code = agent_response.get("code", 500)
            error_message = agent_response.get("message", "核心协调智能体处理失败")
            logger.error(f"核心协调智能体返回错误: {error_code}, {error_message}")
            
            # 提供默认回退内容
            return {
                "status": "error",
                "code": error_code,
                "message": error_message,
                "data": {
                    "fallback_response": True,
                    "content": "感谢您的提问。我们正在处理您的请求，请稍候。"
                }
            }
    except Exception as e:
        logger.error(f"调用核心协调智能体时发生错误: {str(e)}")
        # 避免直接向用户暴露内部错误信息
        return {
            "status": "error",
            "code": 500,
            "message": "处理您的请求时发生错误，请稍后再试。",
            "data": {
                "fallback_response": True,
                "content": "感谢您的提问。我们暂时无法处理您的请求，请稍后再试。"
            }
        }

@router.get("/services")
def list_services():
    """列出所有可用的服务"""
    return {
        "public_services": [
            {"name": "导览与预约服务", "endpoint": SERVICE_ROUTING["tour_booking"]},
            {"name": "咨询问答服务", "endpoint": SERVICE_ROUTING["qa"]},
            {"name": "便民服务", "endpoint": SERVICE_ROUTING["facility"]},
            {"name": "反馈处理服务", "endpoint": SERVICE_ROUTING["feedback"]}
        ],
        "internal_services": [
            {"name": "藏品管理服务", "endpoint": SERVICE_ROUTING["collection"]},
            {"name": "安保监控服务", "endpoint": SERVICE_ROUTING["security"]},
            {"name": "设施管理服务", "endpoint": SERVICE_ROUTING["facility_management"]},
            {"name": "行政助理服务", "endpoint": SERVICE_ROUTING["administration"]},
            {"name": "数据分析服务", "endpoint": SERVICE_ROUTING["analytics"]}
        ]
    }