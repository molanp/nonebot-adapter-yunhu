# 示例插件

## 进群退群检测

> plugins/group_handle.py

```python
from nonebot.adapters.yunhu.event import GroupJoinNoticeEvent, GroupLeaveNoticeEvent
from nonebot.adapters.yunhu.message import MessageSegment
from nonebot import on_notice

matcher = on_notice()

@matcher.handle()
async def _(event: GroupJoinNoticeEvent):
    await matcher.send(MessageSegment.markdown(f"> ![image]({event.event.avatarUrl})\n\n`{event.event.nickname}` 加入了我们..."))

@matcher.handle()
async def _(event: GroupLeaveNoticeEvent):
    await matcher.send(MessageSegment.markdown(f"> ![image]({event.event.avatarUrl})\n\n`{event.event.nickname}` 离开了我们..."))
```

## 每日发癫

> plugins/meiriyiju/\_\_init\_\_.py

```python
import random
import os
import json
from pathlib import Path
from typing import Any
from nonebot import on_command
from nonebot.adapters.yunhu import Message
from nonebot.plugin import PluginMetadata
from nonebot.params import CommandArg

__plugin_meta__ = PluginMetadata(
    name="每日发癫",
    description="每日发癫魔楞语句",
    usage="""
usage：
    每日发癫魔楞语句
    指令：
        每日发癫（参数）
    """.strip()
)


aya = on_command("每日发癫", priority=5, block=True)


DATA = None

async def readInfo(file):
    global DATA
    if DATA:
      return DATA
    path = os.path.dirname(__file__)
    with open(os.path.join(path, file), "r", encoding="utf-8") as f:
        DATA = json.loads((f.read()).strip())
    return DATA

@aya.handle()
async def _(args: Message = CommandArg()):
    cost =  args.extract_plain_text().strip()
    if cost == "":
        await aya.finish("至少需要一个参数!", at_sender=True)
    # json数据存放路径
    ayanami = (await readInfo("post.json"))["post"]
    # 随机选取数组中的一个对象
    randomPost = random.choice(ayanami).replace("阿咪", cost)
    await aya.send(randomPost, at_sender=True)
```

> plugins/meiriyiju/post.json
```json
{
    "post": [
        "阿咪啊……阿咪啊！你就像那水里的鱼，而我像是只熊！我不去捞阿咪我都不舒服！但这过程艰难且长久，不过！当我捞到阿咪的时候，我会用我的舌头，把阿咪身上的每一个角落都舔一边，然后用我的利牙，在你的脖颈上留下只属于我的印记。但这也是结果罢了，我现在依然没有得到你。所以，我，一直在盯着阿咪🤤🤤🤤",
        ...
    ]
}
```
