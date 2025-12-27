from collections.abc import Iterable
from dataclasses import dataclass
import re
from typing import TYPE_CHECKING, Any, Optional, TypedDict, Union
from typing_extensions import override, NotRequired

from nonebot.adapters import Message as BaseMessage
from nonebot.adapters import MessageSegment as BaseMessageSegment
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
        return self.type == "text"

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
    def at(user_id: str, name: Optional[str] = None) -> "At":
        return At("at", {"user_id": user_id, "name": name})

    @staticmethod
    def image(
        imageKey: Optional[str] = None, raw: Optional[bytes] = None, **kwargs
    ) -> "Image":
        return Image("image", {"imageKey": imageKey, "_raw": raw})

    @staticmethod
    def video(
        videoKey: Optional[str] = None, raw: Optional[bytes] = None, **kwargs
    ) -> "Video":
        return Video("video", {"videoKey": videoKey, "_raw": raw})

    @staticmethod
    def file(
        fileKey: Optional[str] = None, raw: Optional[bytes] = None, **kwargs
    ) -> "File":
        return File("file", {"fileKey": fileKey, "_raw": raw})

    @staticmethod
    def markdown(text: str) -> "MessageSegment":
        return Markdown("markdown", {"text": text})

    @staticmethod
    def html(text: str) -> "Html":
        return Html("html", {"text": text})

    @staticmethod
    def buttons(buttons: list[list[ButtonBody]]) -> "Buttons":
        """
        :param buttons: 按钮列表，子列表为每一行的按钮
        """
        return Buttons("buttons", {"buttons": buttons})

    @staticmethod
    def audio(audioUrl: str, audioDuration: int, **kwargs):
        """语音消息，只收不发"""
        return Audio("audio", {"audioUrl": audioUrl, "audioDuration": audioDuration})

    @staticmethod
    def face(code: str, emoji: str) -> "MessageSegment":
        """表情"""
        return Face("face", {"code": code, "emoji": emoji})


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
        return f"[markdown:{self.data['text']}"


@dataclass
class Html(MessageSegment):
    if TYPE_CHECKING:
        data: _TextData  # type: ignore

    @override
    def __str__(self) -> str:
        return f"[html:{self.data['text']}"


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


class _FaceData(TypedDict):
    code: str
    emoji: str


@dataclass
class Face(MessageSegment):
    if TYPE_CHECKING:
        data: _FaceData  # type: ignore

    @override
    def __str__(self) -> str:
        return f"[face:code={self.data['code']}]"


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
        """
        序列化消息为协议内容
        """
        result: dict[str, Any] = {"at": []}
        if "audio" in self:
            logger.warning("Sending audio is not supported")
            self.exclude("audio")
        if "buttons" in self:
            buttons = self["buttons"]
            assert isinstance(buttons, Buttons)
            result["buttons"] = buttons.data["buttons"]

        if not self:
            raise ValueError("Empty message")

        # 只处理文本相关（text/markdown/html）和 Face 段
        if all(seg.is_text() or isinstance(seg, (At, Face)) for seg in self):
            text_buffer = ""
            lasttexttype: str | None = None
            for seg in self:
                if isinstance(seg, At):
                    result["at"].append(seg.data["user_id"])
                elif isinstance(seg, Face):
                    text_buffer += f"[.{seg.data['code']}]\u200b"
                elif seg.is_text():
                    text_buffer += seg.data["text"]
                    lasttexttype = seg.type

            if text_buffer:
                result["text"] = text_buffer
                # 如果没有任何文本段（只有 @），默认仍然用 text
                return result, lasttexttype or "text"
            # 只有 @，无文本
            return result, "text"

        # 处理混合类型（如图片、文件等）
        _type = None
        for seg in self:
            if isinstance(seg, At):
                result["at"].append(seg.data["user_id"])
            elif seg.is_text():
                result["text"] = seg.data["text"]
                _type = seg.type
            else:
                result |= seg.data
                _type = seg.type
        return result, _type or "text"

    @staticmethod
    def deserialize(
        content: Content,
        at_list: Optional[list[str]],
        message_type: str,
        command_name: Optional[str] = None,
    ) -> "Message":
        msg = Message(f"{command_name} ") if command_name else Message()
        parsed_content = content.to_dict()
        from .tool import YUNHU_EMOJI_MAP, _EMOJI_PATTERN

        def _split_face_segments(segment: str) -> list[MessageSegment]:
            """将文本分割为 Text/Face 段列表"""
            segments: list[MessageSegment] = []
            last_end = 0
            for match in _EMOJI_PATTERN.finditer(segment):
                if match.start() > last_end:
                    normal_text = segment[last_end : match.start()]
                    if normal_text:
                        segments.append(Text("text", {"text": normal_text}))
                emoji_code = match.group(0)
                clean_code = emoji_code.lstrip("[").rstrip("]").lstrip(".")
                emoji_value = YUNHU_EMOJI_MAP.get(emoji_code)
                if emoji_value:
                    segments.append(
                        Face("face", {"code": clean_code, "emoji": emoji_value})
                    )
                last_end = match.end()
            if last_end < len(segment):
                normal_text = segment[last_end:]
                if normal_text:
                    segments.append(Text("text", {"text": normal_text}))
            return segments

        def parse_text(text: str, with_face: bool = False):
            # 优化性能：只正则一次，分割@和普通文本
            at_pattern = re.compile(r"@(?P<name>[^@\u200b\s]+)\s*\u200b")
            at_name_mapping = {}
            at_index = 0
            pos = 0
            for embed in at_pattern.finditer(text):
                # 处理@前的文本
                segment = text[pos : embed.start()]
                if segment:
                    if with_face:
                        msg.extend(Message(_split_face_segments(segment)))
                    else:
                        msg.append(Text("text", {"text": segment}))
                # 处理@本身
                user_name = embed.group("name")
                if user_name in at_name_mapping:
                    actual_user_id = at_name_mapping[user_name]
                else:
                    actual_user_id = ""
                    if at_list and at_index < len(at_list):
                        actual_user_id = at_list[at_index]
                        at_name_mapping[user_name] = actual_user_id
                        at_index += 1
                if actual_user_id:
                    msg.append(At("at", {"user_id": actual_user_id, "name": user_name}))
                pos = embed.end()
            # 处理最后一段文本
            segment = text[pos:]
            if segment:
                if with_face:
                    msg.extend(Message(_split_face_segments(segment)))
                else:
                    msg.append(Text("text", {"text": segment}))

        match message_type:
            case "text":
                assert isinstance(content, TextContent)
                parse_text(content.text, with_face=True)
            case "markdown":
                assert isinstance(content, MarkdownContent)
                parse_text(content.text)
            case "html":
                assert isinstance(content, HTMLContent)
                parse_text(content.text)
            case _:
                parsed_content.pop("at", None)
                if seg_builder := getattr(MessageSegment, message_type, None):
                    msg.append(seg_builder(**parsed_content))
                else:
                    msg.append(MessageSegment(message_type, parsed_content))
        return msg

    @override
    def extract_plain_text(self) -> str:
        text_list: list[str] = []
        text_list.extend(str(seg) for seg in self if seg.is_text())
        return "".join(text_list)
