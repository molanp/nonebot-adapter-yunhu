from copy import deepcopy
from datetime import datetime
from typing import TYPE_CHECKING, Any, Literal, Optional
from typing_extensions import override

from nonebot.adapters import Event as BaseEvent
from nonebot.compat import model_dump
from nonebot.utils import escape_tag


from .message import Message
from .models import (
    EventHeader,
    MessageEventDetail,
    Reply,
    GroupNoticeDetail,
    BotNoticeDetail,
    ButtonReportNoticeDetail,
    TipNoticeDetail
)


class Event(BaseEvent):
    """
    云湖协议事件。各事件字段参考 `云湖文档`_

    .. _云湖文档:
        https://www.yhchat.com/document/300-310
    """

    __event__ = ""
    version: str
    """事件内容版本号"""
    header: EventHeader
    """包括事件的基础信息"""
    event: Any
    """包括事件的内容。注意：Event对象的结构会在不同的eventType下发生变化"""

    @override
    def get_type(self) -> str:
        return self.header.eventType

    @override
    def get_event_name(self) -> str:
        return self.header.eventType

    @override
    def get_event_description(self) -> str:
        return escape_tag(str(model_dump(self)))

    @override
    def get_message(self) -> Message:
        raise ValueError("Event has no message!")

    @override
    def get_plaintext(self) -> str:
        raise ValueError("Event has no plaintext!")

    @override
    def get_user_id(self) -> str:
        raise ValueError("Event has no user_id!")

    @override
    def get_session_id(self) -> str:
        raise ValueError("Event has no session_id!")

    @override
    def is_tome(self) -> bool:
        return False

    @property
    def time(self) -> datetime:
        return datetime.utcfromtimestamp(int(self.header.eventTime) / 1000)


class MessageEvent(Event):
    __event__ = "message.receive.normal"
    event: MessageEventDetail

    to_me: bool = False
    """
    :说明: 消息是否与机器人有关

    :类型: ``bool``
    """
    reply: Optional[Reply] = None

    if TYPE_CHECKING:
        _message: Message
        original_message: Message

    @override
    def get_type(self) -> Literal["message"]:
        return "message"

    @override
    def get_event_name(self) -> str:
        return f"{self.get_type()}.{self.event.message.chatType}"

    @override
    def get_event_description(self) -> str:
        return (
            f"Message {self.event.message.msgId} from {self.get_user_id()}"
            f"@[{self.event.message.chatType}:{self.event.message.chatId}]"
            f" '{escape_tag(str(self.get_message()))}'"
        )

    @override
    def get_message(self) -> Message:
        if not hasattr(self, "_message"):
            deserialized = Message.deserialize(
                self.event.message.content,
                self.event.message.content.at,
                self.event.message.contentType,
                self.event.message.commandName,
            )
            setattr(
                self,
                "_message",
                deserialized,
            )
            setattr(
                self,
                "original_message",
                deepcopy(deserialized),
            )

        return getattr(self, "_message")

    @property
    def message_id(self) -> str:
        return self.event.message.msgId

    @override
    def get_plaintext(self) -> str:
        return str(self.get_message())

    @override
    def get_user_id(self) -> str:
        return self.event.sender.senderId

    @override
    def get_session_id(self) -> str:
        return (
            f"{self.event.message.chatType}"
            f"_{self.event.message.chatId}"
            f"_{self.get_user_id()}"
        )

    @override
    def is_tome(self) -> bool:
        return self.to_me


class GroupMessageEvent(MessageEvent):
    __event__ = "message.receive.normal.group"


class PrivateMessageEvent(MessageEvent):
    __event__ = "message.receive.normal.bot"
    to_me: bool = True


class InstructionMessageEvent(MessageEvent):
    """机器人收不到用户对其他机器人的命令消息，不用担心误触发"""

    __event__ = "message.receive.instruction"
    to_me: bool = True


class NoticeEvent(Event):
    __event__ = "__notice__"
    event: Any

    @override
    def get_type(self) -> Literal["notice"]:
        return "notice"

    @override
    def get_event_name(self) -> str:
        return self.__event__

    @override
    def get_event_description(self) -> str:
        return escape_tag(str(model_dump(self.event)))

    @override
    def get_message(self) -> Message:
        raise ValueError("Event has no message!")

    @override
    def get_plaintext(self) -> str:
        raise ValueError("Event has no plaintext!")

    @override
    def get_user_id(self) -> str:
        return getattr(self.event, "userId", "")

    @override
    def get_session_id(self) -> str:
        raise ValueError("Event has no session_id!")


class GroupJoinNoticeEvent(NoticeEvent):

    __event__ = "group.join"
    event: GroupNoticeDetail


class GroupLeaveNoticeEvent(NoticeEvent):

    __event__ = "group.leave"
    event: GroupNoticeDetail


class BotFollowedNoticeEvent(NoticeEvent):

    __event__ = "bot.followed"
    event: BotNoticeDetail


class BotUnfollowedNoticeEvent(NoticeEvent):

    __event__ = "bot.unfollowed"
    event: BotNoticeDetail


class TipNoticeEvent(NoticeEvent):
    __event__ = "group.tip"
    event: TipNoticeDetail


class ButtonReportNoticeEvent(NoticeEvent):
    __event__ = "button.report.inline"
    event: ButtonReportNoticeDetail
