from re import IGNORECASE
from traceback import format_exc
from typing import Dict,cast
import nonebot
from nonebot import get_bot, get_driver, on_command, require,on_regex
from nonebot.log import logger
from nonebot.typing import T_State
from ..config import config_data
from nonebot.adapters.onebot.v11 import Bot, Event, Message  # type: ignore
from nonebot.adapters.onebot.v11.event import (  # type: ignore
        GroupMessageEvent,
        MessageEvent,
    )
from ..logger import log_info
require("apscheduler")
from ..apscheduler import scheduler  # noqa: E402

from .data_source import check_push, get_epic_free, subscribe_helper  # noqa: E402

from nonebot.plugin import PluginMetadata
__plugin_meta__ = PluginMetadata(
    name='喜加一',
    description='epic喜加一',
    usage='',
    extra={'prefix': '娱乐', 'version': '1.1.0'}
)


epic_matcher = on_command("free", aliases={'喜加一','epic'},priority=20)
"""查看是否有可用的epic免费游戏"""
@epic_matcher.handle()
async def query_handle(event: Event):
    free = await get_epic_free()
    if isinstance(event, GroupMessageEvent):
        await epic_matcher.send(free)  # type: ignore
    else:
        await epic_matcher.send(free)  # type: ignore


sub_matcher = on_regex(r"^喜(加|\+|＋)(一|1)(私聊)?订阅(删除|取消)?$", priority=10)


@sub_matcher.handle()
async def sub_handle(bot: Bot, event: MessageEvent, state: T_State):
    msg = event.get_plaintext()
    state["action"] = "删除" if any(s in msg for s in ["删除", "取消"]) else "启用"
    if isinstance(event, GroupMessageEvent):
        if (
            (event.sender.role not in ["admin", "owner"])
            and (event.get_user_id() not in bot.config.superusers)
        ) or "私聊" in msg:
            # 普通群员只会启用私聊订阅
            state["sub_type"] = "私聊"
        else:
            # 管理员用户、主人用户询问需要私聊订阅还是群聊订阅
            pass
    else:
        state["sub_type"] = "私聊"


@sub_matcher.got(
    "sub_type", prompt=Message.template("回复「私聊」{action}私聊订阅，回复其他内容{action}群聊订阅：")
)
async def subEpic(bot: Bot, event: MessageEvent, state: T_State):
    if any("私聊" in i for i in [event.get_plaintext().strip(), state["sub_type"]]):
        state["target_id"] = event.get_user_id()
        state["sub_type"] = "私聊"
    else:
        state["target_id"] = str(event.group_id)  # type: ignore
        state["sub_type"] = "群聊"
    msg = await subscribe_helper(state["action"], state["sub_type"], state["target_id"])
    await sub_matcher.finish(str(msg))


config = config_data["epicfree"]["time"]
hour, minute, second = config.split(" ")


@scheduler.scheduled_job("cron", hour=hour, minute=minute, second=second)
async def epic_subscribe():
    bot = get_bot()
    subscriber = await subscribe_helper()
    msg_list = await get_epic_free()
    if not check_push(msg_list):
        return
    try:
        assert isinstance(subscriber, Dict)
        for group in subscriber["群聊"]:
            log_info("群")
            await cast(Bot,bot).send_group_msg(group_id=group, messages=msg_list)
        for private in subscriber["私聊"]:
            await cast(Bot,bot).send_private_msg(user_id=private, messages=msg_list)
    except Exception as e:
        logger.error(f"Epic 限免游戏资讯定时任务出错 {e.__class__.__name__}\n{format_exc()}")
