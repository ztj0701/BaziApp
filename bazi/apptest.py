# app.py: the api for coze
from flask import Flask, request, jsonify
app = Flask(__name__)

# 假设您的本地程序是一个函数
def your_local_function(input_data):
    # 这里替换为您的实际代码
    # 例如：计算两个数的和
    a = input_data.get('a', 0)
    b = input_data.get('b', 0)
    return a + b  # 返回结


@app.route('/api/bazi', methods=['POST'])  # 定义一个端点，供远程调用
def calculate():
    data = request.get_json()  # 从请求中获取数据
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    result = your_local_function(data)  # 调用您的本地函数
    return jsonify({"result": result})  # 返回 JSON 响应
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)  # 运行服务器
