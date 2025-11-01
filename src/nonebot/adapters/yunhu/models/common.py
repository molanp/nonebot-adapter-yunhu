from typing import Literal, Optional, Union, Dict, Any
from pydantic import BaseModel, Field
from nonebot.compat import model_validator, model_dump


class EventHeader(BaseModel):
    eventId: str
    """事件ID，全局唯一"""
    eventTime: int
    """事件产生的时间，毫秒13位时间戳"""
    eventType: str
    """事件类型"""


class Sender(BaseModel):
    """发送者信息"""

    senderId: str
    """发送者ID，给用户回复消息需要该字段"""
    senderType: Literal["user"]
    """发送者用户类型"""
    senderUserLevel: Literal["owner", "administrator", "member", "unknown"]
    """发送者级别(群主、管理员、群成员、未知)"""
    senderNickname: str
    """发送者昵称"""


class Chat(BaseModel):
    """
    聊天信息

    需在群聊中的 `chatType` 为 `group` , `chatId` 为群ID;

    在私聊中的 `chatType` 为 `bot`, `chatId` 为机器人ID

    """

    chatId: str
    """聊天ID"""
    chatType: Literal["bot", "group"]
    """聊天类型"""


class CommonContent(BaseModel):
    """通用消息内容"""

    at: Optional[list[str]] = Field(None)
    """被@的成员id列表"""
    
    def to_dict(self) -> dict:
        return model_dump(self)



class TextContent(CommonContent):
    contentType: Literal["text"] = Field("text")
    text: str

    def to_dict(self) -> dict:
        return {"text": self.text}


class ImageContent(CommonContent):
    contentType: Literal["image"] = Field("image")
    imageUrl: str
    """图片地址(直接访问需要Refer:https://www.yhchat.com/)"""
    imageName: str
    """图片文件名，可用于发送"""
    etag: str
    imageWidth: int
    """图片宽度 (像素)"""
    imageHeight: int
    """图片高度 (像素)"""
    
    def to_dict(self) -> dict:
        return {"imageKey": self.imageName.split(".")[0]}


class VideoContent(CommonContent):
    contentType: Literal["video"] = Field("video")
    videoUrl: str
    """视频地址(需要拼接baseUrl)"""
    etag: str
    videoDuration: int
    """视频时长 (秒)"""
    
    def to_dict(self) -> dict:
        return {"videoKey": self.videoUrl.split(".")[0]}


class HTMLContent(CommonContent):
    contentType: Literal["html"] = Field("html")
    text: str


class MarkdownContent(CommonContent):
    contentType: Literal["markdown"] = Field("markdown")
    text: str


class FileContent(CommonContent):
    contentType: Literal["file"] = Field("file")
    fileName: str
    """文件名"""
    fileUrl: str
    """文件地址"""
    fileSize: int
    """文件大小 (字节)"""
    etag: str
    
    def to_dict(self) -> dict:
        return {"fileKey": self.fileName.split(".")[0]}


class ExpressionContent(CommonContent):
    contentType: Literal["expression"] = Field("expression")
    imageName: str
    """表情包路径"""
    expressionId: int
    """"""
    stickerId: int
    """表情包ID"""
    stickerPackId: int
    """表情包组ID"""
    imageWidth: int
    """表情包宽度"""
    imageHeight: int
    """表情包高度"""


class FormDetail(BaseModel):
    id: str
    """表单ID"""
    type: Literal["input", "textarea", "radio", "checkbox", "switch", "select"]
    """表单类型"""
    label: str
    """表单标签"""
    value: Optional[str]
    """输入框/开关值"""
    selectIndex: Optional[int]
    """单选框/选择框选中索引"""
    selectValue: Optional[str]
    """单选框选中选项"""
    selectStatus: Optional[list[bool]]
    """多选框选中状态"""
    selectValues: Optional[list[str]]
    """多选框选中选项"""


class FormContent(CommonContent):
    contentType: Literal["form"] = Field("form")
    formJson: Dict[str, FormDetail]
    """表单数据"""


Content = Union[
    TextContent,
    HTMLContent,
    ImageContent,
    MarkdownContent,
    FileContent,
    VideoContent,
    ExpressionContent,
    FormContent,
]


