from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.plugin import PluginMetadata
from nonebot import logger, require, on_command

from .srcode_data_source import get_code_msg


__plugin_meta__ = PluginMetadata(
    name="StarRailCode",
    description="崩坏：星穹铁道前瞻直播兑换码",
    usage="""\
查询兑换码: srcode
""",
    extra={
        "version": "1.0",
        "srhelp": """\
查询兑换码: srcode
""",
    },
)

srcode = on_command("srcode", aliases={"星铁兑换码"})


@srcode.handle()
async def _(event: GroupMessageEvent):
    try:
        codes = await get_code_msg()
    except Exception as e:
        logger.opt(exception=e).error("获取前瞻兑换码失败")
        codes = "获取前瞻兑换码失败"
    msg = str(codes)
    await srcode.finish(msg)
