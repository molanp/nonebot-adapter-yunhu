from collections.abc import Iterable
from dataclasses import dataclass
import re
from typing import TYPE_CHECKING, Any, Literal, Optional, TypedDict, Union
from typing_extensions import override, NotRequired

from nonebot.adapters import Message as BaseMessage
from nonebot.adapters import MessageSegment as BaseMessageSegment
from nonebot.compat import model_dump
from nonebot.log import logger

from .models.common import (
    ButtonBody,
    Content,
    HTMLContent,
    MarkdownContent,
    TextContent,
)


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
        return self.type in ("text", "markdown", "html")

    @override
    def __str__(self) -> str:
        return str(self.data)

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
    def at(user_id: str, name: Optional[str] = None):
        return At("at", {"user_id": user_id, "name": name})

    @staticmethod
    def image(imageKey: Optional[str] = None, raw: Optional[bytes] = None) -> "Image":
        return Image("image", {"imageKey": imageKey, "_raw": raw})

    @staticmethod
    def video(
        videoKey: Optional[str] = None, raw: Optional[bytes] = None
    ) -> "MessageSegment":
        return Video("video", {"videoKey": videoKey, "_raw": raw})

    @staticmethod
    def file(
        fileKey: Optional[str] = None, raw: Optional[bytes] = None
    ) -> "MessageSegment":
        return File("file", {"fileKey": fileKey, "_raw": raw})

    @staticmethod
    def markdown(text: str) -> "MessageSegment":
        return Markdown("markdown", {"text": text})

    @staticmethod
    def html(text: str) -> "MessageSegment":
        return Html("html", {"text": text})

    @staticmethod
    def buttons(buttons: list[list[ButtonBody]]):
        """
        :param buttons: 按钮列表，子列表为每一行的按钮
        :type buttons: list[list[ButtonBody]]
        """
        return Buttons("button", {"buttons": buttons})

    @staticmethod
    def audio(audioUrl: str, audioDuration: int):
        """语音消息，只收不发"""
        return Audio("audio", {"audioUrl": audioUrl, "audioDuration": audioDuration})


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
    name: Optional[str]


@dataclass
class At(MessageSegment):
    if TYPE_CHECKING:
        data: _AtData  # type: ignore

    @override
    def __str__(self) -> str:
        return f"[at:user_id={self.data['user_id']},name={self.data['name']}]"


class _ImageData(TypedDict):
    imageKey: Optional[str]
    _raw: NotRequired[Optional[bytes]]


@dataclass
class Image(MessageSegment):
    if TYPE_CHECKING:
        data: _ImageData  # type: ignore

    @override
    def __str__(self) -> str:
        return f"[image:{self.data['imageKey']}]"


class _VideoData(TypedDict):
    videoKey: Optional[str]
    _raw: NotRequired[Optional[bytes]]


@dataclass
class Video(MessageSegment):
    if TYPE_CHECKING:
        data: _VideoData  # type: ignore

    @override
    def __str__(self) -> str:
        return f"[video:{self.data['videoKey']}]"


class _FileData(TypedDict):
    fileKey: Optional[str]
    _raw: NotRequired[Optional[bytes]]


@dataclass
class File(MessageSegment):
    if TYPE_CHECKING:
        data: _FileData  # type: ignore

    @override
    def __str__(self) -> str:
        return f"[file:{self.data['fileKey']}]"


class _ButtonData(TypedDict):
    buttons: list[list[ButtonBody]]


@dataclass
class Buttons(MessageSegment):
    if TYPE_CHECKING:
        data: _ButtonData  # type: ignore

    @override
    def __str__(self) -> str:
        return f"[buttons:{self.data['buttons']}]"


class _AudioData(TypedDict):
    audioUrl: str
    audioDuration: int


@dataclass
class Audio(MessageSegment):
    if TYPE_CHECKING:
        data: _AudioData  # type: ignore

    @override
    def __str__(self) -> str:
        return f"[audio:{self.data['audioUrl']}]"


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

    def serialize(self) -> tuple[dict[str, Any], str]:
        result = {"at": []}
        if "audio" in self:
            logger.warning("Sending audio is not supported")
            self.exclude("audio")
        if "buttons" in self:
            buttons = self["buttons"]
            assert isinstance(buttons, Buttons)
            result["buttons"] = [
                model_dump(b) for button in buttons.data["buttons"] for b in button
            ]

        if len(self) >= 2:
            _type = "text"
            prev_type: Optional[str] = None

            for seg in self:
                if isinstance(seg, At):
                    result["at"].append(seg.data["user_id"])
                    continue

                # 合并相邻且同类型的文本段（text/markdown/html）
                if seg.is_text():
                    if prev_type == seg.type and "text" in result:
                        result["text"] = result["text"] + seg.data["text"]
                    else:
                        result["text"] = seg.data["text"]
                else:
                    # 其他类型保留现有行为（后者字段会覆盖同名字段）
                    result |= seg.data

                prev_type = seg.type
                _type = seg.type

            return result, _type

        elif len(self) == 1:
            return (
                {"at": [self.data["user_id"]]} if isinstance(self, At) else self[0].data
            ), ("text" if isinstance(self, At) else self[0].type)
        else:
            raise ValueError("Empty message")

    @staticmethod
    def deserialize(
        content: Content,
        at_list: Optional[list[str]],
        message_type: Literal[
            "text",
            "image",
            "markdown",
            "file",
            "video",
            "html",
            "expression",
            "form",
            "tip",
            "audio",
        ],
        command_name: Optional[str] = None,
    ) -> "Message":
        command_name = f"{command_name} " if command_name else None
        msg = Message(command_name)
        parsed_content = content.to_dict()

        if message_type in ["text", "markdown", "html"]:
            assert isinstance(content, Union[TextContent, MarkdownContent, HTMLContent])
            text = content.text
            text_begin = 0

            # 记录已经处理过的用户名及其在at_list中的对应ID
            at_name_mapping = {}
            # at_list的索引
            at_index = 0

            # 匹配格式: @用户名 \u200b
            for embed in re.finditer(
                r"@(?P<name>[^@\u200b\s]+)\s*\u200b",
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
                if actual_user_id:
                    """忽略假at"""
                    msg.extend(
                        Message(
                            At(
                                "at",
                                {"user_id": actual_user_id, "name": user_name},
                            )
                        )
                    )

            if matched := text[text_begin:]:
                msg.append(Text("text", {"text": text[text_begin:]}))

        # 处理其他消息类型
        elif seg_builder := getattr(MessageSegment, message_type, None):
            parsed_content.pop("at", None)
            msg.append(seg_builder(**parsed_content))
        else:
            parsed_content.pop("at", None)
            msg.append(MessageSegment(message_type, parsed_content))

        return msg

    @override
    def extract_plain_text(self) -> str:
        text_list: list[str] = []
        text_list.extend(str(seg) for seg in self if seg.is_text())
        return "".join(text_list)
