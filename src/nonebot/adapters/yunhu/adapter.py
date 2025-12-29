import asyncio
import inspect
import json
from typing import Any, Optional, cast
from typing_extensions import override

from pygtrie import StringTrie

from nonebot import get_plugin_config
from nonebot.adapters import Adapter as BaseAdapter
from nonebot.compat import type_validate_python
from nonebot.drivers import (
    URL,
    ASGIMixin,
    Driver,
    HTTPClientMixin,
    HTTPServerSetup,
    Request,
    Response,
)
from nonebot.utils import escape_tag

from . import event
from .bot import Bot
from .config import Config, YunHuConfig
from .event import Event
from .exception import (
    ApiNotAvailable,
    YunHuAdapterException,
    NetworkError,
    ActionFailed,
)
from nonebot.log import logger
from .models import BotInfo


class Adapter(BaseAdapter):
    # init all event models
    event_models: StringTrie = StringTrie(separator=".")
    """所有事件模型索引"""

    for model_name in dir(event):
        model = getattr(event, model_name)
        if not inspect.isclass(model) or not issubclass(model, Event):
            continue
        event_models["." + model.__event__] = model

    @override
    def __init__(self, driver: Driver, **kwargs: Any):
        super().__init__(driver, **kwargs)
        """云湖适配器配置"""
        self.configs: Config = get_plugin_config(Config)
        self.tasks: set["asyncio.Task"] = set()
        self.bot_apps: dict[str, YunHuConfig] = {}
        self.setup()

    @classmethod
    @override
    def get_name(cls) -> str:
        """适配器名称: `YunHu`"""
        return "YunHu"

    async def startup(self):
        for yhc in self.configs.yunhu_bots:
            if not yhc.app_id or not yhc.token:
                continue
            result = await self.get_bot_info(yhc)
            if result.code != 1:
                logger.error(
                    f"<r><bg #f8bbd0>Failed to get Both {yhc.app_id} info. Response {result.msg}</bg #f8bbd0></r> "
                )
                continue
            assert result.data
            bot_info = result.data.bot

            bot = Bot(
                self,
                bot_info.botId,
                bot_config=yhc,
                nickname=bot_info.nickname,
            )
            self.bot_apps[yhc.app_id] = yhc
            self.bot_connect(bot)
            logger.info(
                f"Bot {bot_info.nickname} ({bot_info.botId}) connected",
            )
            logger.info(f"当前 Bot 使用人数: {bot_info.headcount}")

    def setup(self) -> None:
        if not isinstance(self.driver, ASGIMixin):
            raise RuntimeError(
                f"Current driver {self.config.driver} "
                "doesn't support reverse connections!"
                f"{self.get_name()} Adapter needs a ASGI Driver to work."
            )

        if not isinstance(self.driver, HTTPClientMixin):
            raise RuntimeError(
                f"Current driver {self.config.driver} "
                "doesn't support http client requests!"
                f"{self.get_name()} Adapter needs a HTTPClient Driver to work."
            )
        for yhc in self.configs.yunhu_bots:
            if not yhc.app_id or not yhc.token:
                logger.warning(f"缺少配置项: app_id={yhc.app_id}, token={yhc.token}")
                continue
            setup = HTTPServerSetup(
                URL(f"/yunhu/{yhc.app_id}"),
                "POST",
                self.get_name(),
                self._handle_http,
            )
            self.setup_http_server(setup)
        self.on_ready(self.startup)

    def get_api_url(self, path: str) -> URL:
        return URL("https://chat-go.jwzhd.com").joinpath("open-apis/v1/", path)

    async def get_bot_info(self, bot_config: YunHuConfig) -> BotInfo:

        response = await self.send_request(
            Request(
                "POST",
                "https://chat-web-go.jwzhd.com/v1/bot/bot-info",
                json={"botId": bot_config.app_id},
            ),
        )
        return type_validate_python(BotInfo, response)

    async def send_request(self, request: Request, **data: Any):
        return_response = data.get("_return_response", False)
        use_stream = data.get("_use_stream", False)
        timeout: float = data.get("_timeout", self.config.api_timeout)
        request.timeout = timeout

        if not isinstance(self.driver, HTTPClientMixin):
            raise ApiNotAvailable

        try:
            if use_stream:
                result = []
                is_json = None
                async for response in self.driver.stream_request(request):
                    result.append(response.content)
                    if is_json is None:
                        is_json = response.headers["Content-Type"].find("application/json") != -1
                content = b"".join(result) if result else b""

                if not is_json:
                    return content
                content_str = content.decode('utf-8')
                return json.loads(content_str)

            response = await self.driver.request(request)

            if 200 <= response.status_code < 300:
                if not response.content:
                    raise ValueError("Empty response")

                if return_response:
                    return response

                if response.headers["Content-Type"].find("application/json") != -1:
                    return json.loads(response.content)
                else:
                    return response.content

            raise NetworkError(
                f"HTTP request received unexpected "
                f"status code: {response.status_code}, "
                f"response content: {response.content}"
            )

        except YunHuAdapterException:
            raise

        except Exception as e:
            raise NetworkError("HTTP request failed") from e

    @override
    async def _call_api(  # pyright: ignore[reportIncompatibleMethodOverride]
        self, bot: Bot, api: str, **data: Any
    ) -> Any:
        logger.debug(f"Calling API: {api}, data: {data}")
        params = data.get("params")
        if api.startswith("https://"):
            url = api
        else:
            url = self.get_api_url(api)
            if params:
                params["token"] = bot.bot_config.token
        request = Request(
            method=data["method"],
            url=url,
            files=data.get("files"),
            json=data.get("json"),
            data=data.get("data"),
            params=params,
        )

        result = await self.send_request(request, _use_stream=data.get("_use_stream"))
        if isinstance(result, dict) and result.get("code") != 1:
            raise ActionFailed(message=result.get("msg"))
        return result

    async def _handle_http(self, request: Request) -> Response:
        bot_config = self.bot_apps.get(request.url.parts[-1])
        if bot_config is None:
            return Response(403, content="Corresponding bot config not found")

        if (data := request.content) is not None:
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                return Response(400, content="Received non-JSON data")

        logger.debug(f"Received request: {data}")

        if data is not None:
            if not (bot := self.bots.get(bot_config.app_id)):
                return Response(404, content="Corresponding Bot instance not found")

            if event := self.json_to_event(data):
                bot = cast("Bot", bot)
                logger.debug("Prepare to handle event")
                task = asyncio.create_task(bot.handle_event(event))
                task.add_done_callback(self.tasks.discard)
                self.tasks.add(task)

        return Response(200)

    @classmethod
    def json_to_event(cls, json_data: Any) -> Optional[Event]:
        """将 json 数据转换为 Event 对象。
        参数:
            json_data: json 数据
            self_id: 当前 Event 对应的 Bot
        返回:
            Event 对象，如果解析失败则返回 None
        """
        if not isinstance(json_data, dict):
            return

        try:
            header = json_data["header"]
            event_type = header.get("eventType", "")
            if json_data.get("event", {}).get("message"):
                event_type += f".{json_data['event']['message']['chatType']}"
                if json_data["event"]["message"]["contentType"] == "tip":
                    event_type = "group.tip"

            models = cls.get_event_model(event_type)
            for model in models:
                try:
                    event = type_validate_python(model, json_data)
                    break
                except Exception:
                    logger.warning(f"Unsupported event: {json_data}")
                    return
            else:
                event = type_validate_python(Event, json_data)

            return event

        except Exception as e:
            logger.error(
                "<r><bg #f8bbd0>Failed to parse event. "
                f"Raw: {escape_tag(str(json_data))}</bg #f8bbd0></r>",
                e,
            )

    @classmethod
    def get_event_model(cls, event_name: str) -> list[type[Event]]:
        """根据事件名获取对应 `Event Model` 及 `FallBack Event Model` 列表，
        不包括基类 `Event`。
        """
        return [model.value for model in cls.event_models.prefixes(f".{event_name}")][
            ::-1
        ]
