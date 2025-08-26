from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import os
from fastapi import APIRouter, HTTPException, Query
from utils.data_loader import load_pre_visit_booking, load_pre_visit_information, load_on_visit_services, load_post_visit_services, load_public_info

router = APIRouter(prefix="/api/public", tags=["Public Services"])

# 模型定义
class BookingCreate(BaseModel):
    visitor_name: str
    visitor_phone: str
    visit_date: str  # YYYY-MM-DD
    visit_time: str
    ticket_type: str
    ticket_count: int

class FeedbackCreate(BaseModel):
    visitor_id: str
    content: str
    rating: Optional[int] = None
    location: Optional[str] = None

class QARequest(BaseModel):
    question: str
    context: Optional[Dict[str, Any]] = None

# 导览与预约服务
@router.get("/tour-booking/bookings")
def get_bookings(phone: Optional[str] = Query(None)):
    """获取预约记录，可以通过手机号筛选"""
    data = load_pre_visit_booking()
    bookings = data.get("bookings", [])
    
    if phone:
        bookings = [b for b in bookings if b["visitor_phone"] == phone]
    
    return {"status": "success", "data": bookings}

@router.post("/tour-booking/create")
def create_booking(booking: BookingCreate):
    """创建新的预约"""
    # 在实际应用中，这里会更新数据库
    # 为了演示，我们只返回创建成功的信息
    new_booking = {
        "booking_id": f"BK{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "visitor_name": booking.visitor_name,
        "visitor_phone": booking.visitor_phone,
        "visit_date": booking.visit_date,
        "visit_time": booking.visit_time,
        "ticket_type": booking.ticket_type,
        "ticket_count": booking.ticket_count,
        "status": "已预约",
        "created_at": datetime.now().isoformat() + "Z"
    }
    
    return {"status": "success", "message": "预约创建成功", "data": new_booking}

@router.get("/tour-booking/available-slots")
def get_available_slots(date: Optional[str] = Query(None)):
    """获取可用的预约时段"""
    data = load_pre_visit_booking()
    slots = data.get("available_slots", [])
    
    if date:
        slots = [s for s in slots if s["date"] == date]
    
    return {"status": "success", "data": slots}

# 咨询问答服务
@router.post("/qa")
def ask_question(qa_request: QARequest):
    """回答游客关于展馆（开放时间等）、展品、历史等的问题"""
    # 在实际应用中，这里会调用知识库或LLM来生成回答
    # 为了演示，我们根据关键词返回预设的回答
    question = qa_request.question.lower()
    
    # 从信息数据中获取一些展品信息
    info_data = load_pre_visit_information()
    exhibitions = info_data.get("exhibitions", [])
    
    # 简单的关键词匹配回答
    if "青铜鼎" in question:
        answer = "青铜鼎是商代晚期的代表性作品，纹饰精美，铸造工艺精湛，是我国现已发现的最重的青铜器。"
    elif "木乃伊" in question or "埃及" in question:
        answer = "古埃及木乃伊是古埃及第18王朝法老图坦卡蒙的遗体，距今已有3000多年历史。"
    elif "开放" in question or "时间" in question:
        answer = "博物馆开放时间为周二至周日9:00-17:00（16:30停止入场），周一闭馆（法定节假日除外）。"
    elif "门票" in question:
        answer = "成人票80元，学生票40元，65岁以上老人、军人、残疾人凭有效证件免费参观。"
    else:
        answer = "感谢您的提问！我们正在为您查询相关信息，稍后将给您更详细的回复。"
    
    return {"status": "success", "question": qa_request.question, "answer": answer}

@router.get("/qa/specific/museum/staff")
def get_museum_staff():
    """获取博物馆公开公众人物信息"""
    # 从信息数据中获取公众人物信息
    info_data = load_public_info()
    staff = info_data.get("staff", [])
    
    return {"status": "success", "data": staff}

@router.get("/qa/specific/museum/vendors")
def get_museum_vendors():
    """获取博物馆公开公众人物信息"""
    # 从信息数据中获取公众人物信息
    info_data = load_public_info()
    vendors = info_data.get("vendors", [])
    
    return {"status": "success", "data": vendors}

