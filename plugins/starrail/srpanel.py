from datetime import datetime, timedelta

from nonebot.log import logger
from nonebot.params import RegexDict
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent,MessageSegment
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata
from nonebot import require, on_regex, get_driver, on_command

from ..apscheduler import scheduler

from .srres import srres
from .srbind import get_user_srbind
from ..logger import log_info,log_warning

from .srpanel_get_img import get_srpanel_img
from .srpanel_model import (
    ScoreFile,
    update_srpanel,
    update_score_file,
    get_srpanel_player,
    get_srpanel_character,
)

__plugin_meta__ = PluginMetadata(
    name="StarRailPanel",
    description="崩坏：星穹铁道角色面板查询",
    usage="""\
更新面板: srpu
查看面板: xxxx面板
""",
    extra={
        "version": "1.0",
        "srhelp": """\
更新面板: srpu / 更新角色面板
查看面板: [u]xxxx[/u]面板
""",
    },
)

score: ScoreFile = {}

driver = get_driver()


@driver.on_startup
async def _():
    global score
    score_file = await update_score_file()
    if score_file:
        score = score_file
        log_info("遗器评分标准加载完成")
    else:
        logger.error("遗器评分标准加载失败，请检查网络连接和插件配置")
    scheduler.add_job(update_score_file, "cron", day=1, id="srscore_update")
    log_info("遗器评分标准自动更新任务已添加")


srsupdate = on_command(
    "srsupdate", aliases={"更新星铁评分标准"}, permission=SUPERUSER, block=True
)


@srsupdate.handle()
async def _():
    global score
    msg = "开始更新遗器评分标准"
    await srsupdate.send(msg)
    score_file = await update_score_file()
    if not score_file:
        msg = "遗器评分标准更新失败，请检查网络连接和插件配置"
    else:
        score = score_file
        msg = "遗器评分标准更新完成"
    await srsupdate.finish(msg)


srpu = on_command(
    "srpu",
    aliases={
        "更新角色面板",
        "更新星铁面板",
        "更新星铁角色面板",
        "星铁更新面板",
        "星铁更新角色面板",
    },
    priority=2,
    block=False,
)
srpanel = on_regex(r"(?P<name>\w{1,10})面板$", priority=9, block=False)


@srpu.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    user_list = await get_user_srbind(bot.self_id, event.get_user_id())
    if not user_list:
        msg = "未绑定SRUID，请使用`sruid [uid]`绑定或`srqr`扫码绑定"
        await srpu.finish(msg)
    sr_uid = user_list[0].sr_uid
    log_info(f"开始更新SRUID『{sr_uid}』角色面板")
    msg = f"开始更新SRUID『{sr_uid}』角色面板"
    await srpu.send(msg)
    updated = await update_srpanel(bot.self_id, event.get_user_id(), sr_uid)
    if updated:
        msg = f"成功更新以下角色面板\n{updated}"
    else:
        msg = "角色面板更新失败，请稍后重试"
    await srpu.finish(msg)


@srpanel.handle()
async def _(bot: Bot, event: GroupMessageEvent, regex_dict: dict = RegexDict()):
    name: str = regex_dict["name"] or ""
    if not name:
        await srpanel.finish()
    if name not in srres.NicknameRev:
        await srpanel.finish()
    cid = srres.NicknameRev[name]
    if len(cid) != 4:
        await srpanel.finish()
    user_list = await get_user_srbind(bot.self_id, event.get_user_id())
    if not user_list:
        msg = "未绑定SRUID，请使用`sruid [uid]`绑定或`srqr`扫码绑定"
        await srpanel.finish(msg)
    sr_uid = user_list[0].sr_uid
    if str(cid).startswith("80"):
        cid = "8000"
    info = await get_srpanel_character(bot.self_id, event.get_user_id(), sr_uid, cid)
    if info is None or (
        info.time is not None
        and datetime.strptime(info.time, "%Y-%m-%d %H:%M:%S")
        < datetime.now() - timedelta(days=10)
    ):
        # 无角色信息或距离上次更新超过十天时自动更新一次
        await update_srpanel(bot.self_id, event.get_user_id(), sr_uid)
        info = await get_srpanel_character(
            bot.self_id, event.get_user_id(), sr_uid, cid
        )

    name = srres.ResIndex["characters"][cid].name if cid != "8000" else "开拓者"

    if info is None:
        msg = f"未找到『{name}』的面板，请放置在游戏展柜中五分钟后使用`srpu`更新面板"
        await srpanel.finish(msg)

    # 绘图操作前提示信息
    msg = f"正在绘制『{name}』的面板，请耐心等待"
    await srpanel.send(msg)

    player_info = await get_srpanel_player(bot.self_id, event.get_user_id(), sr_uid)
    if player_info is not None:
        try:
            global score
            img = await get_srpanel_img(player_info, info, score)
        except Exception as e:
            img = None
            await log_warning(f"绘图出错：{e}")
            logger.exception(e)
    else:
        img = None
    if img is None:
        msg ="绘图出错，请尝试使用`srpu`更新面板"
        await srpanel.finish(msg)
    await srpanel.finish(MessageSegment.image(img))
