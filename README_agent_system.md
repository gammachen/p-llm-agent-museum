# 博物馆智能体系统

## 系统概述

博物馆智能体系统是基于AgentScope框架构建的多智能体协作系统，旨在为博物馆提供智能化的服务和管理支持。系统通过多个专业智能体协同工作，处理游客咨询、门票预约、藏品管理等多种场景的需求。

## 系统架构

系统采用分层架构设计，主要包含以下组件：

1. **核心协调层**：由OrchestratorAgent负责，根据用户请求的意图，将任务分发给相应的专业智能体。
2. **专业智能体层**：包含多个专注于不同领域的智能体，如导览预约、咨询问答、藏品管理等。
3. **服务集成层**：通过API调用已构建的博物馆服务，获取或更新数据。
4. **工具支持层**：提供邮件发送、服务调用等通用工具。

## 智能体列表

### 1. OrchestratorAgent（核心协调智能体）
- **功能**：接收用户请求，识别意图，路由到相应的专业智能体。
- **位置**：`agents/orchestrator_agent.py`
- **主要方法**：
  - `reply()`：处理用户请求并返回响应。
  - `register_agent()`：注册新的智能体。
  - `_route_request()`：根据意图路由请求。

### 2. TourBookingAgent（导览与预约智能体）
- **功能**：处理门票预约、团队预约、生成参观路线等。
- **位置**：`agents/tour_booking_agent.py`
- **主要方法**：
  - `_handle_booking()`：处理预约请求。
  - `_generate_route()`：生成个性化参观路线。
  - `_query_booking()`：查询预约信息。
  - `_get_available_slots()`：获取可用预约时段。

### 3. QAAgent（咨询问答智能体）
- **功能**：回答关于博物馆藏品、展览、开放时间、票价政策等常见问题。
- **位置**：`agents/qa_agent.py`
- **主要方法**：
  - `_handle_collection_query()`：处理藏品相关查询。
  - `_handle_exhibition_query()`：处理展览相关查询。
  - `_generate_answer()`：使用大模型生成回答。

### 4. CollectionManagementAgent（藏品管理智能体）
- **功能**：处理藏品列表查询、详情获取、环境监测数据查询和借展申请处理等。
- **位置**：`agents/collection_management_agent.py`
- **主要方法**：
  - `_get_collection_list()`：获取藏品列表。
  - `_get_collection_detail()`：获取藏品详情。
  - `_get_environment_data()`：获取环境监测数据。
  - `_handle_loan_request()`：处理借展申请。
  - `_search_collection()`：搜索藏品。

## 工具支持

系统提供了以下工具支持智能体的功能实现：

### 1. 邮件发送工具
- **功能**：通过SMTP发送邮件通知。
- **位置**：`utils/email_tool.py`
- **使用方法**：调用`send_email()`函数发送邮件。

### 2. 智能体工具集
- **功能**：为智能体提供服务调用、数据查询等通用功能。
- **位置**：`utils/agent_tools.py`
- **主要工具**：
  - `execute_museum_service()`：调用博物馆服务API。
  - `send_museum_email()`：发送博物馆相关邮件。
  - `get_museum_booking_info()`：获取预约信息。
  - `create_museum_booking()`：创建预约。
  - `search_collection_info()`：搜索藏品信息。
  - `get_collection_environment_data()`：获取藏品环境监测数据。
  - `create_exhibition_loan_request()`：创建借展申请。
  - `search_exhibition_info()`：搜索展览信息。

## 环境配置

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置Ollama服务

系统使用本地Ollama服务运行大模型，请确保：

- 已安装Ollama服务
- 已下载qwen2模型
- Ollama服务正在运行

### 3. 配置邮件服务

邮件发送功能需要配置环境变量，请创建`.env`文件，添加以下内容：

```
EMAIL_USERNAME=your_email@example.com
EMAIL_PASSWORD=your_email_password
```

## 启动服务

### 1. 启动博物馆服务

```bash
./start_service.sh
```

此脚本会安装依赖并启动FastAPI服务。

### 2. 运行智能体测试

```bash
python test_museum_agents.py
```

此脚本会测试所有智能体的功能，并提供交互式演示。

## 使用示例

以下是使用博物馆智能体系统的简单示例：

```python
import asyncio
from agents.orchestrator_agent import OrchestratorAgent
from agentscope.message import Msg

async def main():
    # 初始化OrchestratorAgent
    orchestrator = OrchestratorAgent()
    
    # 创建用户消息
    user_msg = Msg(name="user", content="我想预约明天的参观")
    
    # 获取智能体响应
    response = await orchestrator.reply(user_msg)
    
    # 打印响应
    print(f"智能助手: {response.content}")

if __name__ == "__main__":
    asyncio.run(main())
```

## 系统集成

### 1. 与FastAPI服务集成

智能体系统通过API调用与FastAPI服务集成，主要集成点包括：

- 预约服务：`/api/public/tour-booking/`
- 咨询服务：`/api/public/qa/`
- 藏品管理服务：`/api/internal/collection/`

### 2. 与外部系统集成

- 邮件服务：通过SMTP协议发送邮件通知
- Ollama服务：调用本地Ollama大模型进行意图识别和自然语言生成

## 注意事项

1. 请确保在运行智能体系统前，已启动博物馆服务和Ollama服务。
2. 系统使用的是模拟数据，实际应用中需要连接到真实的数据库。
3. 邮件发送功能需要正确配置SMTP服务和账户信息。
4. 对于生产环境，请确保所有API调用都进行了适当的身份验证和授权。

## 未来优化方向

1. 增强意图识别的准确性，支持更复杂的用户请求。
2. 增加更多专业智能体，覆盖博物馆运营的更多场景。
3. 优化智能体间的协作机制，实现更复杂的任务处理流程。
4. 集成真实的数据库和外部服务，提供更准确的数据支持。
5. 添加监控和日志系统，方便问题排查和性能优化。