import json
import logging

import requests
import yaml
from flask import Flask, jsonify, request
from jinja2 import Template

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
            content_type = headers.get("Content-Type", "").lower()

            if "application/json" in content_type:
                try:
                    # 渲染后的 body 是 JSON 字符串，解析后作为 JSON 发送
                    json_body = json.loads(rendered_body)
                    response = requests.post(url, json=json_body, headers=headers)
                except json.JSONDecodeError:
                    # fallback：如果不是合法 JSON，使用 UTF-8 编码发送原文
                    response = requests.post(
                        url, data=rendered_body.encode("utf-8"), headers=headers
                    )
            else:
                # 非 JSON 类型，直接发送 UTF-8 编码的数据
                response = requests.post(
                    url, data=rendered_body.encode("utf-8"), headers=headers
                )

        elif method == "GET":
            # GET 请求通常通过 URL 参数，不存在编码问题
            response = requests.get(url, headers=headers, params=incoming_data)
        else:
            return jsonify({"error": f"Unsupported method {method}"}), 400
        logging.info(f"Forwarded to {url}, status: {response.status_code}")
        return jsonify({"status": "ok", "forward_status": response.status_code})

    except Exception as e:
        logging.exception("Error processing request")
        return jsonify({"error": str(e)}), 500


def flatten(d, parent_key="", sep="."):
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
