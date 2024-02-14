from .utils import load_yaml_dict,load_yaml_single
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
mysql_config = load_yaml_dict(config_path / 'mysql.yml') 
# Mysql数据库配置文件
opengroup = load_yaml_single('OpenGroup',config_path / 'group.yml')
# 开启机器人的群聊
siyuan = load_yaml_dict(config_path / 'siyuan.yml')
# 思源笔记配置文件
logger = load_yaml_dict(config_path / 'logger.yml')

cloudmusic = load_yaml_dict(config_path / 'cloudmusic.yml')