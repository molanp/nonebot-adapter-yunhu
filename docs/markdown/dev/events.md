# 事件 (Events)

`nonebot-adapter-yunhu` 负责接收来自云湖平台的 Webhook 事件。

本页将详细说明云湖事件与 Nonebot 事件之间的对应关系。

您可以在插件中通过依赖注入来监听这些事件。

例如：

```python
#  监听通知事件
matcher = on_notice()

@matcher.handle()
async def _(event: GroupJoinNoticeEvent): # 仅监听新成员加入群聊
    await matcher.send(MessageSegment.markdown(f"> ![image]({event.event.avatarUrl})\n\n`{event.event.nickname}` 加入了我们..."))

# 监听消息事件
aya = on_message()
@aya.handle()
async def _(event: MessageEvent): # 任意消息均会触发此响应器
  ...

com = on_command("aya", block=True, priority=5)
@com.handle()
async def _(event: InstructionMessageEvent): # 仅斜线指令会触发
  ...



ovo = on_command("ovo", block=True, priority=5)
@com.handle()
async def _(event: GroupMessageEvent): # 仅群消息会触发
  ...
## 不建议这样监听群消息，可以使用rule来过滤群消息
```

## 消息事件 (`MessageEvent`)

| 云湖事件类型                  | Nonebot 事件                   | Nonebot 事件类            | 触发时机                   |
| :---------------------------- | :----------------------------- | :------------------------ | :------------------------- |
| `message.receive.normal`      | `message.receive.normal.group` | `GroupMessageEvent`       | 收到群组消息               |
| `message.receive.normal`      | `message.receive.normal.bot`   | `PrivateMessageEvent`     | 收到私聊消息               |
| `message.receive.instruction` | `message.receive.instruction`  | `InstructionMessageEvent` | 用户触发了机器人的斜线指令 |

## 通知事件 (`NoticeEvent`)

| 云湖事件类型             | Nonebot 事件           | Nonebot 事件类             | 触发时机                   |
| :----------------------- | :--------------------- | :------------------------- | :------------------------- |
| `message.receive.normal` | `group.tip`            | `TipNoticeEvent`           | 群成员被设置为管理员       |
| `bot.followed`           | `bot.followed`         | `BotFollowedNoticeEvent`   | 用户添加机器人到通讯录     |
| `bot.unfollowed`         | `bot.unfollowed`       | `BotUnfollowedNoticeEvent` | 用户从通讯录删除机器人     |
| `group.join`             | `group.join`           | `GroupJoinNoticeEvent`     | 新成员加入群组             |
| `group.leave`            | `group.leave`          | `GroupLeaveNoticeEvent`    | 成员退出群组               |
| `button.report.inline`   | `button.report.inline` | `ButtonReportNoticeEvent`  | 用户点击了消息中的内联按钮 |
