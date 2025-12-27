from enum import Enum
from typing import Literal, Optional
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
    data: Optional[DataDetail] = None
    """响应数据"""
    msg: str
    """返回信息"""


class CheckChatType(Enum):
    USER = 1
    """用户"""
    GROUP = 2
    """群组"""
    BOT = 3
    """机器人"""


class CheckChatInfoRecord(BaseModel):
    """
    聊天信息审核记录

    用于表示聊天信息的审核记录信息
    """

    id: int
    """记录ID"""
    chatId: str
    """对象ID"""
    chatType: CheckChatType
    """对象类型"""
    checkWay: str
    """审核方式"""
    reason: str
    """审核原因"""
    status: int
    """审核状态"""
    createTime: int
    """创建时间戳"""
    updateTime: int
    """更新时间戳"""
    delFlag: int
    """删除标记, 0表示未删除"""


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
    """机器人令牌"""
    link: str
    """链接"""
    introduction: str
    """机器人简介"""
    createBy: str
    """创建者ID"""
    createTime: int
    """创建时间戳"""
    headcount: int
    """使用人数"""
    private: int
    """是否私有 (0:公开, 1:私有)"""
    uri: str
    """机器人URI"""
    checkChatInfoRecord: CheckChatInfoRecord
    """聊天审核记录"""


class GroupBotRel(BaseModel):
    """群组与机器人关系"""

    id: int
    """关系ID"""
    groupId: str
    """群组ID"""
    botId: str
    """机器人ID"""
    delFlag: int
    """删除标记, 0表示未删除 """
    createTime: int
    """创建时间戳"""
    updateTime: int
    """更新时间戳"""
    bot: Bot
    """机器人信息"""


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
    data: Optional[BotInfoData] = None
    """响应数据内容"""
    msg: str
    """响应消息描述"""


class Group(BaseModel):

    id: int
    """群聊在数据库中的序列"""
    groupId: str
    """群聊ID"""
    name: str
    """群聊名称"""
    introduction: str
    """群聊简介"""
    createBy: str
    """创建者ID"""
    createTime: int
    """创建时间戳"""
    avatarId: int
    """群聊头像ID"""
    avatarUrl: str
    """群聊头像URL"""
    headcount: int
    """群人数"""
    readHistory: int
    """是否允许新成员获取以前的历史消息"""
    category: str
    """群聊分类"""
    uri: str
    """机器人URI"""
    groupBotRel: GroupBotRel
    """群组与机器人关系"""
    checkChatInfoRecord: CheckChatInfoRecord
    """聊天信息审核记录"""


class GroupInfoData(BaseModel):
    """
    响应数据模型

    包装群组信息的容器
    """

    group: Group
    """群组信息对象"""


class GroupInfo(BaseModel):
    """
    群组信息模型

    包含群组的基本信息
    """

    code: int
    """响应状态码 (1表示成功)"""
    data: Optional[GroupInfoData] = None
    """响应数据内容"""
    msg: str
    """响应消息描述"""


class UserMedal(BaseModel):
    """
    用户勋章模型

    包含用户勋章信息
    """

    id: int
    """勋章ID"""
    name: str
    """勋章名称"""
    desc: str
    """勋章描述"""
    imageUrl: str
    """勋章图像URL?"""
    sort: int
    """排序"""


class User(BaseModel):

    userId: str
    """用户ID"""
    nickname: str
    """用户名"""
    avatarUrl: str
    """用户头像URL"""
    registerTime: int
    """注册时间戳"""
    registerTimeText: str
    """注册时间文本"""
    onLineDay: int
    """在线天数"""
    continuousOnLineDay: int
    """连续在线天数"""
    medals: list[UserMedal]
    """用户勋章信息"""
    isVip: int
    """是否为VIP (0:否, 1:是)"""


class UserInfoData(BaseModel):
    """
    响应数据模型

    包装用户信息的容器
    """

    user: User
    """用户信息对象"""


class UserInfo(BaseModel):
    """
    用户信息模型

    包含用户基本信息
    """

    code: int
    """响应状态码 (1表示成功)"""
    data: Optional[UserInfoData] = None
    """响应数据内容"""
    msg: str
    """响应消息描述"""


class BoardData(BaseModel):
    """
    设置看板数据结果模型

    包含设置看板结果信息
    """

    successCount: int
    """成功设置的看板数量"""


class BoardResponse(BaseModel):
    """
    设置看板响应模型

    API返回的设置看板结果
    """

    code: int
    """响应状态码 (1表示成功)"""
    data: Optional[BoardData] = None
    """响应数据内容"""
    msg: str
    """响应消息描述"""
