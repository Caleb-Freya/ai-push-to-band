# 让 AI 的话震到你的小米手环

你不在聊天页面的时候，AI 主动找你 → 手机弹通知 → 手环震一下，你一抬手就知道「他找我了」。

（不是定时闹钟。你正开着聊天页时不推，免得一边看一边震；你走开了它才推。）

不用改手环、不用刷机，靠的是「小米运动健康」本来就有的**应用通知转发**：只要 AI 能让手机弹出一条通知，手环就能收到。

```
你的 AI（Claude / GPT / 自己写的机器人）
   │  调用一行脚本
   ▼
Bark（iPhone 推送 App）  或  网页推送（PWA，安卓也行）
   │  手机弹系统通知
   ▼
小米运动健康 App ──蓝牙──▶ 小米手环 震动显示
```

三条路线，选一条就行。作者自己每天用的是**路线三**（自建网页 + 网页推送）；没有自己网页的：iPhone 用路线一 Bark，安卓用路线二 ntfy，五分钟就能试。

| | 路线一：Bark | 路线二：ntfy | 路线三：网页推送 PWA |
|---|---|---|---|
| 适合 | iPhone，没有自己的网页 | 安卓，没有自己的网页 | 已经有自己的聊天网页（作者在用），两种手机都行 |
| 要装 | Bark App（免费） | ntfy App（免费开源） | 不装 App，要有自己的 HTTPS 网站 |
| 代码 | `bark_push.py`，标准库 | `ntfy_push.py`，标准库 | pywebpush + 一个网页 |

---

## 路线一：Bark（iPhone，最简单）

