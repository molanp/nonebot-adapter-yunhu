from pydantic import BaseModel, Field


class YunHuConfig(BaseModel):
    """云湖适配器配置"""

    app_id: str = Field("")
    """机器人ID"""
    token: str = Field("")
    """机器人Token"""
    use_stream: bool = Field(default=False)
    """是否使用流式回复"""


class Config(BaseModel):

    yunhu_bots: list[YunHuConfig] = Field(default_factory=list)
    """云湖机器人配置列表"""
