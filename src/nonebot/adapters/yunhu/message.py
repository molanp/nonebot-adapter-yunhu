from collections.abc import Iterable
from dataclasses import dataclass
import re
from typing import TYPE_CHECKING, Any, Optional, TypedDict, Union
from typing_extensions import override

from nonebot.adapters import Message as BaseMessage
from nonebot.adapters import MessageSegment as BaseMessageSegment
from nonebot.log import logger
from .tool import YUNHU_EMOJI_MAP, _EMOJI_PATTERN
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
    def at(user_id: str, name: str = "") -> "At":
        return At("at", {"user_id": user_id, "name": name or user_id})

    @staticmethod
    def image(
        url: Optional[str] = None,
        raw: Optional[bytes] = None,
        imageKey: Optional[str] = None,
        **kwargs,
    ) -> "Image":
        return Image("image", {"url": url, "raw": raw, "imageKey": imageKey})

    @staticmethod
    def video(
        url: Optional[str] = None,
        raw: Optional[bytes] = None,
        videoKey: Optional[str] = None,
        **kwargs,
    ) -> "Video":
        return Video("video", {"url": url, "raw": raw, "videoKey": videoKey})

    @staticmethod
    def file(
        url: Optional[str] = None,
        raw: Optional[bytes] = None,
        fileKey: Optional[str] = None,
        **kwargs,
    ) -> "File":
        return File("file", {"url": url, "raw": raw, "fileKey": fileKey})

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
    def audio(url: str, duration: int, **kwargs):
        """语音消息，只收不发"""
        return Audio("audio", {"url": url, "duration": duration})

    @staticmethod
    def face(code: str, emoji: str = "") -> "MessageSegment":
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
    name: str


@dataclass
class At(MessageSegment):
    if TYPE_CHECKING:
        data: _AtData  # type: ignore

    @override
    def __str__(self) -> str:
        return f"[at:user_id={self.data['user_id']},name={self.data['name']}]"


class _ImageData(TypedDict):
    url: Optional[str]
    raw: Optional[bytes]
    imageKey: Optional[str]


@dataclass
class Image(MessageSegment):
    if TYPE_CHECKING:
        data: _ImageData  # type: ignore

    @override
    def __str__(self) -> str:
        return f"[image:{self.data['imageKey']}]"


class _VideoData(TypedDict):
    url: Optional[str]
    raw: Optional[bytes]
    videoKey: Optional[str]


@dataclass
class Video(MessageSegment):
    if TYPE_CHECKING:
        data: _VideoData  # type: ignore

    @override
    def __str__(self) -> str:
        return f"[video:{self.data['url']}]"


class _FileData(TypedDict):
    url: Optional[str]
    raw: Optional[bytes]
    fileKey: Optional[str]


@dataclass
class File(MessageSegment):
    if TYPE_CHECKING:
        data: _FileData  # type: ignore

    @override
    def __str__(self) -> str:
        return f"[file:{self.data['url']}]"


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
    url: str
    duration: int


@dataclass
class Audio(MessageSegment):
    if TYPE_CHECKING:
        data: _AudioData  # type: ignore

    @override
    def __str__(self) -> str:
        return f"[audio:{self.data['url']}]"


