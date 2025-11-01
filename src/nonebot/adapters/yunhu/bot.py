from io import BytesIO
import json
from pathlib import Path
import re
from typing import TYPE_CHECKING, Any, Callable, Literal, Optional, Union
from typing_extensions import override

from nonebot.adapters import Bot as BaseBot
from nonebot.log import logger
from nonebot.compat import type_validate_python
from nonebot.message import handle_event

from .models import Reply

from .exception import ActionFailed

from .config import YunHuConfig
from .event import (
    Event,
    GroupMessageEvent,
    InstructionMessageEvent,
    MessageEvent,
    PrivateMessageEvent,
)
from .message import At, File, Image, Message, MessageSegment, Video

if TYPE_CHECKING:
    from .adapter import Adapter


async def _check_reply(bot: "Bot", event: "Event"):
    if not isinstance(event, MessageEvent):
        return

    if not event.event.message.parentId:
        return

    if event.event.message.parentId != event.event.message.msgId:
        try:
            response = await bot.get_msg(
                event.event.message.parentId,
                event.event.message.chatId,
                event.event.message.chatType,
            )
            result = type_validate_python(
                Reply,
                response,
            )
            if result.senderId == bot.bot_config.app_id:
                event.to_me = True
                event.reply = result

        except Exception as e:
            logger.error("Failed to get reply message", e)


def _check_at_me(bot: "Bot", event: "Event"):
    """
    :说明:

      检查消息是否提及Bot， 并去除@内容
    :参数:

      * ``bot: Bot``: Bot 对象
      * ``event: Event``: Event 对象
    """
    if not isinstance(event, MessageEvent):
        return

    at_list = event.event.message.content.at
    if not at_list:
        return

    if bot.bot_config.app_id in at_list:
        event.to_me = True

        message = event.get_message()

        i = 0
        while i < len(message):
            seg = message[i]
            # 如果是@消息段且是@当前机器人
            if seg.type == "at" and seg.data.get("user_id") == bot.bot_config.app_id:
                # 移除这个@消息段
                message.pop(i)
                # 如果前面有文本段，去除末尾空格
                if i > 0 and message[i - 1].type == "text":
                    message[i - 1].data["text"] = message[i - 1].data["text"].rstrip()
                # 如果后面还有文本段，去除开头空格
                if i < len(message) and message[i].type == "text":
                    message[i].data["text"] = message[i].data["text"].lstrip()
            else:
                i += 1


def _check_nickname(bot: "Bot", event: "Event"):
    """
    :说明:

      检查消息开头是否存在昵称，去除并赋值 ``event.to_me``

    :参数:

      * ``bot: Bot``: Bot 对象
      * ``event: Event``: Event 对象
    """
    if not isinstance(event, MessageEvent):
        return
    first_msg_seg: MessageSegment = event.get_message()[0]
    if first_msg_seg.type != "text":
        return

    if nicknames := set(filter(lambda n: n, bot.config.nickname)):
        # check if the user is calling me with my nickname
        nickname_regex = "|".join(nicknames)
        first_text = first_msg_seg.data["text"]

        if m := re.search(
            rf"^({nickname_regex})([\s,，]*|$)", first_text, re.IGNORECASE
        ):
            nickname = m[1]
            logger.debug(f"User is calling me {nickname}")
            event.to_me = True
            first_msg_seg.data["text"] = first_text[m.end() :]


async def send(
    bot: "Bot",
    event: Event,
    message: Union[str, Message, MessageSegment],
    at_sender: bool = False,
    reply_to: bool = False,
) -> Any:
    """默认回复消息处理函数。"""

    message = message if isinstance(message, Message) else Message(message)

    if isinstance(event, GroupMessageEvent):
        receive_id, receive_type = event.event.message.chatId, "group"
    elif isinstance(event, PrivateMessageEvent):
        receive_id, receive_type = event.get_user_id(), "user"
    elif isinstance(event, InstructionMessageEvent):
        receive_type = event.event.message.chatType
        if receive_type == "bot":
            receive_id = event.get_user_id()
            receive_type = "user"
        else:
            receive_id = event.event.message.chatId
    else:
        raise ValueError("Cannot guess `receive_id` and `receive_type` to reply!")

    full_message = Message()  # create a new message for prepending
    at_sender = at_sender and bool(event.get_user_id())
    if at_sender:
        full_message += (
            At(
                "at",
                {
                    "user_id": event.get_user_id(),
                    "name": event.event.sender.senderNickname,
                },
            )
            + " "
        )
    full_message += message

    content, msg_type = full_message.serialize()

    return await bot.send_msg(
        receive_type,
        receive_id,
        content,
        msg_type,
        event.event.message.msgId if reply_to else None,
    )


