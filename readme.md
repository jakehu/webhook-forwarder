# Webhook Forwarder Server

这是一个轻量级的 Python Webhook 接收与转发服务器，支持通过配置文件将任意结构的 JSON 请求转发到其他服务。

为什么会有这个项目？

那是因为Emby的Webhook没法自定义，嗯，就是这样

---

## ✨ 功能特性

- ✅ 接收 JSON Webhook 数据（支持任意嵌套结构）
- ✅ 通过配置文件定义转发目标（支持 GET / POST）
- ✅ 支持自定义 HTTP 头部、Content-Type
- ✅ 支持请求体模板化（基于 Jinja2 语法，可插值变量）

---

## 🧱 示例接收数据（接口 A）

```json
{
  "Title": "Test Notification",
  "Description": "Test Notification Description",
  "Date": "2025-07-25T09:33:20.6594104Z",
  "Event": "system.webhooktest",
  "Severity": "Info",
  "User": {
    "Name": "jakehu",
    "Id": "jakehu"
  },
  "Server": {
    "Name": "JakehuNas",
    "Id": "JakehuNas",
    "Version": "4.9.1.10"
  }
}