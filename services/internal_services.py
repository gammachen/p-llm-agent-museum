from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query
from utils.data_loader import load_collection_management, load_security_management, load_facility_management, load_administration

router = APIRouter(prefix="/api/internal", tags=["Internal Management"])

# 模型定义
class CollectionQuery(BaseModel):
    collection_id: Optional[str] = None
    name: Optional[str] = None
    category: Optional[str] = None
    period: Optional[str] = None

class EnvironmentAlert(BaseModel):
    location: str
    parameter: str
    value: float
    threshold: float
    status: str

class MaintenanceRequest(BaseModel):
    equipment_id: str
    location: str
    issue_description: str
    priority: str = "medium"

class ApprovalRequest(BaseModel):
    request_type: str
    requestor_id: str
    amount: Optional[float] = None
    reason: str
    attachments: Optional[List[str]] = None

# 藏品管理服务
@router.get("/collection/list")
def list_collections(
    name: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None)
):
    """列出藏品信息，支持筛选"""
    data = load_collection_management()
    collections = data.get("collections", [])
    
    # 应用筛选条件
    if name:
        collections = [c for c in collections if name in c["name"]]
    if category:
        collections = [c for c in collections if c["category"] == category]
    if status:
        collections = [c for c in collections if c["exhibition_status"] == status]
    
    return {"status": "success", "data": collections}

@router.get("/collection/detail/{collection_id}")
def get_collection_detail(collection_id: str):
    """获取单个藏品的详细信息"""
    data = load_collection_management()
    collections = data.get("collections", [])
    
    collection = next((c for c in collections if c["collection_id"] == collection_id), None)
    
    if collection:
        return {"status": "success", "data": collection}
    else:
        raise HTTPException(status_code=404, detail="未找到藏品信息")

@router.get("/collection/search")
def search_collection_info(
    keywords: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    period: Optional[str] = Query(None)
):
    """搜索藏品信息"""
    data = load_collection_management()
    collections = data.get("collections", [])
    
    # 应用搜索条件
    if keywords:
        keywords = keywords.lower()
        collections = [
            c for c in collections 
            if keywords in c["name"].lower() or 
               keywords in c["description"].lower() or 
               keywords in c["origin"].lower()
        ]
    if category:
        collections = [c for c in collections if c["category"] == category]
    if period:
        collections = [c for c in collections if period in c["period"]]
    
    return {"status": "success", "data": collections}

@router.get("/collection/environment")
def get_environment_monitoring():
    """获取藏品环境监测数据"""
    data = load_collection_management()
    environment_data = data.get("environment_monitoring", {})
    
    return {"status": "success", "data": environment_data}

@router.get("/collection/loans")
def get_loan_requests(status: Optional[str] = Query(None)):
    """获取借展申请记录"""
    data = load_collection_management()
    loan_requests = data.get("loan_requests", [])
    
    if status:
        loan_requests = [l for l in loan_requests if l["status"] == status]
    
    return {"status": "success", "data": loan_requests}

# 安保监控服务
@router.get("/security/camera-list")
def get_camera_list():
    """获取监控摄像头列表"""
    data = load_security_management()
    cameras = data.get("monitoring_system", {}).get("cameras", [])
    
    return {"status": "success", "data": cameras}

@router.get("/security/incidents")
def get_security_incidents(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    status: Optional[str] = Query(None)
):
    """获取安全事件记录"""
    data = load_security_management()
    incidents = data.get("monitoring_system", {}).get("incident_records", [])
    
    # 应用筛选条件
    if start_date:
        incidents = [i for i in incidents if i["timestamp"] >= start_date]
    if end_date:
        incidents = [i for i in incidents if i["timestamp"] <= end_date]
    if status:
        incidents = [i for i in incidents if i["status"] == status]
    
    return {"status": "success", "data": incidents}

@router.get("/security/emergency-plans")
def get_emergency_plans():
    """获取应急预案列表"""
    data = load_security_management()
    plans = data.get("emergency_response", {}).get("emergency_plans", [])
    
    return {"status": "success", "data": plans}

# 设施管理服务
@router.get("/facility/equipment")
def list_equipment(
    equipment_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None)
):
    """列出设施设备信息"""
    data = load_facility_management()
    equipment = data.get("equipment_management", {}).get("equipment", [])
    
    if equipment_type:
        equipment = [e for e in equipment if e["type"] == equipment_type]
    if status:
        equipment = [e for e in equipment if e["status"] == status]
    
    return {"status": "success", "data": equipment}

