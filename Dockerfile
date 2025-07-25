FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 拷贝项目文件
COPY server.py .
COPY config.yaml .

# 暴露端口
EXPOSE 8000

# 启动应用
CMD ["python", "server.py"]