
from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Bot, Event, MessageSegment,Message

from ..to_image import generate_image
from nonebot.plugin import PluginMetadata

from .handler import *

__plugin_meta__ = PluginMetadata(
    name='帮助',
    description='帮助',
    usage='',
    extra={'prefix':'功','version': '1.1.0'}
)


# 创建一个NoneBot命令
search_plugins = on_command("help", aliases={"帮助"}, priority=5)
"""提供所有插件的帮助"""


@search_plugins.handle()
async def handle_first_receive(bot: Bot, event: Event, arg : Message = CommandArg()):
    # 定义存储插件和注释的字典
    if arg:
        plugin_name = str(arg)
        output = await get_single_plugin_detail(arg)
        if output ==None:
            await search_plugins.finish(f"未找到插件 {plugin_name} 的帮助信息。")
        else:
            description_text = f"{plugin_name} 插件的帮助。格式:\n[命令名] / [命令别名]\n└ [命令描述及帮助]"
            image = generate_image(title=f"{plugin_name} 帮助", description=description_text, text=output)
            await search_plugins.finish(MessageSegment.image(image))
    else:
        output = await get_all_plugins_detail()
        description_text = "机器人的所有插件的帮助。格式:\n[插件名]\n├ [命令名] / [命令别名]\n└ [命令描述及帮助]"
        image = generate_image(title="帮助大全", description=description_text, text=output)
    # 发送消息
        await search_plugins.finish(MessageSegment.image(image))
