# APIs

## 获取 Bot 实例

以下所有 bot 均通过这样获取：

```python
matcher = on_xxx(...)

@matcher.handle()
async def _(bot):
  ...
```

更高级的方法是读取 `current_bot` 变量，因为获取到的都是同一个 bot，在此不再举例

## 基础方法

### _method_ get_msgs

获取消息列表

```python
async def get_msgs(
  self, chat_id: str, chat_type:  Literal["user", "group"], **params: Any
) -> list[Reply]:
```

#### 参数

- `chat_id`: 获取消息对象 ID
  - 用户: 使用 `userId`
  - 群: 使用 `groupId`
- `chat_type`: 获取消息对象类型
  - 用户: `user`
  - 群: `group`
- `message_id`(`str`): (可选)起始消息 ID，不填时可以配合 `before` 参数返回最近的 N 条消息
- `before`(`int`): (可选) 指定消息 ID 前 N 条，默认 0 条
- `after`(`int`): (可选) 指定消息 ID 后 N 条，默认 0 条

#### 返回

- `list[Reply]` 消息对象列表

### _method_ get_msg

获取指定消息

```python
async def get_msg(
    self, message_id: str, chat_id: str, chat_type: Literal["group", "user", "bot"]
) -> Reply:
```

#### 参数

- `message_id`: 消息 ID
- `chat_id`: 获取消息对象 ID
  - 用户: 使用 `userId`
  - 群: 使用 `groupId`
- `chat_type`: 获取消息对象类型
  - 用户: `user`
  - 机器人: `bot`(自动转为`user`,请不要使用此类型，仅作兼容)
  - 群: `group`

#### 返回

- `Reply` 消息对象

### _method_ delete_msg

撤回指定消息

```python
async def delete_msg(
    self, message_id: str, chat_id: str, chat_type: Literal["user", "group"]
):
```

#### 参数

- `message_id`: 撤回消息的 ID
- `chat_id`: 撤回消息对象 ID
  - 用户: 使用 `userId`
  - 群: 使用 `groupId`
- `chat_type`: 撤回消息对象类型
  - 用户: `user`
  - 群: `group`

### _method_ edit_msg

编辑消息

```python
async def edit_msg(
    self,
    message_id: str,
    recvId: str,
    recvType: Literal["user", "group"],
    content: BaseTextContent,
    content_type: BASE_TEXT_TYPE,
):
```

#### 参数

- `message_id`: 编辑消息的 ID
- `recvId`: 编辑消息对象 ID
  - 用户: 使用 `userId`
  - 群: 使用 `groupId`
- `recvType`: 编辑消息对象类型
  - 用户: `user`
  - 群: `group`
- `content`: 新消息内容, 字典结构参考类 `BaseTextContent`
- `content_type`: 新消息内容类型(`text`/`markdown`/`html`)

### _method_ get_group_info

获取群信息

```python
async def get_group_info(self, group_id: str):
```

#### 参数

- `group_id`: 群 ID

#### 返回

- `GroupInfo` 群信息

### _method_ get_user_info

获取用户信息

```python
async def get_user_info(self, user_id: str):
```

#### 参数

- `user_id`: 用户 ID

#### 返回

- `UserInfo` 用户信息

### _method_ set_group_board

设置群看板

```python
async def set_group_board(
    self,
    content: str,
    content_type: BASE_TEXT_TYPE,
    group_id: str,
    memberId: Optional[str] = None,
    expire_time: int = 0,
):
```

#### 参数

- `content`: 看板内容
- `content_type`: 看板内容类型(`text`/`markdown`/`html`)
- `group_id`: 群 ID
- `memberId`: 成员 ID(可为指定成员设置，留空则全局设置)
- `expire_time`: 看板过期时间(0 为不过期)

#### 返回

- `BoardResponse`

### _method_ dismiss_group_board

移除群看板

```python
async def dismiss_group_board(
    self,
    group_id: str,
    memberId: Optional[str] = None,
):
```

#### 参数

- `group_id`: 群 ID
- `memberId`: 成员 ID (可为指定成员取消，留空则全部取消)

#### 返回

- `BoardResponse`

### _method_ set_user_board

设置用户看板

```python
async def set_user_board(
    self,
    content: str,
    content_type: BASE_TEXT_TYPE,
    user_id: str,
    expire_time: int = 0,
):
```

#### 参数

- `content`: 看板内容
- `content_type`: 看板内容类型(`text`/`markdown`/`html`)
- `user_id`: 用户 ID
- `expire_time`: 看板过期时间(0 为不过期)

#### 返回

- `BoardResponse`

### _method_ dismiss_user_board

移除用户看板

```python
async def dismiss_user_board(
    self,
    user_id: str,
):
```

#### 参数

- `user_id`: 用户 ID

#### 返回

- `BoardResponse`

### _method_ set_all_board

设置全局看板

```python
async def set_all_board(
    self,
    content: str,
    content_type: BASE_TEXT_TYPE,
    expire_time: int = 0,
):
```

#### 参数

- `content`: 看板内容
- `content_type`: 看板内容类型(`text`/`markdown`/`html`)
- `expire_time`: 看板过期时间(0 为不过期)

#### 返回

- `BoardResponse`

### _method_ dismiss_all_board

移除全局看板

```python
async def dismiss_all_board(self):
```

#### 返回

- `BoardResponse`

## 高级方法

### _method_ call_api

::: tip
若不知道这个方法的作用请不要调用
:::
调用 云湖 协议 API

```python
async def call_api(self, api: str, **data) -> Any:
```

#### 参数

- `api: str`: API 名称或自定义 URL
- `**data: Any`: API 参数

#### 返回

- `Any`: API 调用返回数据

#### 异常

- `NetworkError`: 网络错误
- `ActionFailed`: API 调用失败

### _method_ send_msg

::: warning
此为发送消息底层 API，不建议使用此方法，请使用 `matcher.send()`
:::

发送消息

```python
async def send_msg(
    self,
    receive_type: Literal["group", "user"],
    receive_id: str,
    content: dict[str, Any],
    content_type: str,
    parent_id: Optional[str] = None,
):
```

#### 参数

- `receive_type`: 接收对象类型
  - 用户: `user`
  - 群: `group`
- `receive_id`: 接收对象 ID
- `content`: 消息内容
- `content_type`: 消息内容类型(`text`/`markdown`/`html`)
- `parent_id`: 引用消息 ID(可选)

#### 返回

- `SendMsgResponse`

### _method_ post_file

::: warning
不建议调用此方法，发送内容含有媒体消息段会自动上传
:::
上传文件获取 `fileKey`

### _method_ post_video

::: warning
不建议调用此方法，发送内容含有媒体消息段会自动上传
:::
上传视频获取 `videoKey`

### _method_ post_image

::: warning
不建议调用此方法，发送内容含有媒体消息段会自动上传
:::
上传文件获取 `imageKey`
