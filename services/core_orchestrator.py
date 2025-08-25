from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import json

router = APIRouter(prefix="/api/core", tags=["Core Services"])

class RequestMessage(BaseModel):
    user_id: str
    message: str
    context: Optional[Dict[str, Any]] = None

# 简单的意图识别映射表
INTENT_MAPPING = {
    "预约": "tour_booking",
    "门票": "tour_booking",
    "路线": "tour_booking",
    "导览": "tour_booking",
    "问题": "qa",
    "展品": "qa",
    "历史": "qa",
    "艺术家": "qa",
    "寻人": "facility",
    "寻物": "facility",
    "位置": "facility",
    "餐厅": "facility",
    "投诉": "feedback",
    "建议": "feedback",
    "太热": "feedback",
    "太冷": "feedback",
    "藏品": "collection",
    "监控": "security",
    "设备": "facility_management",
    "审批": "administration",
    "报销": "administration",
    "请假": "administration",
    "数据": "analytics"
}

# 服务路由映射
SERVICE_ROUTING = {
    "tour_booking": "/api/public/tour-booking",
    "qa": "/api/public/qa",
    "facility": "/api/public/facility-services",
    "feedback": "/api/public/feedback",
    "collection": "/api/internal/collection",
    "security": "/api/internal/security",
    "facility_management": "/api/internal/facility",
    "administration": "/api/internal/administration",
    "analytics": "/api/internal/analytics"
}

# 为测试目的添加的重定向路径，处理简单路径调用
SIMPLE_PATH_REDIRECTS = {
    "/booking": "/api/public/tour-booking/bookings",
    "/hours": "/api/public/qa",
    "/collections": "/api/internal/collection/list"
}

@router.post("/orchestrate")
def orchestrate_request(request: RequestMessage) -> Dict[str, Any]:
    """核心协调服务，接收所有请求并路由给合适的专业服务"""
    # 简单的意图识别
    recognized_intent = "general"
    for keyword, intent in INTENT_MAPPING.items():
        if keyword in request.message:
            recognized_intent = intent
            break
    
    # 生成路由信息
    if recognized_intent in SERVICE_ROUTING:
        target_service = SERVICE_ROUTING[recognized_intent]
        
        # 在实际应用中，这里会将请求转发给对应的服务
        # 为了演示，我们只返回路由信息
        return {
            "status": "success",
            "intent": recognized_intent,
            "target_service": target_service,
            "message": request.message,
            "context": request.context,
            "next_steps": f"请调用 {target_service} 服务继续处理"
        }
    else:
        raise HTTPException(status_code=404, detail="未找到匹配的服务")

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