class _FaceData(TypedDict):
    code: str
    """表情码"""
    emoji: str
    """字符emoji"""


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
        # sourcery skip: dict-assign-update-to-union
        """
        序列化消息为协议内容
        """
        if not self:
            raise ValueError("Empty message")

        result: dict[str, Any] = {"at": []}

        # 不支持语音发送
        if "audio" in self:
            logger.warning("Sending audio is not supported")
            self.exclude("audio")

        # 按钮单独挂在 result 上
        if "buttons" in self:
            result["buttons"] = []
            for seg in self["buttons"]:
                result["buttons"].extend(seg.data["buttons"])

        # 只包含 Text / At / Face 的消息，统一走纯文本通道
        if all(isinstance(seg, (Text, At, Face)) for seg in self):
            text_buffer: list[str] = []
            last_text_type: str | None = None

            for seg in self:
                if isinstance(seg, At):
                    result["at"].append(seg.data["user_id"])
                    text_buffer.append(f"@{seg.data['name']}\u200b")
                elif isinstance(seg, Face):
                    # 按协议要求转回 [.<code>]
                    text_buffer.append(f"[.{seg.data['code']}]\u200b")
                elif isinstance(seg, Text):
                    text_buffer.append(seg.data["text"])
                    last_text_type = seg.type

            result["text"] = "".join(text_buffer)
            return result, last_text_type or "text"

        # 包含图片且消息段大于1，转为md发送
        if len(self) > 1 and self.has("image"):
            return self._build_markdown_message(result)
        # 其它混合类型（只有单图/视频/文件）
        text_parts: list[str] = []
        message_type: Optional[str] = None

        for seg in self:
            if isinstance(seg, At):
                result["at"].append(seg.data["user_id"])
                text_parts.append(seg.data["name"] + "\u200b")
            elif isinstance(seg, (Markdown, Html)):
                text_parts.append(seg.data["text"])
                message_type = seg.type
            else:
                # 非文本段的数据直接合并到 result
                result.update(seg.data)
                message_type = seg.type

        result["text"] = "".join(text_parts)
        return result, message_type or "text"

    def _build_markdown_message(
        self, result: dict[str, Any]
    ) -> tuple[dict[str, Any], str]:
        md_parts: list[str] = []

        for seg in self:
            if isinstance(seg, At):
                # at 仍然单独放到 result["at"]，markdown 里按普通文本输出
                result["at"].append(seg.data["user_id"])
                name = seg.data["name"] or seg.data["user_id"]
                md_parts.append(f"@{name}\u200b")
            elif isinstance(seg, Face):
                # 表情转成字符
                md_parts.append(seg.data["emoji"])
            elif seg.is_text():
                md_parts.append(seg.data["text"])
            elif isinstance(seg, Image):
                if image_url := seg.data["url"]:
                    # 普通 markdown 图片语法，src 由云湖解释
                    md_parts.append(f"![image]({image_url})\n")
            else:
                # 文件、视频等不进 markdown 混排，忽略或以后按需扩展
                logger.debug(
                    "Ignore non-image segment in markdown mixed message: %r", seg
                )

        md_text = "".join(md_parts).strip()
        if not md_text:
            # 与其构造空 markdown，不如显式抛错提示调用方
            raise ValueError("Cannot serialize image message: no renderable content")

        result["text"] = md_text
        return result, "markdown"

    @staticmethod
    def deserialize(
        content: Content,
        at_list: Optional[list[str]],
        message_type: str,
        command_name: Optional[str] = None,
    ) -> "Message":
        # 特殊情况：
        # 1. 仅 text 消息会出现
        # 2. command_name 形如 "xxx"
        # 3. content.text 形如 "/xxx"
        # 4. 消息内容就是这个 command_name
        # 这种情况下，期望最终消息内容只有 command_name 本身，
        # 不需要再把 content.text 解析追加一遍。
        if (
            command_name
            and message_type == "text"
            and isinstance(content, TextContent)
            and content.text.removeprefix("/").strip() == command_name
        ):
            return Message(command_name)

        msg = Message(f"{command_name} ") if command_name else Message()
        parsed_content = content.to_dict()

        def _split_face_segments(segment: str) -> list[MessageSegment]:
            """将文本分割为 Text/Face 段列表"""
            segments: list[MessageSegment] = []
            last_end = 0
            for match in _EMOJI_PATTERN.finditer(segment):
                if match.start() > last_end:
                    normal_text = segment[last_end : match.start()]
                    if normal_text:
                        segments.append(MessageSegment.text(normal_text))
                emoji_code = match.group(0)
                clean_code = emoji_code.lstrip("[").rstrip("]").lstrip(".")
                emoji_value = YUNHU_EMOJI_MAP.get(emoji_code)
                if emoji_value:
                    segments.append(MessageSegment.face(clean_code, emoji_value))
                last_end = match.end()
            if last_end < len(segment):
                normal_text = segment[last_end:]
                if normal_text:
                    segments.append(MessageSegment.text(normal_text))
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
                        msg.append(MessageSegment.text(segment))
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
                    msg.append(MessageSegment.at(actual_user_id, user_name))
                pos = embed.end()
            # 处理最后一段文本
            segment = text[pos:]
            if segment:
                if with_face:
                    msg.extend(Message(_split_face_segments(segment)))
                else:
                    msg.append(MessageSegment.text(segment))

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
        text_list.extend(str(seg) for seg in self if seg.type == "text")
        return "".join(text_list)
