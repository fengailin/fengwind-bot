from nonebot.plugin import PluginMetadata
from nonebot.log import logger
from nonebot import get_driver, get_plugin_config
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from .config import Config

__plugin_meta__ = PluginMetadata(
    name="定时任务",
    description="APScheduler 定时任务插件",
    usage=(
        '声明依赖: `require("nonebot_plugin_apscheduler")\n'
        "导入调度器: `from nonebot_plugin_apscheduler import scheduler`\n"
        "添加任务: `scheduler.add_job(...)`\n"
    ),
    type="library",
    homepage="https://github.com/nonebot/plugin-apscheduler",
    config=Config,
    supported_adapters=None,
    extra={'prefix': '功能', 'version': '1'}
)


driver = get_driver()

plugin_config = get_plugin_config(Config)

scheduler = AsyncIOScheduler()
scheduler.configure(plugin_config.apscheduler_config)

async def _start_scheduler():
    if not scheduler.running:
        scheduler.start()

        logger.opt(colors=True).info("<c><u>apscheduler</u></c> | ✅ 计划程序已启动")
        #logger.opt(colors=True).info("<y>✅ 计划程序已启动</y>")


async def _shutdown_scheduler():
    if scheduler.running:
        scheduler.shutdown()

        logger.opt(colors=True).info("<c><u>apscheduler</u></c> | ✅ 计划程序已关闭")
        #logger.opt(colors=True).info("<y>✅ 计划程序已关闭</y>")
#if plugin_config.apscheduler_autostart:
#    driver.on_startup(_start_scheduler)
#    driver.on_shutdown(_shutdown_scheduler)
driver.on_startup(_start_scheduler)
driver.on_shutdown(_shutdown_scheduler)

#aps_logger = logging.getLogger("apscheduler")
#aps_logger.setLevel(plugin_config.apscheduler_log_level)
#aps_logger.handlers.clear()
#aps_logger.addHandler(LoguruHandler())
