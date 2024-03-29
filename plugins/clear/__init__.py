import nonebot
from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message,GroupMessageEvent,MessageEvent
from nonebot.permission import SuperUser
from ..config import cache_path
from ..logger import log_plugin,log_user,log_exception
import asyncio
import os
__plugin_meta__ = nonebot.plugin.PluginMetadata(
    name='清理',
    description='清理缓存',
    usage='',
    extra={'prefix':'插件','version': '1.1.0'}
)
clear = on_command("清理缓存", aliases={}, priority=10, block=True,permission=SuperUser)
@clear.handle()
async def _(event:GroupMessageEvent,data: Message = CommandArg()):
    log_user(event=event,operation="清理缓存")
    if not os.path.exists(cache_path):
        await clear.send('缓存目录不存在，无需清理。')
        return
    number = 0 
    # 清理缓存目录下的所有文件
    try:
        for root, dirs, files in os.walk(cache_path, topdown=False):
            for name in files:
                file_path = os.path.join(root, name)
                os.remove(file_path)
                number = number +1
            for name in dirs:
                dir_path = os.path.join(root, name)
                os.rmdir(dir_path)
                number = number +1
        log_plugin(f"清理缓存: {number} 个文件")
        await clear.send(f'清理完成\n共清理 {number} 个文件')
    except Exception as e:
        log_exception(f"清理缓存错误:{str(e)}")
    
