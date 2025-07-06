# app.py
# 这个文件用于启动 Flask 服务，并将 bazi.py 包装成 API。

import io
import contextlib
import re
from flask import Flask, request, jsonify

# --- 1. 导入我们刚刚修改好的 bazi_api.py 中的主函数 ---
try:
    # 请确保 bazi_api.py (修改版) 和这个 app.py 文件在同一个目录下。
    from bazi_api import bazi_main
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保 bazi_api.py 以及其依赖的 datas.py, sizi.py, common.py, yue.py 都在当前目录。")
    # 定义一个备用函数以防程序在导入失败时崩溃
    def bazi_main(*args, **kwargs):
        print("请检查：")
        print("1. 项目根目录中是否存在 bazi_api.py 文件？")
        print("2. bazi_api.py 文件中是否定义了 bazi_main 函数？")
        print("3. 是否所有依赖文件 (datas.py, sizi.py 等) 都被正确复制到了 Docker 镜像中？")

# 初始化 Flask 应用
app = Flask(__name__)
# 设置这个选项可以确保返回的 JSON 中，中文字符能正常显示而不是被转义成 Unicode。
app.config['JSON_AS_ASCII'] = False

def strip_ansi_codes(text):
    """用于移除 colorama 输出的 ANSI 颜色代码的函数"""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

@app.route('/api/bazi', methods=['GET', 'POST'])
def bazi_api():
    """
    八字计算的 API 接口。
    它接收参数，调用 bazi_main 函数，捕获其所有 print 输出，并以 JSON 格式返回。
    """
    # --- 2. 获取输入参数 ---
    # 为了方便测试，同时支持 GET 的查询参数和 POST 的 JSON body。
    if request.method == 'POST':
        data = request.json
        if not data:
            return jsonify({"error": "POST 请求需要提供 JSON 格式的数据"}), 400
    else: # GET
        data = request.args

    try:
        # 从请求数据中提取必要的参数
        year = int(data.get('year'))
        month = int(data.get('month'))
        day = int(data.get('day'))
        time = int(data.get('time'))
        # 获取布尔值参数
        is_gregorian = data.get('is_gregorian', 'true').lower() in ('true', '1', 't')
        is_female = data.get('is_female', 'false').lower() in ('true', '1', 't')
        is_leap = data.get('is_leap', 'false').lower() in ('true', '1', 't')

    except (TypeError, ValueError, AttributeError):
        return jsonify({
            "error": "参数缺失或格式不正确。请确保提供了 'year', 'month', 'day', 'time' 并且它们都是数字。"
        }), 400

    # --- 3. 捕获 print 输出的核心逻辑 ---
    output_buffer = io.StringIO()
    try:
        # 使用 contextlib.redirect_stdout 将所有 print 输出重定向到 buffer
        with contextlib.redirect_stdout(output_buffer):
            bazi_main(
                year=year,
                month=month,
                day=day,
                time=time,
                is_gregorian=is_gregorian,
                is_leap=is_leap,
                is_female=is_female
            )
        
        # 从 buffer 中获取所有被捕获的输出内容
        raw_output = output_buffer.getvalue()
        
        # 移除颜色代码，让返回的文本更干净
        clean_output = strip_ansi_codes(raw_output)

        # --- 4. 格式化并返回结果 ---
        return jsonify({
            "code": 0,
            "message": "success",
            "data": {
                "raw_output": clean_output.strip()
            }
        })

    except Exception as e:
        app.logger.error(f"执行 bazi_main 时发生错误: {e}")
        return jsonify({"error": f"服务器内部错误: {str(e)}"}), 500

# Gunicorn 部署时会使用这个 'app' 对象
if __name__ == '__main__':
    # 本地测试时，可以通过 `python app.py` 来启动一个测试服务器
    app.run(host='0.0.0.0', port=5000, debug=True)

