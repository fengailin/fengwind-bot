from nonebot import on_command
from ..database import execute_sql
from nonebot.adapters.onebot.v11 import Message,GroupMessageEvent
from pathlib import Path
from ..config import config_data
import nonebot


from nonebot.plugin import PluginMetadata
__plugin_meta__ = PluginMetadata(
    name='权限',
    description='权限狗',
    usage='',
    extra={'prefix':'核心','version': '1.0.0'}
)
from nonebot import get_driver

config = get_driver().config
superusers = config.superusers
def check_permission(event:GroupMessageEvent,p_level=None,p_name=None):
    """
    检查权限
    :param event: 这个事件可获取用户qq和群号
    :param p_level: 如果存在的话需要权限等级达到
    :param p_name: 如果存在的话需要特定权限
    :return: True 或者 False
    """
    if event.user_id in superusers:
        return True
    # 超级用户可以在任何群使用
    else:
        if event.group_id in config_data['permission']['open_group']:

            # 不在开启群聊中无法使用
            return True
        else:
            return False

clear = on_command("权限测试", aliases={}, priority=10, block=True)
@clear.handle()
async def _(event:GroupMessageEvent):
    if not check_permission(event):
        await clear.send(f'失败')
        return
    await clear.send(f'成功')