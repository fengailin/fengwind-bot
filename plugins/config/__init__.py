from pathlib import Path
import nonebot
from nonebot import on_command
from nonebot.permission import SuperUser
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent
from .utils import ConfigLoader,logger
from ..apscheduler import scheduler
import asyncio
# 插件元数据
from nonebot.plugin import PluginMetadata
__plugin_meta__ = PluginMetadata(
    name='设置工具',
    description='加载或保存插件所需设置',
    usage='',
    extra={'prefix': '核心', 'version': '1.3.0'}
)

# 获取程序根目录
root = Path.cwd()

# 定义路径常量
data_path = root / 'data'
cache_path = root / 'cache'
config_path = root / 'config'
resource_path = root / 'resource'
# 初始化配置加载器
config_loader = ConfigLoader(config_path)
config_data = {}

def reload_all_config():
    """
    重新加载所有配置文件
    """
    global config_data
    config_data = config_loader.load_all_configs()
    return True

# 初始加载配置
reload_all_config()

# 定义命令处理器
rl_all = on_command('重载', aliases={"rl"}, priority=10, block=True, permission=SuperUser)

@rl_all.handle()
async def reload_all_config_command(event: GroupMessageEvent):
    """
    处理重载配置命令
    """
    #await log_user(event=event, operation="重载配置")
    success = reload_all_config()

    if success:
        #await log_plugin("重载配置成功")
        
        number_of_configs = len(config_data)
        #logger.opt(colors=True).info(f"<c><u>config</u></c> | ✅ 重载 {number_of_configs} 个配置文件")
        await rl_all.send(f"成功重载 {number_of_configs} 个配置文件")
        if scheduler.running:
            scheduler.shutdown()
            #logger.opt(colors=True).info("✅ 计划程序已关闭")
            await asyncio.sleep(1)
        scheduler.start()
        logger.opt(colors=True).info("✅ 计划程序已重启")
    else:
        await rl_all.send("重载配置文件失败，请检查日志获取详细信息")
