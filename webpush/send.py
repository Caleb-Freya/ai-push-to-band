"""Web Push 精简版：给已订阅的网页（PWA）发通知。
依赖：pip install pywebpush
先生成 VAPID 密钥：vapid --gen（pywebpush 自带的 py_vapid），得到 private_key.pem 和公钥。
subscription.json 是网页订阅后 POST 给你的那段 JSON（见 sw.js / page.html）。
用法：python3 send.py "标题" "正文"
"""
import json
import sys

from pywebpush import webpush

sub = json.load(open("subscription.json", encoding="utf-8"))
webpush(
    subscription_info=sub,
    data=json.dumps({"title": sys.argv[1], "body": sys.argv[2][:60]}),
    vapid_private_key="private_key.pem",
    vapid_claims={"sub": "mailto:you@example.com"},  # 换成你自己的联系邮箱
)
print("已发送")
