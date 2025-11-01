# NoneBot YunHu Adapter

<div align="center">

YunHu adapter for NoneBot2

[![PyPI](https://img.shields.io/pypi/v/nonebot-adapter-yunhu)](https://pypi.org/project/nonebot-adapter-yunhu/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/nonebot-adapter-yunhu)](https://pypi.org/project/nonebot-adapter-yunhu/)
![GitHub](https://img.shields.io/github/license/molanp/nonebot-adapter-yunhu)

</div>


## 事件支持情况

- [x] 基础消息事件
- [ ] 按钮事件接收
- [ ] 机器人设置消息事件
- [ ] 按钮发送
- [ ] 表单发送

## 简介

`nonebot-adapter-yunhu` 是一个为 [NoneBot2](https://github.com/nonebot/nonebot2) 设计的云湖(YunHu)平台适配器。它允许您使用 NoneBot2 框架开发云湖机器人，提供了对云湖平台消息和服务的完整支持。

## 安装

### 使用 pip 安装

```bash
pip install nonebot-adapter-yunhu
```

### 使用 poetry 安装

```bash
poetry add nonebot-adapter-yunhu
```

## 配置

在您的 NoneBot 项目配置文件 `.env` 中添加以下配置：

```env
DRIVER=~fastapi+~httpx

YUNHU_BOTS = '[{
    "app_id": "123456",
    "token": "xxx",
}
]
'

HOST = 127.0.0.1
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

### 基本用法

```python
from nonebot import on_command
from nonebot.adapters.yunhu import Bot, MessageEvent

echo = on_command("echo")

@echo.handle()
async def handle_echo(bot: Bot, event: MessageEvent):
    await echo.finish(event.get_message())
```

### 发送不同类型的消息

```python
from nonebot import on_command
from nonebot.adapters.yunhu import Bot, MessageEvent, MessageSegment

send_image = on_command("image")

@send_image.handle()
async def handle_send_image(bot: Bot, event: MessageEvent):
    # 发送文本
    await bot.send(event, MessageSegment.text("Hello World"))

    # 发送图片（需要先上传图片获取 image_key）
    await bot.send(event, MessageSegment.image("image_key"))

    # @某人
    await bot.send(event, MessageSegment.at("user_id"))
```

## 特性

- ✅ 支持接收和发送多种类型的消息
- ✅ 支持 Webhook 回调模式
- ✅ 完整的事件系统支持
- ✅ 易于使用的 API 封装
- ✅ 良好的类型提示支持

## 许可证

MIT License


## 相关链接

- [云湖第三方文档 1](https://yh-api.yyyyt.top/api/v1/msg.html#%E6%89%B9%E9%87%8F%E6%92%A4%E5%9B%9E%E6%B6%88%E6%81%AF)
- [云湖第三方文档 2](https://fly1919.github.io/adapter-yunhupro/markdown/dev/yunhu-official/400/7.html)
- [云湖第三方文档 3](https://www.yhchat.top/#/yunhu-bot-dev/msg-type-examples)