@router.post("/facility/maintenance-request")
def create_maintenance_request(request: MaintenanceRequest):
    """创建维修请求"""
    # 在实际应用中，这里会创建维修工单并通知维修人员
    new_request = {
        "request_id": f"MR{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "equipment_id": request.equipment_id,
        "location": request.location,
        "issue_description": request.issue_description,
        "priority": request.priority,
        "request_time": datetime.now().isoformat() + "Z",
        "status": "待处理"
    }
    
    return {"status": "success", "message": "维修请求已创建", "data": new_request}

@router.get("/facility/energy-consumption")
def get_energy_consumption(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    area: Optional[str] = Query(None)
):
    """获取能耗数据"""
    data = load_facility_management()
    energy_data = data.get("energy_management", {}).get("consumption_data", [])
    
    # 应用筛选条件
    if start_date:
        energy_data = [e for e in energy_data if e["date"] >= start_date]
    if end_date:
        energy_data = [e for e in energy_data if e["date"] <= end_date]
    if area:
        energy_data = [e for e in energy_data if e["area"] == area]
    
    return {"status": "success", "data": energy_data}

# 行政助理服务
@router.post("/administration/approval")
def submit_approval(request: ApprovalRequest):
    """提交审批申请"""
    # 在实际应用中，这里会创建审批流程并发送给相关负责人
    new_approval = {
        "approval_id": f"AP{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "request_type": request.request_type,
        "requestor_id": request.requestor_id,
        "amount": request.amount,
        "reason": request.reason,
        "attachments": request.attachments,
        "submit_time": datetime.now().isoformat() + "Z",
        "status": "待审批",
        "current_step": "部门经理审批"
    }
    
    return {"status": "success", "message": "审批申请已提交", "data": new_approval}

@router.get("/administration/meetings")
def get_meetings(date: Optional[str] = Query(None)):
    """获取会议记录"""
    data = load_administration()
    meetings = data.get("meeting_management", {}).get("meeting_records", [])
    
    if date:
        meetings = [m for m in meetings if m["date"] == date]
    
    return {"status": "success", "data": meetings}

@router.get("/administration/knowledge-base")
def search_knowledge_base(query: str):
    """搜索内部知识库"""
    data = load_administration()
    knowledge_base = data.get("internal_knowledge_base", {})
    
    # 合并所有知识库内容进行搜索
    all_articles = []
    all_articles.extend(knowledge_base.get("rules_regulations", []))
    all_articles.extend(knowledge_base.get("operating_procedures", []))
    all_articles.extend(knowledge_base.get("frequently_asked_questions", []))
    
    # 简单的关键词搜索
    results = [a for a in all_articles if query in a.get("title", "") or query in a.get("content", "")]
    
    return {"status": "success", "query": query, "results": results}

# 数据分析服务
@router.get("/analytics/visitor-stats")
def get_visitor_stats(
    start_date: str,
    end_date: str,
    granularity: Optional[str] = Query("daily", regex="^(daily|weekly|monthly)$")
):
    """获取游客统计数据"""
    # 模拟数据
    visitor_stats = [
        {"date": "2025-08-20", "visitors": 1250, "ticket_sales": 96500},
        {"date": "2025-08-21", "visitors": 1420, "ticket_sales": 108500},
        {"date": "2025-08-22", "visitors": 1890, "ticket_sales": 145800},
        {"date": "2025-08-23", "visitors": 2150, "ticket_sales": 165200},
        {"date": "2025-08-24", "visitors": 1980, "ticket_sales": 152300},
        {"date": "2025-08-25", "visitors": 1340, "ticket_sales": 103200},
        {"date": "2025-08-26", "visitors": 1120, "ticket_sales": 86500}
    ]
    
    # 筛选日期范围
    filtered_stats = [s for s in visitor_stats if start_date <= s["date"] <= end_date]
    
    return {"status": "success", "data": filtered_stats}

@router.get("/analytics/exhibition-popularity")
def get_exhibition_popularity():
    """获取展览 popularity 数据"""
    # 从信息数据中获取展览信息
    from utils.data_loader import load_pre_visit_information
    info_data = load_pre_visit_information()
    exhibitions = info_data.get("exhibitions", [])
    
    # 为每个展览添加模拟的 popularity 数据
    for i, exhibition in enumerate(exhibitions):
        exhibition["visitors_count"] = 5000 + i * 2000
        exhibition["average_stay_time"] = 45 + i * 10
        exhibition["satisfaction_rate"] = 0.92 - i * 0.03
    
    return {"status": "success", "data": exhibitions}