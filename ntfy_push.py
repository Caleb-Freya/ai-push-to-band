#!/usr/bin/env python3
"""安卓版：把一句话推到手机上的 ntfy App，再由「小米运动健康」转发到手环。

用法：
    python3 ntfy_push.py "标题" "正文"
    echo "正文" | python3 ntfy_push.py "标题"

主题名读取顺序：环境变量 NTFY_TOPIC → 同目录 ntfy.conf 第一行。
主题名相当于密码：谁知道它谁就能收到你的消息，起一个长的随机名字。
只用标准库，Python 3.8+。
"""
import json
import os
import sys
import urllib.request

SERVER = os.environ.get("NTFY_SERVER", "https://ntfy.sh").rstrip("/")
MAX_BODY = int(os.environ.get("NTFY_MAX", "60"))   # 手环屏幕小，建议 60 字以内


def load_topic():
    topic = os.environ.get("NTFY_TOPIC", "").strip()
    if not topic:
        conf = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ntfy.conf")
        try:
            with open(conf, encoding="utf-8") as f:
                topic = f.readline().strip()
        except OSError:
            pass
    if not topic:
        sys.exit("没找到主题名：设置环境变量 NTFY_TOPIC，或在脚本同目录建 ntfy.conf 写一行主题名")
    return topic


def push(title, body):
    body = " ".join(body.split())
    if len(body) > MAX_BODY:
        body = body[:MAX_BODY - 1] + "…"
    # 用 JSON 发，中文标题不会乱码（放请求头里会）
    data = json.dumps({"topic": load_topic(), "title": title, "message": body}).encode()
    req = urllib.request.Request(SERVER, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return r.status


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    title = sys.argv[1]
    body = sys.argv[2] if len(sys.argv) > 2 else sys.stdin.read()
    if not body.strip():
        sys.exit("正文是空的")
    print("已发送" if push(title, body) == 200 else "发送失败")
