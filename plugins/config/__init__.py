from .utils import load_yaml_dict,load_yaml_single
from nonebot import on_command
from nonebot.permission import SuperUser
from nonebot.adapters.onebot.v11 import Message,GroupMessageEvent
from pathlib import Path
import nonebot


__plugin_meta__ = nonebot.plugin.PluginMetadata(
    name='设置工具',
    description='加载或保存插件所需设置',
    usage='',
    extra={'prefix':'核心','version': '2023-06-30'}
)
root = Path.cwd()
# 获取程序根目录

data_path = root / 'data'
cache_path =  root / 'cache'
config_path = root / 'config'
#下面是各种配置常量
config_data = {}

def reload_all_config():
    global config_data
    #log_plugin("重载配置文件成功")
    # 重新加载所有配置文件
    config_data['mysql_config'] = load_yaml_dict(config_path / 'mysql.yml') 
    config_data['permission'] = load_yaml_dict(config_path / 'permission.yml')
    config_data['siyuan'] = load_yaml_dict(config_path / 'siyuan.yml')
    config_data['logger'] = load_yaml_dict(config_path / 'logger.yml')
    config_data['cloudmusic'] = load_yaml_dict(config_path / 'cloudmusic.yml')

    # 处理其他逻辑，例如更新插件配置等

    # 返回 True 表示重新加载成功
    return True
reload_all_config()

rl_all = on_command('重载', aliases={"rl"}, priority=10, block=True,permission=SuperUser)
@rl_all.handle()
async def reload_all_config_command(event:GroupMessageEvent):
    #log_user(event=event,operation="重载配置文件")
    success = reload_all_config()
    from ..logger import log_plugin,log_user
    log_user(event=event,operation="重载配置")

    if success == True:
        log_plugin("重载配置成功")
        number = len(config_data)
        await rl_all.send(f"成功重载 {number} 个配置文件")
    else:
        await rl_all.send(config_data)