"""最小 MCP 工具：让支持 MCP 的 AI（Claude Desktop / Claude Code 等）自己调用推送。
依赖：pip install mcp
Claude Code 里添加：claude mcp add band -- python3 /你的路径/examples/mcp_server.py
"""
import os
import sys

from mcp.server.fastmcp import FastMCP

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from bark_push import push  # noqa: E402

mcp = FastMCP("band")


@mcp.tool()
def send_to_band(title: str, body: str) -> str:
    """推一条短消息到用户手环。正文尽量 60 字以内。"""
    return "已发送" if push(title, body) == 200 else "发送失败"


if __name__ == "__main__":
    mcp.run()
