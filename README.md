<p align="center">
  <a href="https://nonebot.dev/"><img src="https://nonebot.dev/logo.png" width="200" height="200" alt="nonebot"></a>
</p>

<div align="center">
NoneBot-Adapter-YunHu

_✨ YunHu adapter for NoneBot2 ✨_

[![PyPI](https://img.shields.io/pypi/v/nonebot-adapter-yunhu)](https://pypi.org/project/nonebot-adapter-yunhu/)
![GitHub](https://img.shields.io/github/license/molanp/nonebot-adapter-yunhu)

</div>

## 支持情况

### 事件支持情况

- [x] 基础消息事件
- [x] 按钮事件上报接收
- [ ] 机器人设置事件
- [x] 按钮发送
- [x] 表单接收

### 支持的消息元素

| 元素              | 支持情况 |
| ----------------- | -------- |
| 文本 Text         | ✅       |
| 图片 Image        | ✅       |
| 提及用户 At(user) | ✅       |
| 按钮 Buttons      | ✅       |
| 表单 Form         | ⬇️       |
| 表情包 expression | ⬇️       |
| 语音 Audio        | ⬇️       |
| 视频 Video        | ✅       |
| 文件 File         | ✅       |
| HTML HTML         | ✅       |
| 文章 Post         | ⬇️       |
| Markdown          | ✅       |
| 提示信息 Tip      | ⬇️       |
| 回复 Reply        | ✅       |

### 支持的消息操作

| 操作              | 支持情况 |
| ----------------- | -------- |
| 发送 Send         | ✅       |
| 撤回 Recall       | ✅       |
| 编辑 Edit         | ✅       |
| 表情响应 Reaction | 🚫       |

## 简介

`nonebot-adapter-yunhu` 是为 [NoneBot2](https://github.com/nonebot/nonebot2) 设计的云湖(YunHu)平台适配器，支持开发云湖机器人，提供完整的消息和服务支持。

## 安装

### 使用 pip 安装

```bash
pip install nonebot-adapter-yunhu
```

### 使用 nb-cli 安装

```bash
nb adapter install nonebot-adapter-yunhu
```

### 使用 poetry 安装

```bash
poetry add nonebot-adapter-yunhu
```

## 配置

在您的 NoneBot 项目配置文件 `.env` 中添加以下配置：

> `app_id` 是 Bot 的 ID，可在 bot 信息页面查看

```env
DRIVER=~fastapi+~httpx

YUNHU_BOTS = '[{
    "app_id": "123456",
    "token": "xxx",
}
]
'

HOST = 0.0.0.0
PORT = 8080
```

在 `bot.py` 中注册适配器：

```python
import nonebot
from nonebot.adapters.yunhu import Adapter as YunhuAdapter

nonebot.init()

driver = nonebot.get_driver()
driver.register_adapter(YunhuAdapter)
```

> 在云湖控制台，上报地址为 `http(s)://{HOST}:{PORT}/yunhu/{app_id}`

## 使用方法

> [!tip]
> 
> 建议使用 `nonebot-plugin-alconna` 和 `nonebot-plugin-uninfo` 等插件，来提高插件可移植性，避免直接与适配器底层交互

### 基本用法

```python
from nonebot import on_command
from nonebot.adapters.yunhu import Bot, Event

echo = on_command("echo")

@echo.handle()
async def handle_echo(bot: Bot, event: Event):
    await echo.finish(event.get_message())
```

### 发送不同类型的消息

具体类型参考 `message.py`

```python
from nonebot import on_command
from nonebot.adapters.yunhu import Bot, Event, MessageSegment

test = on_command("test")

@test.handle()
async def handle_send_image(bot: Bot, event: Event):
    # 发送文本
    await test.send(MessageSegment.text("Hello World"))
    # 发送图片, 也可以直接传参 raw=bytes 或 raw="imageKey"
    await test.send(MessageSegment.image(url="xxxxx"))
    # @某人
    await test.send(MessageSegment.at("user_id"))
```

## 获取帮助

<img alt="image" width="300" src="https://github.com/user-attachments/assets/b133281f-58d2-4974-bee3-77b520b0864f" />

- 加入云湖群聊【NoneBot 云湖适配器交流群】: [链接](https://yhfx.jwznb.com/share?key=85HNqkjNINWc&ts=1762393601)
- 群 ID: 519215204

## 相关链接

- [适配器帮助文档](https://yunhu.awkchan.top/)
- [云湖第三方文档 1](https://yh-api.yyyyt.top/api/v1/msg.html#%E6%89%B9%E9%87%8F%E6%92%A4%E5%9B%9E%E6%B6%88%E6%81%AF)
- [云湖第三方文档 2](https://fly1919.github.io/adapter-yunhupro/markdown/dev/yunhu-official/400/7.html)
- [云湖第三方文档 3](https://www.yhchat.top/#/yunhu-bot-dev/msg-type-examples)