@router.get("/qa/specific/museum/architecture")
def get_museum_architecture():
    """获取博物馆公开架构信息"""
    # 从信息数据中获取公众人物信息
    info_data = load_public_info()
    architecture = info_data.get("architecture", [])
    
    return {"status": "success", "data": architecture}

@router.get("/qa/specific/museum/history")
def get_museum_history():
    """获取博物馆公开历史信息"""
    # 从信息数据中获取公众人物信息
    info_data = load_public_info()
    history = info_data.get("history", [])
    
    return {"status": "success", "data": history}

@router.get("/qa/exhibitions/search")
def search_exhibitions(
    keywords: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None)
):
    """搜索展览信息"""
    info_data = load_pre_visit_information()
    exhibitions = info_data.get("exhibitions", [])
    
    # 应用搜索条件
    if keywords:
        keywords = keywords.lower()
        exhibitions = [
            e for e in exhibitions 
            if keywords in e["title"].lower() or 
               keywords in e["description"].lower() or 
               keywords in e["subtitle"].lower()
        ]
    if status:
        exhibitions = [e for e in exhibitions if e["status"] == status]
    if start_date:
        exhibitions = [e for e in exhibitions if e["start_date"] >= start_date]
    
    return {"status": "success", "data": exhibitions}

# 便民服务
@router.get("/facility-services/locations")
def get_locations(type: Optional[str] = Query(None)):
    """获取设施位置信息"""
    # 模拟数据
    locations = [
        {"type": "洗手间", "floor": "1F", "location": "展厅A东侧"},
        {"type": "母婴室", "floor": "2F", "location": "展厅B北侧"},
        {"type": "餐厅", "floor": "1F", "location": "入口大厅西侧"},
        {"type": "纪念品商店", "floor": "1F", "location": "出口处"}
    ]
    
    if type:
        locations = [l for l in locations if l["type"] == type]
    
    return {"status": "success", "data": locations}

@router.get("/facility-services/lost-found")
def get_lost_found():
    """获取失物招领信息"""
    # 从服务中数据获取失物招领信息
    on_visit_data = load_on_visit_services()
    lost_found = on_visit_data.get("facility_services", {}).get("lost_found", [])
    
    return {"status": "success", "data": lost_found}

# 反馈处理服务
@router.post("/feedback")
def submit_feedback(feedback: FeedbackCreate):
    """提交游客反馈"""
    # 在实际应用中，这里会将反馈存储并进行情感分析
    # 为了演示，我们只返回提交成功的信息
    new_feedback = {
        "feedback_id": f"FB{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "visitor_id": feedback.visitor_id,
        "content": feedback.content,
        "rating": feedback.rating,
        "location": feedback.location,
        "submitted_at": datetime.now().isoformat() + "Z",
        "status": "已接收"
    }
    
    # 简单的情感分析
    negative_words = ["太热", "太冷", "脏", "差", "不好", "不满意", "糟糕"]
    is_negative = any(word in feedback.content for word in negative_words)
    
    if is_negative:
        return {"status": "success", "message": "感谢您的反馈，我们会尽快处理您的问题", "data": new_feedback, "priority": "high"}
    else:
        return {"status": "success", "message": "感谢您的反馈", "data": new_feedback, "priority": "normal"}

# 游客服务后 - 会员与社区
@router.get("/post-visit/membership")
def get_membership_info(visitor_id: str):
    """获取会员信息"""
    post_visit_data = load_post_visit_services()
    membership = post_visit_data.get("membership", [])
    
    # 查找特定游客的会员信息
    member_info = next((m for m in membership if m["visitor_id"] == visitor_id), None)
    
    if member_info:
        return {"status": "success", "data": member_info}
    else:
        raise HTTPException(status_code=404, detail="未找到会员信息")

@router.get("/post-visit/analytics")
def get_visit_analytics(visitor_id: str):
    """获取参观分析数据"""
    post_visit_data = load_post_visit_services()
    analytics = post_visit_data.get("visit_analytics", {})
    
    # 在实际应用中，这里会根据游客ID查询具体的分析数据
    # 为了演示，我们返回一些通用的分析信息
    return {"status": "success", "data": {
        "visitor_id": visitor_id,
        "total_visits": analytics.get("total_visits", 0),
        "favorite_exhibitions": analytics.get("favorite_exhibitions", []),
        "recommended_exhibitions": analytics.get("recommended_exhibitions", [])
    }}