async def upload_resource_data(
    bot: "Bot",
    message: Message,
) -> Message:
    """
    遍历消息段，查找image、video、file类型并上传raw数据

    Args:
        message: 要处理的消息对象

    Returns:
        处理后的消息对象，其中缺失key的资源段已被设置key

    Raises:
        ValueError: 当资源段既没有key也没有raw数据时抛出异常
    """
    processed_message = Message()

    for segment in message:
        raw = segment.data.get("_raw")
        if isinstance(segment, Image):
            # 处理图片类型
            if not segment.data.get("imageKey") and raw:
                # 如果没有imageKey但有raw数据，则上传
                image_key = await bot.post_image(raw)
                processed_segment = Image(
                    "image",
                    {
                        "imageKey": image_key,
                    },
                )
                processed_message.append(processed_segment)
            elif not segment.data.get("imageKey") and not raw:
                # 既没有key也没有raw数据，报错
                raise ValueError("Image segment missing both imageKey and raw data")
            else:
                # 已有imageKey，直接添加
                processed_message.append(segment)

        elif isinstance(segment, Video):
            # 处理视频类型
            if not segment.data.get("videoKey") and raw:
                # 如果没有videoKey但有raw数据，则上传
                video_key = await bot.post_video(raw)
                processed_segment = Video(
                    "video",
                    {
                        "videoKey": video_key,
                    },
                )
                processed_message.append(processed_segment)
            elif not segment.data.get("videoKey") and not raw:
                # 既没有key也没有raw数据，报错
                raise ValueError("Video segment missing both videoKey and raw data")
            else:
                # 已有videoKey，直接添加
                processed_message.append(segment)

        elif isinstance(segment, File):
            # 处理文件类型
            if not segment.data.get("fileKey") and raw:
                # 如果没有fileKey但有raw数据，则上传
                file_key = await bot.post_file(raw)
                processed_segment = File(
                    "file",
                    {
                        "fileKey": file_key,
                    },
                )
                processed_message.append(processed_segment)
            elif not segment.data.get("fileKey") and not raw:
                # 既没有key也没有raw数据，报错
                raise ValueError("File segment missing both fileKey and raw data")
            else:
                # 已有fileKey，直接添加
                processed_message.append(segment)

        else:
            # 其他类型消息段直接添加
            processed_message.append(segment)

    return processed_message


