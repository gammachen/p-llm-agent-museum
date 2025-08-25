import asyncio
import sys
from typing import Dict, Any
from agents.orchestrator_agent import OrchestratorAgent
from agents.tour_booking_agent import TourBookingAgent
from agents.qa_agent import QAAgent
from agents.collection_management_agent import CollectionManagementAgent
from agentscope.message import Msg
from utils.agent_tools import execute_museum_service

class MuseumAgentSystem:
    """博物馆智能体系统集成测试"""
    
    def __init__(self):
        # 初始化各个智能体
        self.orchestrator = OrchestratorAgent()
        self.tour_booking_agent = TourBookingAgent()
        self.qa_agent = QAAgent()
        self.collection_management_agent = CollectionManagementAgent()
        
        # 启动博物馆服务（如果尚未启动）
        print("正在检查博物馆服务状态...")
        self._check_service_status()
    
    def _check_service_status(self):
        """检查博物馆服务是否正常运行"""
        try:
            # 尝试调用一个简单的API来检查服务状态
            result = execute_museum_service(endpoint="/")
            if result.get("status") == "success":
                print("博物馆服务已成功启动！")
            else:
                print("警告：博物馆服务可能未正常启动。请确保已运行 './start_service.sh'")
        except Exception as e:
            print(f"错误：无法连接到博物馆服务。请先运行 './start_service.sh'\n错误信息: {str(e)}")
    
    async def test_orchestrator_agent(self):
        """测试核心协调智能体"""
        print("\n=== 测试核心协调智能体 ===")
        
        # 测试用例
        test_cases = [
            "我想预约明天的参观",
            "博物馆的开放时间是什么时候？",
            "查询藏品信息"
        ]
        
        for i, test_case in enumerate(test_cases):
            print(f"\n测试用例 {i+1}: {test_case}")
            user_msg = Msg(name="user", content=test_case)
            response = await self.orchestrator.reply(user_msg)
            print(f"OrchestratorAgent 响应: {response.content}")
    
    async def test_tour_booking_agent(self):
        """测试导览与预约智能体"""
        print("\n=== 测试导览与预约智能体 ===")
        
        # 测试用例
        test_cases = [
            "我想预约8月26日的参观",
            "查询我的预约记录",
            "生成一个参观路线",
            "有哪些可用的预约时段？"
        ]
        
        for i, test_case in enumerate(test_cases):
            print(f"\n测试用例 {i+1}: {test_case}")
            user_msg = Msg(name="user", content=test_case)
            response = await self.tour_booking_agent.reply(user_msg)
            print(f"TourBookingAgent 响应: {response.content}")
    
    async def test_qa_agent(self):
        """测试咨询问答智能体"""
        print("\n=== 测试咨询问答智能体 ===")
        
        # 测试用例
        test_cases = [
            "博物馆的开放时间是什么时候？",
            "票价是多少？",
            "介绍一下青铜鼎这件藏品",
            "当前有哪些展览？"
        ]
        
        for i, test_case in enumerate(test_cases):
            print(f"\n测试用例 {i+1}: {test_case}")
            user_msg = Msg(name="user", content=test_case)
            response = await self.qa_agent.reply(user_msg)
            print(f"QAAgent 响应: {response.content}")
    
    async def test_collection_management_agent(self):
        """测试藏品管理智能体"""
        print("\n=== 测试藏品管理智能体 ===")
        
        # 测试用例
        test_cases = [
            "获取藏品列表",
            "获取COL001的藏品详情",
            "查询一层展厅的环境监测数据",
            "搜索青铜相关的藏品"
        ]
        
        for i, test_case in enumerate(test_cases):
            print(f"\n测试用例 {i+1}: {test_case}")
            user_msg = Msg(name="user", content=test_case)
            response = await self.collection_management_agent.reply(user_msg)
            print(f"CollectionManagementAgent 响应: {response.content}")
    
    async def interactive_demo(self):
        """交互式演示"""
        print("\n=== 博物馆智能体系统交互式演示 ===")
        print("输入'quit'退出演示\n")
        
        while True:
            user_input = input("您: ")
            if user_input.lower() == 'quit':
                print("谢谢使用，再见！")
                break
            
            # 创建用户消息
            user_msg = Msg(name="user", content=user_input)
            
            # 发送给OrchestratorAgent
            response = await self.orchestrator.reply(user_msg)
            print(f"智能助手: {response.content}")
    
    async def run_all_tests(self):
        """运行所有测试"""
        await self.test_orchestrator_agent()
        await self.test_tour_booking_agent()
        await self.test_qa_agent()
        await self.test_collection_management_agent()
        
        # 最后运行交互式演示
        await self.interactive_demo()

async def main():
    """主函数"""
    # 显示欢迎信息
    print("""
    ============================================================
    博物馆智能体系统测试工具
    ============================================================
    此工具用于测试基于AgentScope构建的博物馆智能体系统。
    系统包含以下智能体：
    1. OrchestratorAgent - 核心协调智能体
    2. TourBookingAgent - 导览与预约智能体
    3. QAAgent - 咨询问答智能体
    4. CollectionManagementAgent - 藏品管理智能体
    
    注意：请确保已启动博物馆服务（运行 './start_service.sh'）
    并且本地Ollama服务正常运行，已加载qwen2模型。
    ============================================================
    """)
    
    # 创建测试系统
    test_system = MuseumAgentSystem()
    
    # 运行所有测试
    await test_system.run_all_tests()

if __name__ == "__main__":
    # 检查Python版本
    if sys.version_info[0] < 3 or (sys.version_info[0] == 3 and sys.version_info[1] < 7):
        print("错误：此程序需要Python 3.7或更高版本。")
        sys.exit(1)
    
    # 检查是否在Windows环境下运行
    if sys.platform == 'win32':
        # Windows下需要设置策略以允许嵌套的事件循环
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    # 运行主函数
    asyncio.run(main())