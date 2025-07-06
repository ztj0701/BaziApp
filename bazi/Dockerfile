# Dockerfile for the Flask application

# 1. 使用官方的 Python 3.9 slim 版本作为基础镜像
FROM python:3.9-slim

# 2. 设置工作目录
WORKDIR /app

# 3. 复制依赖文件并安装 (利用 Docker 缓存)
# 使用 -i 参数指定清华大学的 PyPI 镜像源，解决国内网络访问慢或失败的问题。
COPY requirements.txt .
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install --no-cache-dir -r requirements.txt

# 4. 复制所有应用源代码到工作目录
COPY . .

# 5. 暴露 Gunicorn 运行的端口
EXPOSE 5000

# 6. 定义容器启动时要执行的命令
CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:5000", "app:app"]

