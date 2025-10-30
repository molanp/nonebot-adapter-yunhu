from collections.abc import Iterable
from dataclasses import dataclass
import re
from typing import TYPE_CHECKING, Literal, Optional, TypedDict, Union
from typing_extensions import override

from nonebot.adapters import Message as BaseMessage
from nonebot.adapters import MessageSegment as BaseMessageSegment

from .models.common import Content, TextContent
from nonebot.compat import model_dump


class MessageSegment(BaseMessageSegment["Message"]):
    """
    云湖 协议 MessageSegment 适配。具体方法参考协议消息段类型或源码。
    """

    @classmethod
    @override
    def get_message_class(cls) -> type["Message"]:
        return Message

    @override
    def is_text(self) -> bool:
        return self.type in ["text", "markdown", "html"]

    @override
    def __str__(self) -> str:
        return self.data.get("text", "") if self.is_text() else ""

    @override
    def __add__(  # type: ignore
        self, other: Union[str, "MessageSegment", Iterable["MessageSegment"]]
    ) -> "Message":
        return Message(self) + (
            MessageSegment.text(other) if isinstance(other, str) else other
        )

    @override
    def __radd__(  # type: ignore
        self, other: Union[str, "MessageSegment", Iterable["MessageSegment"]]
    ) -> "Message":
        return (
            MessageSegment.text(other) if isinstance(other, str) else Message(other)
        ) + self

    @staticmethod
    def text(text: str) -> "Text":
        return Text("text", {"text": text})

    @staticmethod
    def at(user_id: str):
        return At("at", {"user_id": user_id})

    @staticmethod
    def image(image_key: str) -> "Image":
        return Image("image", {"image_key": image_key})

    @staticmethod
    def video(file_key: str, duration: Optional[int] = None) -> "MessageSegment":
        return Video("video", {"video_key": file_key, "duration": duration})

    @staticmethod
    def file(file_key: str, file_name: Optional[str] = None) -> "MessageSegment":
        return File("file", {"file_key": file_key, "file_name": file_name})

    @staticmethod
    def markdown(text: str) -> "MessageSegment":
        return Markdown("markdown", {"text": text})

    @staticmethod
    def html(text: str) -> "MessageSegment":
        return Html("html", {"text": text})


class _TextData(TypedDict):
    text: str


@dataclass
class Text(MessageSegment):
    if TYPE_CHECKING:
        data: _TextData  # type: ignore

    @override
    def __str__(self) -> str:
        return self.data["text"]


@dataclass
class Markdown(MessageSegment):
    if TYPE_CHECKING:
        data: _TextData  # type: ignore

    @override
    def __str__(self) -> str:
        return self.data["text"]


@dataclass
class Html(MessageSegment):
    if TYPE_CHECKING:
        data: _TextData  # type: ignore

    @override
    def __str__(self) -> str:
        return self.data["text"]


class _AtData(TypedDict):
    user_id: str


@dataclass
class At(MessageSegment):
    if TYPE_CHECKING:
        data: _AtData  # type: ignore

    @override
    def __str__(self) -> str:
        return f"@{self.data['user_id']}"


class _ImageData(TypedDict):
    image_key: str


@dataclass
class Image(MessageSegment):
    if TYPE_CHECKING:
        data: _ImageData  # type: ignore

    @override
    def __str__(self) -> str:
        return f"[image:{self.data['image_key']!r}]"


class _VideoData(TypedDict):
    video_key: str
    duration: Optional[int]


@dataclass
class Video(MessageSegment):
    if TYPE_CHECKING:
        data: _VideoData  # type: ignore

    @override
    def __str__(self) -> str:
        return f"[video:{self.data!r}]"


class _FileData(TypedDict):
    file_key: str
    file_name: Optional[str]


@dataclass
class File(MessageSegment):
    if TYPE_CHECKING:
        data: _FileData  # type: ignore

    @override
    def __str__(self) -> str:
        return f"[file:{self.data!r}]"


class Message(BaseMessage[MessageSegment]):
    """
    云湖 协议 Message 适配。
    """

    @classmethod
    @override
    def get_segment_class(cls) -> type[MessageSegment]:
        return MessageSegment

    @override
    def __add__(
        self, other: Union[str, "MessageSegment", Iterable["MessageSegment"]]
    ) -> "Message":
        return super().__add__(
            MessageSegment.text(other) if isinstance(other, str) else other
        )

    @override
    def __radd__(
        self, other: Union[str, "MessageSegment", Iterable["MessageSegment"]]
    ) -> "Message":
        return super().__radd__(
            MessageSegment.text(other) if isinstance(other, str) else other
        )

    @staticmethod
    @override
    def _construct(msg: str) -> Iterable[MessageSegment]:
        yield Text("text", {"text": msg})

    def serialize(self) -> tuple[dict, str]:
        if len(self) >= 2:
            result = {}
            _type = "text"
            for seg in self:
                if isinstance(seg, At):
                    result["at"].append(seg.data["user_id"])
                else:
                    result |= seg.data
                    _type = seg.type

            return result, _type

        elif len(self) == 1:
            return (
                {"at": [self.data["user_id"]]} if isinstance(self, At) else self[0].data
            ), ("text" if isinstance(self, At) else self[0].type)
        else:
            raise ValueError("Cannot serialize empty message")

    @staticmethod
    def deserialize(
        content: Content,
        at_list: Optional[list[str]],
        message_type: Literal[
            "text", "image", "markdown", "file", "video", "html", "expression", "form"
        ],
        command_name: Optional[str] = None,
    ) -> "Message":
        command_name = f"{command_name} " if command_name else ""
        msg = Message(command_name)
        parsed_content = model_dump(content)

        if message_type == "text":
            assert isinstance(content, TextContent)
            text = content.text
            text_begin = 0

            # 记录已经处理过的用户名及其在at_list中的对应ID
            at_name_mapping = {}
            # at_list的索引
            at_index = 0

            # 修改正则表达式以匹配格式: @用户名 \u200b (后面可能还有内容)
            for embed in re.finditer(
                r"@(?P<name>[^ \u200b]+)\s*\u200b",
                text,
            ):
                if matched := text[text_begin : embed.start()]:
                    msg.extend(Message(Text("text", {"text": matched})))

                text_begin = embed.end()

                # 获取@用户名
                user_name = embed.group("name")

                # 如果这个用户名已经映射过，使用之前记录的用户ID
                # 否则从at_list中获取下一个用户ID
                if user_name in at_name_mapping:
                    actual_user_id = at_name_mapping[user_name]
                else:
                    actual_user_id = ""
                    if at_list and at_index < len(at_list):
                        actual_user_id = at_list[at_index]
                        at_name_mapping[user_name] = (
                            actual_user_id  # 记录这个用户名对应的at_list中的ID
                        )
                        at_index += 1

                msg.extend(
                    Message(
                        At(
                            "at",
                            {"user_id": actual_user_id},
                        )
                    )
                )

            if matched := text[text_begin:]:
                msg.append(Text("text", {"text": text[text_begin:]}))

        # 处理其他消息类型
        elif seg_builder := getattr(MessageSegment, message_type, None):
            msg.append(seg_builder(**parsed_content))
        else:
            msg.append(MessageSegment(message_type, parsed_content))

        return msg

    @override
    def extract_plain_text(self) -> str:
        text_list: list[str] = []
        text_list.extend(str(seg) for seg in self if seg.is_text())
        return "".join(text_list)
