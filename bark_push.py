#!/usr/bin/env python3
"""把一句话推到 iPhone 的 Bark App，再由「小米运动健康」转发到手环。

用法：
    python3 bark_push.py "标题" "正文"
    echo "正文" | python3 bark_push.py "标题"

key 读取顺序：环境变量 BARK_KEY → 同目录 bark.conf 第一行。
只用标准库，Python 3.8+。
"""
import os
import sys
import urllib.parse
import urllib.request

SERVER = os.environ.get("BARK_SERVER", "https://api.day.app").rstrip("/")
MAX_BODY = int(os.environ.get("BARK_MAX", "60"))   # 手环屏幕小，太长会被截，建议 60 字以内
GROUP = os.environ.get("BARK_GROUP", "AI")          # 通知分组名，手机通知中心里会归在一起


def load_key():
    key = os.environ.get("BARK_KEY", "").strip()
    if not key:
        conf = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bark.conf")
        try:
            with open(conf, encoding="utf-8") as f:
                key = f.readline().strip()
        except OSError:
            pass
    if not key:
        sys.exit("没找到 Bark key：设置环境变量 BARK_KEY，或在脚本同目录建 bark.conf 写一行 key")
    return key


def push(title, body):
    body = " ".join(body.split())                     # 去掉换行，手环上更好看
    if len(body) > MAX_BODY:
        body = body[:MAX_BODY - 1] + "…"
    q = lambda s: urllib.parse.quote(s, safe="")      # 中文、空格、斜杠都要编码
    # 正文要放在路径里（/key/标题/正文）；只放 query 参数时有的版本只显示标题
    url = f"{SERVER}/{load_key()}/{q(title)}/{q(body)}?group={q(GROUP)}"
    with urllib.request.urlopen(url, timeout=10) as r:
        return r.status


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    title = sys.argv[1]
    body = sys.argv[2] if len(sys.argv) > 2 else sys.stdin.read()
    if not body.strip():
        sys.exit("正文是空的")
    print("已发送" if push(title, body) == 200 else "发送失败")
