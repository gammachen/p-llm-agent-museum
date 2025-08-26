import requests
import json
import os
from typing import Dict, Any, List, Optional
from utils.email_tool import send_email
import logging
from agentscope.tool import ToolResponse
import requests

logger = logging.getLogger(__name__)

class MuseumToolkit:
    """博物馆智能体工具集"""
    
    # 基础URL，指向我们的FastAPI服务
    BASE_URL = "http://localhost:8000"
    
    @staticmethod
    def call_service(endpoint: str, method: str = "GET", data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """调用博物馆服务API"""
        url = f"{MuseumToolkit.BASE_URL}{endpoint}"
        logger.info(f"开始调用服务: {url}, 方法: {method}, 数据: {data}")
        try:
            if method == "GET":
                response = requests.get(url, params=data)
            elif method == "POST":
                response = requests.post(url, json=data)
            else:
                raise ValueError(f"不支持的请求方法: {method}")
            
            response.raise_for_status()
            result = response.json()
            logger.info(f"服务调用成功: {url}, 响应状态码: {response.status_code}")
            return result
        except requests.exceptions.RequestException as e:
            logger.error(f"调用服务失败: {url}, 错误: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def send_email_notification(recipient: str, subject: str, content: str) -> Dict[str, str]:
        """发送邮件通知"""
        logger.info(f"开始发送邮件: 收件人={recipient}, 主题={subject}")
        try:
            send_email(recipient, subject, content)
            logger.info(f"邮件发送成功: 收件人={recipient}")
            return {"status": "success", "message": f"邮件已发送至 {recipient}"}
        except Exception as e:
            logger.error(f"发送邮件失败: 收件人={recipient}, 错误: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def get_booking_info(phone: Optional[str] = None) -> Dict[str, Any]:
        """获取预约信息"""
        logger.info(f"开始获取预约信息: 手机号={phone}")
        endpoint = "/api/public/tour-booking/bookings"
        params = {"phone": phone} if phone else {}
        result = MuseumToolkit.call_service(endpoint, method="GET", data=params)
        logger.info(f"获取预约信息完成: 手机号={phone}, 结果状态={result.get('status', 'success')}")
        return result
    
    @staticmethod
    def create_booking(booking_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建新的预约"""
        logger.info(f"开始创建预约: 预约数据={booking_data}")
        endpoint = "/api/public/tour-booking/create"
        result = MuseumToolkit.call_service(endpoint, method="POST", data=booking_data)
        logger.info(f"创建预约完成: 结果状态={result.get('status', 'success')}")
        return result
    
    @staticmethod
    def ask_question(question: str) -> Dict[str, Any]:
        """向咨询问答服务提问"""
        logger.info(f"开始向咨询问答服务提问: {question}")
        endpoint = "/api/public/qa"
        data = {"question": question}
        result = MuseumToolkit.call_service(endpoint, method="POST", data=data)
        logger.info(f"咨询问答服务返回: 结果状态={result.get('status', 'success')}")
        return result
    
    @staticmethod
    def submit_feedback(feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """提交游客反馈"""
        logger.info(f"开始提交游客反馈: {feedback_data}")
        endpoint = "/api/public/feedback"
        result = MuseumToolkit.call_service(endpoint, method="POST", data=feedback_data)
        logger.info(f"提交游客反馈完成: 结果状态={result.get('status', 'success')}")
        return result
    
    @staticmethod
    def get_collection_info(collection_id: Optional[str] = None) -> Dict[str, Any]:
        """获取藏品信息"""
        logger.info(f"开始获取藏品信息: 藏品ID={collection_id}")
        if collection_id:
            endpoint = f"/api/internal/collection/detail/{collection_id}"
        else:
            endpoint = "/api/internal/collection/list"
        result = MuseumToolkit.call_service(endpoint, method="GET")
        logger.info(f"获取藏品信息完成: 藏品ID={collection_id}, 结果状态={result.get('status', 'success')}")
        return result
    
    @staticmethod
    def create_maintenance_request(request_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建维修请求"""
        logger.info(f"开始创建维修请求: {request_data}")
        endpoint = "/api/internal/facility/maintenance-request"
        result = MuseumToolkit.call_service(endpoint, method="POST", data=request_data)
        logger.info(f"创建维修请求完成: 结果状态={result.get('status', 'success')}")
        return result
    
    @staticmethod
    def submit_approval(approval_data: Dict[str, Any]) -> Dict[str, Any]:
        """提交审批申请"""
        logger.info(f"开始提交审批申请: {approval_data}")
        endpoint = "/api/internal/administration/approval"
        result = MuseumToolkit.call_service(endpoint, method="POST", data=approval_data)
        logger.info(f"提交审批申请完成: 结果状态={result.get('status', 'success')}")
        return result
    
    @staticmethod
    def search_knowledge_base(query: str) -> Dict[str, Any]:
        """搜索内部知识库"""
        logger.info(f"开始搜索内部知识库: 查询={query}")
        endpoint = f"/api/internal/administration/knowledge-base?query={query}"
        result = MuseumToolkit.call_service(endpoint, method="GET")
        logger.info(f"搜索内部知识库完成: 查询={query}, 结果状态={result.get('status', 'success')}")
        return result
    
    @staticmethod
    def get_visitor_analytics(start_date: str, end_date: str) -> Dict[str, Any]:
        """获取游客统计数据"""
        logger.info(f"开始获取游客统计数据: 开始日期={start_date}, 结束日期={end_date}")
        endpoint = f"/api/internal/analytics/visitor-stats?start_date={start_date}&end_date={end_date}"
        result = MuseumToolkit.call_service(endpoint, method="GET")
        logger.info(f"获取游客统计数据完成: 结果状态={result.get('status', 'success')}")
        return result

    @staticmethod
    def specific_question_about_the_museum(endpoint: str) -> Dict[str, Any]:
        """获取关于展馆更加有针对性的信息，比如展馆是否服务、展馆紧急状态等，在其他服务能够支持的情况下，不建议使用此服务，但是可以通过传递Endpoint参数来获取非标准的内部服务信息，比如传递'endpoint=/'能够获取对应内部'/'路由的信息，该信息表示展馆的it service是online状态 """
        logger.info(f"开始获取关于展馆更加有针对性的信息: 端点={endpoint}")
        
        result = MuseumToolkit.call_service(endpoint, method="GET")
        logger.info(f"获取游客统计数据完成: 结果状态={result.get('status', 'success')}")
        return result
    
    @staticmethod
    def get_museum_staff() -> Dict[str, Any]:
        """获取博物馆公开人物信息"""
        logger.info(f"开始获取博物馆公开人物信息")
        endpoint = f"/qa/specific/museum/staff"
        result = MuseumToolkit.call_service(endpoint, method="GET")
        logger.info(f"获取博物馆公开人物信息: 结果状态={result.get('status', 'success')}")
        return result
    
    @staticmethod
    def get_museum_vendor() -> Dict[str, Any]:
        """获取博物馆公开供应商信息"""
        logger.info(f"开始获取博物馆公开供应商信息")
        endpoint = f"/qa/specific/museum/vendor"
        result = MuseumToolkit.call_service(endpoint, method="GET")
        logger.info(f"获取博物馆公开供应商信息: 结果状态={result.get('status', 'success')}")
        return result
    
    @staticmethod
    def get_museum_architecture() -> Dict[str, Any]:
        """获取博物馆公开建筑信息"""
        logger.info(f"开始获取博物馆公开建筑信息")
        endpoint = f"/qa/specific/museum/architecture"
        result = MuseumToolkit.call_service(endpoint, method="GET")
        logger.info(f"获取博物馆公开建筑信息: 结果状态={result.get('status', 'success')}")
        return result
    
    @staticmethod
    def get_museum_history() -> Dict[str, Any]:
        """获取博物馆公开历史信息"""
        logger.info(f"开始获取博物馆公开历史信息")
        endpoint = f"/qa/specific/museum/history"
        result = MuseumToolkit.call_service(endpoint, method="GET")
        logger.info(f"获取博物馆公开历史信息: 结果状态={result.get('status', 'success')}")
        return result

# 为agentscope工具注册准备的函数
def specific_question_about_the_museum(endpoint: str) -> ToolResponse:
    """获取关于展馆更加有针对性的信息的工具函数"""
    logger.info(f"工具函数调用 - specific_question_about_the_museum: 端点={endpoint}")
    result = MuseumToolkit.specific_question_about_the_museum(endpoint)
    content = [{"type": "text", "text": json.dumps(result)}]
    logger.info(f"工具函数完成 - specific_question_about_the_museum: 结果状态={result.get('status', 'success')}")
    return ToolResponse(content=content, metadata=result)

def get_museum_staff() -> ToolResponse:
    """获取博物馆公开人物信息的工具函数"""
    logger.info(f"工具函数调用 - get_museum_staff")
    result = MuseumToolkit.get_museum_staff()
    content = [{"type": "text", "text": json.dumps(result)}]
    logger.info(f"工具函数完成 - get_museum_staff: 结果状态={result.get('status', 'success')}")
    return ToolResponse(content=content, metadata=result)

def get_museum_vendor() -> ToolResponse:
    """获取博物馆公开供应商信息的工具函数"""
    logger.info(f"工具函数调用 - get_museum_vendor")
    result = MuseumToolkit.get_museum_vendor()
    content = [{"type": "text", "text": json.dumps(result)}]
    logger.info(f"工具函数完成 - get_museum_vendor: 结果状态={result.get('status', 'success')}")
    return ToolResponse(content=content, metadata=result)

def get_museum_architecture() -> ToolResponse:
    """获取博物馆公开建筑信息的工具函数"""
    logger.info(f"工具函数调用 - get_museum_architecture")
    result = MuseumToolkit.get_museum_architecture()
    content = [{"type": "text", "text": json.dumps(result)}]
    logger.info(f"工具函数完成 - get_museum_architecture: 结果状态={result.get('status', 'success')}")
    return ToolResponse(content=content, metadata=result)

def get_museum_history() -> ToolResponse:
    """获取博物馆公开历史信息的工具函数"""
    logger.info(f"工具函数调用 - get_museum_history")
    result = MuseumToolkit.get_museum_history()
    content = [{"type": "text", "text": json.dumps(result)}]
    logger.info(f"工具函数完成 - get_museum_history: 结果状态={result.get('status', 'success')}")
    return ToolResponse(content=content, metadata=result)

def send_museum_email(recipient: str, subject: str, content: str) -> ToolResponse:
    """发送博物馆邮件通知的工具函数"""
    logger.info(f"工具函数调用 - send_museum_email: 收件人={recipient}, 主题={subject}")
    result = MuseumToolkit.send_email_notification(recipient, subject, content)
    content = [{"type": "text", "text": json.dumps(result)}]
    logger.info(f"工具函数完成 - send_museum_email: 结果状态={result.get('status', 'success')}")
    return ToolResponse(content=content, metadata=result)

def get_museum_booking_info(phone: Optional[str] = None) -> ToolResponse:
    """获取博物馆预约信息的工具函数"""
    logger.info(f"工具函数调用 - get_museum_booking_info: 手机号={phone}")
    result = MuseumToolkit.get_booking_info(phone)
    content = [{"type": "text", "text": json.dumps(result)}]
    logger.info(f"工具函数完成 - get_museum_booking_info: 结果状态={result.get('status', 'success')}")
    return ToolResponse(content=content, metadata=result)

def create_museum_booking(booking_data: Dict[str, Any]) -> ToolResponse:
    """创建博物馆预约的工具函数"""
    logger.info(f"工具函数调用 - create_museum_booking: 预约数据={booking_data}")
    result = MuseumToolkit.create_booking(booking_data)
    content = [{"type": "text", "text": json.dumps(result)}]
    logger.info(f"工具函数完成 - create_museum_booking: 结果状态={result.get('status', 'success')}")
    return ToolResponse(content=content, metadata=result)

def general_question_about_the_museum(question: str) -> ToolResponse:
    """向博物馆咨询问答服务提问的工具函数(关于展馆的通用问题都可以咨询)"""
    logger.info(f"工具函数调用 - ask_museum_question: {question}")
    result = MuseumToolkit.ask_question(question)
    content = [{"type": "text", "text": json.dumps(result)}]
    logger.info(f"工具函数完成 - ask_museum_question: 结果状态={result.get('status', 'success')}")
    return ToolResponse(content=content, metadata=result)

def submit_museum_feedback(feedback_data: Dict[str, Any]) -> ToolResponse:
    """提交博物馆游客反馈的工具函数"""
    logger.info(f"工具函数调用 - submit_museum_feedback: {feedback_data}")
    result = MuseumToolkit.submit_feedback(feedback_data)
    content = [{"type": "text", "text": json.dumps(result)}]
    logger.info(f"工具函数完成 - submit_museum_feedback: 结果状态={result.get('status', 'success')}")
    return ToolResponse(content=content, metadata=result)

def search_collection_info(keywords: str) -> ToolResponse:
    """搜索博物馆藏品信息的工具函数"""
    logger.info(f"工具函数调用 - search_collection_info: 关键词={keywords}")
    endpoint = f"/api/internal/collection/search?keywords={keywords}"
    result = MuseumToolkit.call_service(endpoint, method="GET")
    content = [{"type": "text", "text": json.dumps(result)}]
    logger.info(f"工具函数完成 - search_collection_info: 结果状态={result.get('status', 'success')}")
    return ToolResponse(content=content, metadata=result)

def search_exhibition_info(keywords: str) -> ToolResponse:
    """搜索博物馆展览信息的工具函数"""
    logger.info(f"工具函数调用 - search_exhibition_info: 关键词={keywords}")
    endpoint = f"/api/public/qa/exhibitions/search?keywords={keywords}"
    result = MuseumToolkit.call_service(endpoint, method="GET")
    content = [{"type": "text", "text": json.dumps(result)}]
    logger.info(f"工具函数完成 - search_exhibition_info: 结果状态={result.get('status', 'success')}")
    return ToolResponse(content=content, metadata=result)

def get_collection_environment_data(location: str) -> ToolResponse:
    """获取藏品环境监测数据的工具函数"""
    logger.info(f"工具函数调用 - get_collection_environment_data: 位置={location}")
    endpoint = f"/api/internal/collection/environment?location={location}"
    result = MuseumToolkit.call_service(endpoint, method="GET")
    content = [{"type": "text", "text": json.dumps(result)}]
    logger.info(f"工具函数完成 - get_collection_environment_data: 结果状态={result.get('status', 'success')}")
    return ToolResponse(content=content, metadata=result)

def create_exhibition_loan_request(loan_data: Dict[str, Any]) -> ToolResponse:
    """创建借展申请的工具函数"""
    logger.info(f"工具函数调用 - create_exhibition_loan_request: 借展数据={loan_data}")
    endpoint = "/api/internal/collection/loan-request"
    result = MuseumToolkit.call_service(endpoint, method="POST", data=loan_data)
    content = [{"type": "text", "text": json.dumps(result)}]
    logger.info(f"工具函数完成 - create_exhibition_loan_request: 结果状态={result.get('status', 'success')}")
    return ToolResponse(content=content, metadata=result)

# 在MuseumToolkit类中添加对应的静态方法
def _add_missing_methods_to_toolkit():
    """为MuseumToolkit类添加缺失的静态方法"""
    logger.info("开始为MuseumToolkit类添加缺失的静态方法")
    
    @staticmethod
    def search_collection(keywords: str) -> Dict[str, Any]:
        """搜索藏品信息"""
        logger.info(f"开始搜索藏品信息: 关键词={keywords}")
        endpoint = f"/api/internal/collection/search?keywords={keywords}"
        result = MuseumToolkit.call_service(endpoint, method="GET")
        logger.info(f"搜索藏品信息完成: 关键词={keywords}, 结果状态={result.get('status', 'success')}")
        return result
    
    @staticmethod
    def search_exhibition(keywords: str) -> Dict[str, Any]:
        """搜索展览信息"""
        logger.info(f"开始搜索展览信息: 关键词={keywords}")
        endpoint = f"/api/public/qa/exhibitions/search?keywords={keywords}"
        result = MuseumToolkit.call_service(endpoint, method="GET")
        logger.info(f"搜索展览信息完成: 关键词={keywords}, 结果状态={result.get('status', 'success')}")
        return result
    
    @staticmethod
    def get_environment_data(location: str) -> Dict[str, Any]:
        """获取环境监测数据"""
        logger.info(f"开始获取环境监测数据: 位置={location}")
        endpoint = f"/api/internal/collection/environment?location={location}"
        result = MuseumToolkit.call_service(endpoint, method="GET")
        logger.info(f"获取环境监测数据完成: 位置={location}, 结果状态={result.get('status', 'success')}")
        return result
    
    @staticmethod
    def create_loan_request(loan_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建借展申请"""
        logger.info(f"开始创建借展申请: {loan_data}")
        endpoint = "/api/internal/collection/loan-request"
        result = MuseumToolkit.call_service(endpoint, method="POST", data=loan_data)
        logger.info(f"创建借展申请完成: 结果状态={result.get('status', 'success')}")
        return result
    
    logger.info("为MuseumToolkit类添加缺失的静态方法完成")

# 执行函数以添加缺失的方法
_add_missing_methods_to_toolkit()