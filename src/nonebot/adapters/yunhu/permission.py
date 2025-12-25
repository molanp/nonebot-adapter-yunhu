from nonebot.permission import Permission

from .event import GroupMessageEvent, InstructionMessageEvent, PrivateMessageEvent


async def _group_owner(event: GroupMessageEvent) -> bool:
    return event.event.sender.senderUserLevel == "owner"


async def _group_admin(event: GroupMessageEvent) -> bool:
    return event.event.sender.senderUserLevel == "administrator"

async def _private(event: PrivateMessageEvent) -> bool:
    return True

async def _group(event: GroupMessageEvent) -> bool:
    return True

async def _instruction(event: InstructionMessageEvent) -> bool:
    return True

GROUP_OWNER: Permission = Permission(_group_owner)
"""匹配任意群聊群主消息类型事件"""
GROUP_ADMIN: Permission = Permission(_group_admin)
"""匹配任意群组管理员消息类型事件"""
PRIVATE: Permission = Permission(_private)
"""匹配任意私聊消息类型事件"""
GROUP: Permission = Permission(_group)
"""匹配任意群聊消息类型事件"""
INSTRUCTION: Permission = Permission(_instruction)
"""匹配任意指令消息类型事件"""

__all__ = [
    "GROUP_OWNER",
    "GROUP_ADMIN",
    "PRIVATE",
    "GROUP",
    "INSTRUCTION",
]
