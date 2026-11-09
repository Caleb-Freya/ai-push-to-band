# 让 AI 的话震到你的小米手环

AI 想对你说一句话 → 手机弹通知 → 手环震一下、亮屏显示。

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

两条路线：

| | 路线一：Bark（推荐） | 路线二：网页推送 PWA |
|---|---|---|
| 适合 | iPhone 用户，想 5 分钟搞定 | 安卓用户，或不想装 Bark |
| 要装 | Bark App（免费） | 不装 App，要有自己的网站（HTTPS） |
| 代码 | 一个标准库 Python 脚本 | 需要 pywebpush + 一个网页 |

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

**定时提醒**（不用 AI 也行，crontab）：
```
0 15 * * * BARK_KEY=你的key python3 /路径/bark_push.py "下午了" "起来走两步"
```

---

## 路线二：网页推送 PWA（安卓也能用）

原理：网页通过浏览器订阅推送（Web Push 标准，VAPID 密钥签名），你的服务器拿着订阅信息发消息，浏览器弹系统通知，手环再转发。

关键步骤（精简示例在 `webpush/`）：
1. 网站必须是 **HTTPS**（本地调试可用 localhost）。
2. 生成 VAPID 密钥：`pip install pywebpush`，然后 `vapid --gen`，得到私钥 `private_key.pem` 和公钥。
3. 网页 `page.html` 填上公钥，注册 `sw.js`，点按钮请求通知权限并订阅，把得到的订阅 JSON 存成 `subscription.json`（正式使用时应 POST 到你的服务器保存）。
4. 发送：`python3 webpush/send.py "标题" "正文"`。

**iPhone 注意**：iOS 16.4 起才支持网页推送，而且必须先用 Safari「分享 → 添加到主屏幕」，从主屏图标打开后再点订阅；直接在 Safari 里打开是订阅不了的。

---

## 小米运动健康设置

### iPhone（作者自用实测：iPhone + 小米手环，Bark 和网页推送都能转发）
1. 打开「小米运动健康」→ 底部「设备」→ 点你的手环。
2. 进「应用通知」（有的版本叫「通知提醒」），打开总开关。
3. 打开 **「其他」**（或「其他应用」）这一项——Bark 和网页推送的通知都是靠它转发的（实测）。列表里如果单独有 Bark，也一起打开。
4. 确认 iPhone「设置 → 蓝牙」里手环是已连接状态，并且系统弹过的「是否共享系统通知」选了**允许**（iPhone 是靠这个把通知交给手环的）；没弹过或点了不允许，可在「设置 → 蓝牙 → 手环右边的 ⓘ → 共享系统通知」打开（待验证：不同 iOS 版本位置可能不同）。

### 安卓
1. 「小米运动健康」→「设备」→ 手环 →「应用通知」，打开总开关，在列表里打开你的**浏览器**（网页推送是以浏览器名义发出的）或对应 App。
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
- 网页推送的 `private_key.pem`、`subscription.json` 同理。

---

## 致谢
- [Finb/Bark](https://github.com/Finb/Bark)、[Finb/bark-server](https://github.com/Finb/bark-server)：本方案的推送通道。
- 通知聚合类项目（如 [heimdallr](https://github.com/LeslieLeung/heimdallr)）支持 Bark 在内的多种渠道；本仓库只做一件事：让 AI 的话到手环上，越短越好。

## License
MIT
