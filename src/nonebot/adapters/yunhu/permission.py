from nonebot.permission import Permission

from .event import GroupMessageEvent


async def _group_owner(event: GroupMessageEvent) -> bool:
    return event.event.sender.senderUserLevel == "owner"


async def _group_admin(event: GroupMessageEvent) -> bool:
    return event.event.sender.senderUserLevel == "administrator"


GROUP_OWNER: Permission = Permission(_group_owner)
"""匹配任意群聊群主消息类型事件"""
GROUP_ADMIN: Permission = Permission(_group_admin)
"""匹配任意群组管理员消息类型事件"""

__all__ = [
    "GROUP_OWNER",
    "GROUP_ADMIN",
]
