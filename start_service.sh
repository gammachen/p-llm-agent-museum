#!/bin/bash

# 安装依赖
echo "正在安装依赖..."
pip install -r requirements.txt

# 启动服务
echo "正在启动博物馆服务API..."
uvicorn main:app --reload --host 0.0.0.0 --port 8000