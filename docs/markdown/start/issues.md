# 常见问题 (FAQ)

本页收集了用户在使用 `nonebot-adapter-yunhu` 时可能遇到的一些常见问题及其解决方案。

---

### Q1: 机器人配置正确，但收不到任何消息，也没有任何反应。

**检查 Webhook 配置**:

- 在云湖平台的机器人后台，仔细检查您填写的「订阅地址」是否正确。它应该是 `http(s)://你的公网地址:端口/app_id` 的完整形式。
- 确保「订阅地址」中的 `app_id` 与您在 Nonebot 配置中填写的 `app_id` 完全一致。

**检查事件订阅**:

- 在云湖后台，确认您已经勾选了需要接收的事件，特别是「消息事件」。

---

### Q2: 机器人可以收到消息，但发送图片或文件失败。

- **文件大小限制**: 您尝试发送的文件可能超过了云湖平台的大小限制。请尝试发送一个较小的文件。

::: tip
图片最大大小为 10MB, 文件和视频最大大小为 20MB。
:::

---

### Q3: 如何在我的插件中调用云湖特有的 API？

**A:** 您可以通过 `bot` 对象实例来访问适配器封装的所有 API 方法。

- **示例**: 在您的插件中，您可以通过 `bot` 来获取当前的 `Bot` 实例，然后调用其上的方法。

```python
from nonebot import on_command
from nonebot.adapters.yunhu import Message
from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name="只是测试",
    description="",
    usage="""
    123
    """.strip()
)


aya = on_command("t", priority=5, block=True)


@aya.handle()
async def _(bot):
  result = await bot.get_user_info("123456")

### 如果想要语法提示器可以正常提示bot对象所具有的APi，可以这样写
from nonebot.adapters.yunhu import Bot

@aya.handle()
async def _(bot: Bot):
  result = await bot.get_user_info("123456")
```

- 关于所有可用的 API 方法，请参考 [**开发文档 / APIs**](./../dev/apis.md) 章节。
