from re import IGNORECASE
from traceback import format_exc
from typing import Dict,cast

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

from nonebot import require
from nonebot.plugin import on_command
from nonebot.adapters.onebot.v11 import Bot, Event
import asyncio
from ..async_executor import add_async_task
from ..epicfree.data_source import *
config = config_data["epicfree"]["time"]
hour, minute, second = config.split(" ")

test_command = on_command("1")
async def epic_subscribe():
    bot = get_bot()
    subscriber = await subscribe_helper()
    msg_list = await get_epic_free()
    try:
        assert isinstance(subscriber, Dict)
        for group in subscriber["群聊"]:
            await cast(Bot, bot).send_group_msg(
                    group_id=group, message=msg_list)
        #for group in subscriber["群聊"]:
        #    log_info("群")
        #    await bot.send_group_msg(group_id=group, messages=msg_list)
        #for private in subscriber["私聊"]:
        #    await bot.send_private_msg(user_id=private, messages=msg_list)
    except Exception as e:
        logger.error(f"Epic 限免游戏资讯定时任务出错 {e.__class__.__name__}\n{format_exc()}")

@test_command.handle()
async def handle_test_task(bot: Bot, event: Event):
    await epic_subscribe()
    
    #add_async_task(epic_subscribe())
    #await test_command.finish("任务已添加到队列")
