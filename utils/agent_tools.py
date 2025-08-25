import requests
import json
import os
from typing import Dict, Any, List, Optional
from utils.email_tool import send_email
import logging

logger = logging.getLogger(__name__)

class MuseumToolkit:
    """博物馆智能体工具集"""
    
    # 基础URL，指向我们的FastAPI服务
    BASE_URL = "http://localhost:8000"
    
    @staticmethod
    def call_service(endpoint: str, method: str = "GET", data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """调用博物馆服务API"""
        url = f"{MuseumToolkit.BASE_URL}{endpoint}"
        try:
            if method == "GET":
                response = requests.get(url, params=data)
            elif method == "POST":
                response = requests.post(url, json=data)
            else:
                raise ValueError(f"不支持的请求方法: {method}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"调用服务失败: {url}, 错误: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def send_email_notification(recipient: str, subject: str, content: str) -> Dict[str, str]:
        """发送邮件通知"""
        try:
            send_email(recipient, subject, content)
            return {"status": "success", "message": f"邮件已发送至 {recipient}"}
        except Exception as e:
            logger.error(f"发送邮件失败: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def get_booking_info(phone: Optional[str] = None) -> Dict[str, Any]:
        """获取预约信息"""
        endpoint = "/api/public/tour-booking/bookings"
        params = {"phone": phone} if phone else {}
        return MuseumToolkit.call_service(endpoint, method="GET", data=params)
    
    @staticmethod
    def create_booking(booking_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建新的预约"""
        endpoint = "/api/public/tour-booking/create"
        return MuseumToolkit.call_service(endpoint, method="POST", data=booking_data)
    
    @staticmethod
    def ask_question(question: str) -> Dict[str, Any]:
        """向咨询问答服务提问"""
        endpoint = "/api/public/qa"
        data = {"question": question}
        return MuseumToolkit.call_service(endpoint, method="POST", data=data)
    
    @staticmethod
    def submit_feedback(feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """提交游客反馈"""
        endpoint = "/api/public/feedback"
        return MuseumToolkit.call_service(endpoint, method="POST", data=feedback_data)
    
    @staticmethod
    def get_collection_info(collection_id: Optional[str] = None) -> Dict[str, Any]:
        """获取藏品信息"""
        if collection_id:
            endpoint = f"/api/internal/collection/detail/{collection_id}"
        else:
            endpoint = "/api/internal/collection/list"
        return MuseumToolkit.call_service(endpoint, method="GET")
    
    @staticmethod
    def create_maintenance_request(request_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建维修请求"""
        endpoint = "/api/internal/facility/maintenance-request"
        return MuseumToolkit.call_service(endpoint, method="POST", data=request_data)
    
    @staticmethod
    def submit_approval(approval_data: Dict[str, Any]) -> Dict[str, Any]:
        """提交审批申请"""
        endpoint = "/api/internal/administration/approval"
        return MuseumToolkit.call_service(endpoint, method="POST", data=approval_data)
    
    @staticmethod
    def search_knowledge_base(query: str) -> Dict[str, Any]:
        """搜索内部知识库"""
        endpoint = f"/api/internal/administration/knowledge-base?query={query}"
        return MuseumToolkit.call_service(endpoint, method="GET")
    
    @staticmethod
    def get_visitor_analytics(start_date: str, end_date: str) -> Dict[str, Any]:
        """获取游客统计数据"""
        endpoint = f"/api/internal/analytics/visitor-stats?start_date={start_date}&end_date={end_date}"
        return MuseumToolkit.call_service(endpoint, method="GET")

# 为agentscope工具注册准备的函数
def execute_museum_service(endpoint: str, method: str = "GET", data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """执行博物馆服务API调用的工具函数"""
    return MuseumToolkit.call_service(endpoint, method, data)

def send_museum_email(recipient: str, subject: str, content: str) -> Dict[str, str]:
    """发送博物馆邮件通知的工具函数"""
    return MuseumToolkit.send_email_notification(recipient, subject, content)

def get_museum_booking_info(phone: Optional[str] = None) -> Dict[str, Any]:
    """获取博物馆预约信息的工具函数"""
    return MuseumToolkit.get_booking_info(phone)

def create_museum_booking(booking_data: Dict[str, Any]) -> Dict[str, Any]:
    """创建博物馆预约的工具函数"""
    return MuseumToolkit.create_booking(booking_data)

def ask_museum_question(question: str) -> Dict[str, Any]:
    """向博物馆咨询问答服务提问的工具函数"""
    return MuseumToolkit.ask_question(question)

def submit_museum_feedback(feedback_data: Dict[str, Any]) -> Dict[str, Any]:
    """提交博物馆游客反馈的工具函数"""
    return MuseumToolkit.submit_feedback(feedback_data)

def search_collection_info(keywords: str) -> Dict[str, Any]:
    """搜索博物馆藏品信息的工具函数"""
    endpoint = f"/api/internal/collection/search?keywords={keywords}"
    return MuseumToolkit.call_service(endpoint, method="GET")

def search_exhibition_info(keywords: str) -> Dict[str, Any]:
    """搜索博物馆展览信息的工具函数"""
    endpoint = f"/api/public/qa/exhibitions/search?keywords={keywords}"
    return MuseumToolkit.call_service(endpoint, method="GET")

def get_collection_environment_data(location: str) -> Dict[str, Any]:
    """获取藏品环境监测数据的工具函数"""
    endpoint = f"/api/internal/collection/environment?location={location}"
    return MuseumToolkit.call_service(endpoint, method="GET")

def create_exhibition_loan_request(loan_data: Dict[str, Any]) -> Dict[str, Any]:
    """创建借展申请的工具函数"""
    endpoint = "/api/internal/collection/loan-request"
    return MuseumToolkit.call_service(endpoint, method="POST", data=loan_data)

# 在MuseumToolkit类中添加对应的静态方法
def _add_missing_methods_to_toolkit():
    """为MuseumToolkit类添加缺失的静态方法"""
    
    @staticmethod
    def search_collection(keywords: str) -> Dict[str, Any]:
        """搜索藏品信息"""
        endpoint = f"/api/internal/collection/search?keywords={keywords}"
        return MuseumToolkit.call_service(endpoint, method="GET")
    
    @staticmethod
    def search_exhibition(keywords: str) -> Dict[str, Any]:
        """搜索展览信息"""
        endpoint = f"/api/public/qa/exhibitions/search?keywords={keywords}"
        return MuseumToolkit.call_service(endpoint, method="GET")
    
    @staticmethod
    def get_environment_data(location: str) -> Dict[str, Any]:
        """获取环境监测数据"""
        endpoint = f"/api/internal/collection/environment?location={location}"
        return MuseumToolkit.call_service(endpoint, method="GET")
    
    @staticmethod
    def create_loan_request(loan_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建借展申请"""
        endpoint = "/api/internal/collection/loan-request"
        return MuseumToolkit.call_service(endpoint, method="POST", data=loan_data)

# 执行函数以添加缺失的方法
_add_missing_methods_to_toolkit()