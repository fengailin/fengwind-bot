import nonebot
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, Event, MessageSegment
from .utils import generate_image
from nonebot.plugin import PluginMetadata
__plugin_meta__ = PluginMetadata(
    name='文字转图片',
    description='长文字转图片',
    usage='',
    extra={'prefix': '功能', 'version': '1.1.1'}
)
plugin_name = __plugin_meta__.name
plugin_version = __plugin_meta__.extra.get('version')
# 创建一个命令触发器，命令为“text2img”
text2img = on_command("2", aliases={"文字转图片"})

@text2img.handle()
async def handle_first_receive(bot: Bot, event: Event):
    args = str(event.get_message()).strip()


@text2img.got("text", prompt="请输入你想转换为图片的文字：")
async def handle_text(bot: Bot, event: Event):
    text = event.get_plaintext()

    # 生成图片
    image_path = generate_image(text)

    # 将图片发送给用户
    await text2img.finish(MessageSegment.image(image_path))
