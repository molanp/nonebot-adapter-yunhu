# 权限 (Permission)

`nonebot-adapter-yunhu` 适配器提供了基础的权限管理功能，允许你通过`permission`参数来匹配特定的事件

## 权限列表

| 权限名        | 权限描述 |
| :------------ | :------- |
| `GROUP_OWNER` | 群主     |
| `GROUP_ADMIN` | 群管理员 |
| `PRIVATE`     | 私聊     |
| `GROUP`       | 群聊     |
| `INSTRUCTION` | 指令     |

## Demo

```python
from nonebot import on_command
from nonebot.adapters.yunhu import MessageSegment
from nonebot.adapters.yunhu.permission import PRIVATE


matcher = on_command("test", permission=PRIVATE)

@matcher.handle()
async def handle_receive():
    await matcher.send(MessageSegment.markdown("> Hello, world!"))
```
