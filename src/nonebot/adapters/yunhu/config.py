from pydantic import BaseModel, Field


class YunHuConfig(BaseModel):
    """云湖适配器配置"""

    app_id: str = Field("")
    """机器人ID"""
    token: str = Field("")
    """机器人Token"""


class Config(BaseModel):

    yunhu_bots: list[YunHuConfig] = Field(default_factory=list)
