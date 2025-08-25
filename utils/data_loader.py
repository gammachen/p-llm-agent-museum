import json
import os

class DataLoader:
    """数据加载器，用于读取模拟数据文件"""
    
    @staticmethod
    def load_data(file_path: str) -> dict:
        """加载指定路径的JSON数据文件"""
        try:
            # 获取当前文件所在目录的绝对路径
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # 构建完整的文件路径
            full_path = os.path.join(current_dir, "..", file_path)
            
            with open(full_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.info(f"数据文件不存在: {full_path}")
            return {}
        except json.JSONDecodeError:
            logger.info(f"数据文件格式错误: {full_path}")
            return {}

# 为了方便各服务使用，创建一些常用的加载方法
def load_pre_visit_booking() -> dict:
    """加载游客服务前的预约数据"""
    return DataLoader.load_data("public_services/pre_visit_booking.json")

def load_pre_visit_information() -> dict:
    """加载游客服务前的信息发布数据"""
    return DataLoader.load_data("public_services/pre_visit_information.json")

def load_on_visit_services() -> dict:
    """加载游客服务中的服务数据"""
    return DataLoader.load_data("public_services/on_visit_services.json")

def load_post_visit_services() -> dict:
    """加载游客服务后的服务数据"""
    return DataLoader.load_data("public_services/post_visit_services.json")

def load_collection_management() -> dict:
    """加载藏品管理数据"""
    return DataLoader.load_data("internal_management/collection_management.json")

def load_security_management() -> dict:
    """加载安保管理数据"""
    return DataLoader.load_data("internal_management/security_management.json")

def load_facility_management() -> dict:
    """加载设施管理数据"""
    return DataLoader.load_data("internal_management/facility_management.json")

def load_administration() -> dict:
    """加载行政人事数据"""
    return DataLoader.load_data("internal_management/administration.json")