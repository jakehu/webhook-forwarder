from flask import Flask, request, jsonify
import yaml
import requests
from jinja2 import Template
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# 加载配置
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

@app.route("/api/receive", methods=["POST"])
def receive_data():
    try:
        incoming_data = request.json
        logging.info(f"Received data: {incoming_data}")

        # 构造请求体
        body_template = Template(config["webhook"]["body"])
        rendered_body = body_template.render(**incoming_data)

        # 请求参数
        method = config["webhook"]["method"].upper()
        url = config["webhook"]["url"]
        headers = config["webhook"].get("headers", {})

        # 发送请求
        if method == "POST":
            response = requests.post(url, data=rendered_body, headers=headers)
        elif method == "GET":
            response = requests.get(url, headers=headers, params=incoming_data)
        else:
            return jsonify({"error": f"Unsupported method {method}"}), 400

        logging.info(f"Forwarded to {url}, status: {response.status_code}")
        return jsonify({"status": "ok", "forward_status": response.status_code})
    except Exception as e:
        logging.exception("Error processing request")
        return jsonify({"error": str(e)}), 500

def flatten(d, parent_key='', sep='.'):
    """将嵌套的 dict 展平成一个 dict，用于 Jinja2 模板渲染"""
    items = {}
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, dict):
            items.update(flatten(v, new_key, sep=sep))
        else:
            items[new_key] = v
            items[k] = v  # 兼容顶层字段
    return items

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)