class Bot(BaseBot):
    send_handler: Callable[["Bot", Event, Union[str, Message, MessageSegment]], Any] = (
        send
    )
    bot_config: YunHuConfig
    """Bot 配置"""
    nickname: str
    """Bot 昵称"""

    @override
    def __init__(
        self,
        adapter: "Adapter",
        self_id: str,
        *,
        bot_config: YunHuConfig,
        nickname: str,
    ):
        super().__init__(adapter, self_id)
        self.bot_config = bot_config
        self.nickname = nickname

    async def get_msgs(
        self, chat_id: str, chat_type: Literal["user", "hroup"], **params: Any
    ):
        response = await self.call_api(
            "bot/messages",
            method="GET",
            params={
                "chat-id": chat_id,
                "chat-type": chat_type,
                **params,
            },
        )
        try:
            response = json.loads(response)
        except Exception as e:
            raise ActionFailed(
                message=response.content,
            ) from e
        if "data" not in response:
            raise ActionFailed(
                message=response.get("msg", "Unknown error"),
            )
        return response["data"]["list"][0]

    async def get_msg(
        self, message_id: str, chat_id: str, chat_type: Literal["group", "user", "bot"]
    ):
        if chat_type == "bot":
            chat_type = "user"
        response = await self.call_api(
            "bot/messages",
            method="GET",
            params={
                "message-id": message_id,
                "chat-id": chat_id,
                "chat-type": chat_type,
                "before": 1,
            },
        )
        try:
            response = json.loads(response)
        except Exception as e:
            raise ActionFailed(
                message=response.content,
            ) from e
        if "data" not in response:
            raise ActionFailed(
                message=response.get("msg", "Unknown error"),
            )
        return response["data"]["list"][0]

    async def delete_msg(
        self, message_id: str, chat_id: str, chat_type: Literal["user", "group"]
    ):
        return await self.call_api(
            "bot/recall",
            method="POST",
            json={
                "msgId": message_id,
                "chatId": chat_id,
                "chatType": chat_type,
            },
        )

    async def edit_msg(
        self,
        message_id: str,
        recvId: str,
        recvType: str,
        content: dict,
        content_type: Literal["text", "html", "markdown"],
    ):
        return await self.call_api(
            "bot/edit",
            method="POST",
            json={
                "msgId": message_id,
                "recvId": recvId,
                "recvType": recvType,
                "contentType": content_type,
                "content": content,
            },
        )

    async def reply_msg(self, message_id: str, content: dict, content_type: str):
        json = {
            "content": content,
            "contentType": content_type,
            "parentId": message_id,
        }

        return await self.call_api(
            "bot/send",
            method="POST",
            json=json,
        )

    async def send_msg(
        self,
        receive_type: Literal["group", "user"],
        receive_id: str,
        content: dict,
        content_type: str,
        parent_id: Optional[str] = None,
    ):
        return await self.call_api(
            "bot/send",
            method="POST",
            json={
                "recvId": receive_id,
                "recvType": receive_type,
                "content": content,
                "contentType": content_type,
                "parentId": parent_id,
            },
        )

    async def get_file_url(self, file_key: str):
        return f"https://chat-file.jwznb.com/{file_key}"

    async def post_file(
        self,
        file: Union[str, bytes, BytesIO, Path],
    ):
        if not isinstance(file, (bytes, BytesIO)):
            file = open(file, "rb").read()

        files = [("file", file)]

        response = await self.call_api("file/upload", method="POST", files=files)
        try:
            response = json.loads(response)
        except Exception as e:
            raise ActionFailed(
                message=response.content,
            ) from e
        if "data" not in response:
            raise ActionFailed(
                message=response.get("msg", "Unknown error"),
            )
        return response["data"]["fileKey"]

    async def post_video(
        self,
        video: Union[str, bytes, BytesIO, Path],
    ):
        if not isinstance(video, (bytes, BytesIO)):
            video = open(video, "rb").read()

        videos = [("video", video)]

        response = await self.call_api("video/upload", method="POST", files=videos)
        try:
            response = json.loads(response)
        except Exception as e:
            raise ActionFailed(
                message=response.content,
            ) from e
        if "data" not in response:
            raise ActionFailed(
                message=response.get("msg", "Unknown error"),
            )
        return response["data"]["videoKey"]

    async def post_image(
        self,
        image: Union[str, bytes, BytesIO, Path],
    ):
        if not isinstance(image, (bytes, BytesIO)):
            image = open(image, "rb").read()

        images = [("image", image)]

        response = await self.call_api("image/upload", method="POST", files=images)
        try:
            response = json.loads(response)
        except Exception as e:
            raise ActionFailed(
                message=response.content,
            ) from e
        if "data" not in response:
            raise ActionFailed(
                message=response.get("msg", "Unknown error"),
            )
        return response["data"]["imageKey"]

    @override
    async def send(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        event: Event,
        message: Union[str, Message, MessageSegment],
        **kwargs: Any,
    ) -> Any:
        """根据 `event` 向触发事件的主体回复消息。
        参数:
            event: Event 对象
            message: 要发送的消息
            at_sender (bool): 是否 @ 事件主体
            kwargs: 其他参数，可以与 {ref}`nonebot.adapters.yunhu.adapter.Adapter.custom_send` 配合使用
        返回:
            API 调用返回数据
        异常:
            ValueError: 缺少 `user_id`, `group_id`
            NetworkError: 网络错误
            ActionFailed: API 调用失败
        """
        return await self.__class__.send_handler(self, event, message, **kwargs)

    @override
    async def call_api(self, api: str, **data) -> Any:
        """
        :说明:
          调用 云湖 协议 API
        :参数:
          * ``api: str``: API 名称
          * ``**data: Any``: API 参数
        :返回:
          - ``Any``: API 调用返回数据
        :异常:
          - ``NetworkError``: 网络错误
          - ``ActionFailed``: API 调用失败
        """
        return await super().call_api(api, **data)

    async def handle_event(self, event: Event) -> None:
        if isinstance(event, MessageEvent):
            _check_at_me(self, event)
            _check_nickname(self, event)
            await _check_reply(self, event)
        await handle_event(self, event)
