import json
import logging
import requests
import yaml
from flask import Flask, jsonify, request
from jinja2 import Template, StrictUndefined

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# 加载配置文件，确保是 UTF-8 编码
with open("config.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)


@app.route("/api/receive", methods=["POST"])
def receive_data():
    try:
        incoming_data = request.json or {}

        # 获取配置 key，默认是 webhook
        config_key = request.args.get("config_key", "webhook")
        if config_key not in config:
            return jsonify({"error": f"Config key '{config_key}' not found"}), 400

        selected_config = config[config_key]

        logging.info(f"Using config: {config_key}")
        logging.info(f"Received data: {incoming_data}")

        # 构造模板上下文
        context = flatten(incoming_data)
        logging.info(f"Flattened context: {context}")

        # 渲染 body 模板
        body_template = Template(selected_config["body"], undefined=StrictUndefined)
        rendered_body = body_template.render(**context)

        # 请求参数
        method = selected_config["method"].upper()
        url = selected_config["url"]
        headers = selected_config.get("headers", {})

        # 发送请求
        if method == "POST":
            content_type = headers.get("Content-Type", "").lower()

            if "application/json" in content_type:
                try:
                    json_body = json.loads(rendered_body)
                    response = requests.post(url, json=json_body, headers=headers)
                except json.JSONDecodeError:
                    response = requests.post(
                        url, data=rendered_body.encode("utf-8"), headers=headers
                    )
            else:
                response = requests.post(
                    url, data=rendered_body.encode("utf-8"), headers=headers
                )

        elif method == "GET":
            response = requests.get(url, headers=headers, params=incoming_data)
        else:
            return jsonify({"error": f"Unsupported method {method}"}), 400

        logging.info(f"Forwarded to {url}, status: {response.status_code}")
        return jsonify({"status": "ok", "forward_status": response.status_code})

    except Exception as e:
        logging.exception("Error processing request")
        return jsonify({"error": str(e)}), 500


def flatten(d, parent_key="", sep="."):
    """
    将嵌套的 dict 展平成一个 dict，并保留原始字段。
    用于 Jinja2 模板渲染，支持 updateKind['localValue'] 和 updateKind.localValue。
    """
    items = {}
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, dict):
            items[k] = v  # 保留原始嵌套字段
            items.update(flatten(v, new_key, sep=sep))  # 添加扁平字段
        else:
            items[new_key] = v  # 扁平路径字段
            items[k] = v        # 保留顶层字段
    return items


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)