[Bark](https://github.com/Finb/Bark) 是开源的 iOS 推送 App：装上就给你一把 key，任何程序访问一个网址，手机就弹通知。

### 1. 手机上
1. App Store 搜「Bark」安装，打开，**允许通知**。
2. 首页会显示一个网址，形如 `https://api.day.app/xxxxxxxx/这里改成推送内容`，中间那串 `xxxxxxxx` 就是你的 key。
3. iPhone「设置 → 通知 → Bark」：打开「允许通知」，「锁定屏幕」「通知中心」「横幅」都勾上。

### 2. 电脑 / 服务器上
```bash
export BARK_KEY=你的key            # 或者在脚本同目录建 bark.conf，第一行写 key
python3 bark_push.py "提醒" "该喝水了"
```
手机响了，就说明这一步通了。

可选环境变量：
- `BARK_MAX`：正文最长多少字（默认 60，超出截断加…）
- `BARK_GROUP`：通知分组名（默认 AI）
- `BARK_SERVER`：自建 [bark-server](https://github.com/Finb/bark-server) 的地址（默认官方 `https://api.day.app`）

### 3. 让 AI 自己调用
**Claude Code / 能跑命令的 AI**：在它的规则文件（如 CLAUDE.md）里写一句：
```
想主动跟我说话时，运行：python3 /路径/bark_push.py "标题" "一句话（60字内）"
```

**支持 MCP 的 AI**（Claude Desktop、Claude Code 等）：用 `examples/mcp_server.py`
```bash
pip install mcp
claude mcp add band -- python3 /路径/examples/mcp_server.py
```
AI 就多了一个 `send_to_band` 工具。

**顺便也能做定时提醒**（不用 AI 也行，crontab）：
```
0 15 * * * BARK_KEY=你的key python3 /路径/bark_push.py "下午了" "起来走两步"
```

---

## 路线二：ntfy（安卓，最简单）

[ntfy](https://github.com/binwiederhier/ntfy) 是开源的推送服务，有安卓 App，用法和 Bark 差不多：手机订阅一个「主题」，程序往这个主题发消息，手机就弹通知。

### 1. 手机上
1. 安装 ntfy App：Google Play 或 F-Droid 搜「ntfy」；国内手机没有谷歌商店的，可以从 [GitHub Releases](https://github.com/binwiederhier/ntfy-android/releases) 下载 APK（待验证：国内网络能否稳定收到 ntfy.sh 的推送，收不到可自建 ntfy 服务器）。
2. 打开 App，点「+」订阅一个主题，名字自己起，**越长越随机越好**（比如 `ai-band-7f3k9q2x`）——ntfy.sh 上的主题是公开的，谁猜到名字谁就能看到你的消息。
3. 允许 ntfy 发通知；在手机设置里把 ntfy 设为**不限制后台 / 允许自启动 / 省电白名单**，否则后台被杀就收不到。

### 2. 电脑 / 服务器上
```bash
export NTFY_TOPIC=你起的主题名      # 或者在脚本同目录建 ntfy.conf，第一行写主题名
python3 ntfy_push.py "提醒" "该喝水了"
```
可选：`NTFY_MAX`（正文最长字数，默认 60）、`NTFY_SERVER`（自建 ntfy 地址，默认 `https://ntfy.sh`）。

让 AI 调用的方法和路线一一样，把 `bark_push.py` 换成 `ntfy_push.py` 即可（MCP 示例里改一行 import）。

---

## 路线三：网页推送 PWA（作者在用，安卓也能用）

原理：网页通过浏览器订阅推送（Web Push 标准，VAPID 密钥签名），你的服务器拿着订阅信息发消息，浏览器弹系统通知，手环再转发。

关键步骤（精简示例在 `webpush/`）：
1. 网站必须是 **HTTPS**（本地调试可用 localhost）。
2. 生成 VAPID 密钥：`pip install pywebpush`，然后 `vapid --gen`，得到私钥 `private_key.pem` 和公钥。
3. 网页 `page.html` 填上公钥，注册 `sw.js`，点按钮请求通知权限并订阅，把得到的订阅 JSON 存成 `subscription.json`（正式使用时应 POST 到你的服务器保存）。
4. 发送：`python3 webpush/send.py "标题" "正文"`。

**iPhone 注意**：iOS 16.4 起才支持网页推送，而且必须先用 Safari「分享 → 添加到主屏幕」，从主屏图标打开后再点订阅；直接在 Safari 里打开是订阅不了的。

---

### 作者的用法：不在页面时才推

作者的 AI 平时在自建聊天网页里说话。规则只有一条：**AI 发了新消息，而你此刻没在看这个页面，就推一条到手环。** 做法：

1. 网页在前台时，每 30 秒告诉服务器「我在看」：
```js
setInterval(() => {
  if (document.visibilityState === "visible") fetch("/api/here", { method: "POST" });
}, 30000);
document.addEventListener("visibilitychange", () => {
  if (document.visibilityState === "visible") fetch("/api/here", { method: "POST" });
});
```
2. 服务器记下最后一次「我在看」的时间；AI 每发一条消息时检查一下：
```python
import time
last_seen = 0            # /api/here 被调用时更新：last_seen = time.time()

def on_ai_message(text):
    if time.time() - last_seen > 60:      # 超过 60 秒没在看 → 你不在页面
        push("新消息", text)              # 换成 bark_push / ntfy_push / 网页推送 任一种
```
这样你开着页面聊天时手环安静，一走开 AI 再找你，手环就震。用 Bark / ntfy 的也可以照搬这个判断。

---

## 小米运动健康设置

### iPhone（作者实测：iPhone + 小米手环；日常用网页推送，也试过 Bark，都能转发）
1. 打开「小米运动健康」→ 底部「设备」→ 点你的手环。
2. 进「应用通知」（有的版本叫「通知提醒」），打开总开关。
3. 打开 **「其他」**（或「其他应用」）这一项——Bark 和网页推送的通知都是靠它转发的（实测）。列表里如果单独有 Bark，也一起打开。
4. 确认 iPhone「设置 → 蓝牙」里手环是已连接状态，并且系统弹过的「是否共享系统通知」选了**允许**（iPhone 是靠这个把通知交给手环的）；没弹过或点了不允许，可在「设置 → 蓝牙 → 手环右边的 ⓘ → 共享系统通知」打开（待验证：不同 iOS 版本位置可能不同）。

### 安卓
1. 「小米运动健康」→「设备」→ 手环 →「应用通知」，打开总开关，在列表里打开 **ntfy**（路线二），或你的**浏览器**（路线三，网页推送是以浏览器名义发出的）。
2. 手机「设置 → 应用 → 小米运动健康 → 通知使用权」允许（第一次打开应用通知时一般会引导）。
3. 把「小米运动健康」加入省电白名单 / 允许后台运行、自启动，否则后台被杀就不转发了。
4. 小米/红米手机以外的安卓也可以用，步骤类似（待验证：各厂商省电设置名称不同）。

---

## 常见问题

**手机响了，手环不震**
- 手环开了勿扰/睡眠模式。
- 手环 App 里有「手机解锁时不提醒」之类的选项（待验证：部分版本叫「仅锁屏时提醒」），你正在玩手机时就不转发。
- 应用通知里没打开 Bark /「其他」/ 浏览器。
- 手环和手机蓝牙断了：打开小米运动健康让它同步一下。

**手环只显示标题，不显示正文**
- Bark 的正文要放在网址路径里（`/key/标题/正文`），只用 `?body=` 参数时有的情况只显示标题。本仓库脚本已经这样处理。

**中文乱码 / 发送失败**
- 标题和正文都要做 URL 编码（尤其是空格、`/`、`#`、`?`）。脚本里已用 `urllib.parse.quote(…, safe="")` 处理。

**消息太长被截断**
- 手环屏幕小，一屏只能显示几行，长消息要在手环上翻页或直接被截。建议正文 **60 字以内**，最重要的话放最前面；脚本默认超过 60 字自动截断，可用 `BARK_MAX` 调。

**安全**
- Bark key 相当于往你手机发通知的钥匙，别贴到公开的地方；放环境变量或 `bark.conf`（已在 `.gitignore` 里）。
- ntfy 的主题名同理，起长一点的随机名。
- 网页推送的 `private_key.pem`、`subscription.json` 同理。

---

## 致谢
- [Finb/Bark](https://github.com/Finb/Bark)、[Finb/bark-server](https://github.com/Finb/bark-server)、[ntfy](https://github.com/binwiederhier/ntfy)：本方案的推送通道。
- 通知聚合类项目（如 [heimdallr](https://github.com/LeslieLeung/heimdallr)）支持 Bark 在内的多种渠道；本仓库只做一件事：让 AI 的话到手环上，越短越好。

## License
MIT
