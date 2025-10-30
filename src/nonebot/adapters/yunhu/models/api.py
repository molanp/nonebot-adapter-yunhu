from typing import Literal
from pydantic import BaseModel


class MsgInfo(BaseModel):
    msgId: str
    """消息ID"""
    recvId: str
    """	接收消息对象ID"""
    recvType: Literal["group", "user"]
    """接收对象类型"""


class DataDetail(BaseModel):
    messageInfo: MsgInfo


class SendMsgResponse(BaseModel):
    code: int
    """状态码， 1 表示成功"""
    data: DataDetail | None
    """响应数据"""
    msg: str
    """返回信息"""


class UpImgResponse(BaseModel):
    imageKey: str
    """图片的标签"""


class UpVideoResponse(BaseModel):
    videoKey: str
    """视频的标签"""


class UpFileResponse(BaseModel):
    fileKey: str
    """文件的标签"""


class UploadResponse(BaseModel):
    code: int
    """返回码"""

    data: UpImgResponse | UpVideoResponse | UpFileResponse | None
    """返回数据"""

    msg: str
    """返回信息"""


class CheckChatInfoRecord(BaseModel):
    """
    聊天信息检查记录模型

    用于表示机器人聊天信息的审核记录信息
    """

    id: int
    """某种神秘的ID"""

    chatId: str
    """对象ID (与botId相同)"""

    chatType: int
    """对象类型 (3表示机器人)"""

    checkWay: str
    """检查方式 (通常为空)"""

    reason: str
    """原因 (通常为空)"""

    status: int
    """状态 (0表示正常)"""

    createTime: int
    """创建时间戳"""

    updateTime: int
    """更新时间戳 (0表示未更新)"""

    delFlag: int
    """删除标志 (0表示未删除)"""


class Bot(BaseModel):
    """
    机器人信息模型

    包含机器人的基本信息、配置和状态
    """

    id: int
    """机器人在数据库中的序列"""

    botId: str
    """机器人唯一标识"""

    nickname: str
    """机器人昵称"""

    nicknameId: int
    """昵称ID"""

    avatarId: int
    """头像ID"""

    avatarUrl: str
    """头像URL地址"""

    token: str
    """访问令牌 (通常为空)"""

    link: str
    """机器人订阅接口URL (通常为空)"""

    introduction: str
    """机器人简介"""

    createBy: str
    """创建者标识"""

    createTime: int
    """创建时间戳"""

    headcount: int
    """使用人数"""

    private: int
    """是否私有 (0:公开, 1:私有)"""

    uri: str
    """API发送消息地址"""

    checkChatInfoRecord: CheckChatInfoRecord
    """聊天信息检查记录"""


class BotInfoData(BaseModel):
    """
    响应数据模型

    包装机器人信息的容器
    """

    bot: Bot
    """机器人信息对象"""


class BotInfo(BaseModel):
    """
    机器人信息响应模型

    API返回的完整机器人信息结构
    """

    code: int
    """响应状态码 (1表示成功)"""

    data: BotInfoData | None
    """响应数据内容"""

    msg: str
    """响应消息描述 (success表示成功)"""