class EventMessage(BaseModel):
    msgId: str
    """消息ID,全局唯一"""
    parentId: Optional[str] = None
    """引用消息时的父消息ID"""
    sendTime: int
    """消息发送时间，毫秒13位时间戳"""
    chatId: str
    """
    当前聊天的对象ID

    单聊消息,`chatId`即对方用户ID

    群聊消息,`chatId`即群ID

    机器人消息,`chatId`即机器人ID
    """
    chatType: Literal["group", "bot"]
    """当前聊天的对象类型(group: 群聊, bot: 单聊)"""
    contentType: Literal[
        "text", "image", "markdown", "file", "video", "html", "expression", "form"
    ]
    """消息内容类型（可能不存在于 incoming content）"""
    # 使用 discriminator 让 pydantic 根据 content.contentType 选择子模型
    content: Content = Field(..., discriminator="contentType")
    """消息正文（根据 contentType 解析为不同模型）"""
    commandId: Optional[int] = None
    """指令ID, 可用来区分用户发送的指令"""
    commandName: Optional[str] = None
    """指令名称, 可用来区分用户发送的指令"""

    @model_validator(mode="before")
    def _fill_content_type(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """
        在解析前确保 content 内包含 contentType（discriminator 需要）。
        优先使用外层 contentType；若不存在则根据 content 字段特征启发式推断。
        """
        content = values.get("content")
        outer_ct = values.get("contentType")
        if not isinstance(content, dict):
            return values

        # 如果已经有内层 contentType，保证外层一致或回填外层
        if "contentType" in content:
            values.setdefault("contentType", content["contentType"])
            return values

        # 优先使用外层 contentType 回填内层
        if outer_ct:
            content = {"contentType": outer_ct, **content}
            values["content"] = content
            return values

        # 启发式推断（根据云湖实际字段调整规则）
        ct: Optional[str] = None
        if "text" in content:
            ct = "text"
        elif "markdown" in content:
            ct = "markdown"
        elif "imageUrl" in content or "imageName" in content:
            ct = "image"
        elif "fileUrl" in content or "fileName" in content:
            ct = "file"
        elif "videoUrl" in content:
            ct = "video"
        elif "formJson" in content:
            ct = "form"
        elif "expressionId" in content or "stickerId" in content:
            ct = "expression"
        # 回填
        if ct:
            content = {"contentType": ct, **content}
            values["content"] = content
            values.setdefault("contentType", ct)

        return values


class MessageEventDetail(BaseModel):
    sender: Sender
    chat: Chat
    message: EventMessage


class Reply(BaseModel):
    msgId: str
    """消息ID"""
    parentId: str
    """引用消息时的父消息ID"""
    senderId: str
    """发送者ID"""
    senderType: Literal["user"]
    """发送者类型"""
    senderNickname: str
    """发送者昵称"""
    contentType: Literal["text", "image", "markdown", "file", "video", "html"]
    """消息内容类型"""
    content: Content
    """消息正文（根据 contentType 解析为不同模型）"""
    commandId: Optional[int] = None
    """指令ID, 可用来区分用户发送的指令"""
    commandName: Optional[str] = None
    """指令名称, 可用来区分用户发送的指令"""
    sendTime: int
    """消息发送时间，毫秒13位时间戳"""


class GroupNoticeDetail(BaseModel):
    time: int
    """触发事件时间戳,毫秒13位时间戳"""
    chatId: str
    """群ID"""
    chatType: Literal["group"]
    """事件对象类型"""
    userId: str
    """触发事件的用户ID"""
    nickname: str
    """触发事件用户昵称"""
    avatarUrl: str
    """触发事件用户头像URL"""


class BotNoticeDetail(BaseModel):
    time: int
    """触发事件时间戳,毫秒13位时间戳"""
    chatId: str
    """自身ID"""
    chatType: Literal["bot"]
    """事件对象类型"""
    userId: str
    """触发事件的用户ID"""
    nickname: str
    """触发事件用户昵称"""
    avatarUrl: str
    """触发事件用户头像URL"""
