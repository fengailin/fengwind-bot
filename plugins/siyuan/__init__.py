from nonebot import on_command, on_message, get_bot
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent, MessageEvent
import re
import httpx
import mimetypes
from pathlib import Path
from .utils import *
from ..config import config_data, cache_path
from ..logger import log_info, log_exception, log_plugin,log_user
from ..async_executor import add_async_task
import nonebot
from nonebot.plugin import PluginMetadata
__plugin_meta__ = PluginMetadata(
    name='思源',
    description='思源',
    usage='',
    extra={'prefix': '核心', 'version': '1.0.3'}
)

async def collect_daily(data):
    files_count, files_dict = await listDocsByPath()
    name = str(datetime.datetime.now().strftime("%Y-%m-%d"))
    ctime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if name in files_dict:
        file_id = files_dict[name]
        previous_id = await getDoc(file_id)
        block_id = await insertBlock(data=ctime, previousID=previous_id)
        block_id2 = await insertBlock(data=data, previousID=block_id)
        return block_id2
    else:
        file_id = await createDoc(title=name)
        previous_id = await getDoc(file_id)
        block_id = await insertBlock(data=ctime, previousID=previous_id)
        block_id2 = await insertBlock(data=data, previousID=block_id)
        return block_id2


collect = on_message(priority=9999)

@collect.handle()
async def collect_handle(group_event: GroupMessageEvent, event: MessageEvent):
    if group_event.group_id in config_data['siyuan']['collect_group']:
        message = str(event.get_message())
        add_async_task(process_message(group_event, event, message))

async def process_message(group_event: GroupMessageEvent, event: MessageEvent, message: str):
    current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    pattern_image = r"\[CQ:image,file=(.*?)\]"
    match_image = re.search(pattern_image, message)

    bot = get_bot()

    if match_image:
        file_content = match_image.group(1)
        file_url = file_content.split(',')[0]
        image_response = httpx.get(file_url)
        content_type = image_response.headers.get('content-type', 'application/octet-stream')

        if image_response.status_code == 200:
            file_type = mimetypes.guess_extension(content_type)
            save_path = cache_path / 'siyuan' / 'image' / Path(f'collect_{current_time}{file_type}')
            save_path.parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, 'wb') as f:
                f.write(image_response.content)

            result = await upload(path=save_path, file=f, content_type=content_type)
            for original_name, uploaded_path in result.items():
                block_id = await collect_daily(f'![{original_name}]({uploaded_path})')
                await bot.send(event, f"✅上传成功\n🏞️ 图片 {original_name}\n⚓ 路径 {uploaded_path}\n✅插入成功\nℹ️id {block_id}")
    else:
        await handle_text_message(bot, event, message)

async def handle_text_message(bot, event: MessageEvent, message: str):
    files_count, files_dict = await listDocsByPath()
    name = str(datetime.datetime.now().strftime("%Y-%m-%d"))
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if name in files_dict:
        file_id = files_dict[name]
        previous_id = await getDoc(file_id)
        block_id = await insertBlock(data=current_time, previousID=previous_id)
        block_id2 = await insertBlock(data=message, previousID=block_id)
        await bot.send(event, f"✅插入成功\nℹ️id {block_id2}")
    else:
        file_id = await createDoc(title=name)
        previous_id = await getDoc(file_id)
        block_id = await insertBlock(data=current_time, previousID=previous_id)
        block_id2 = await insertBlock(data=message, previousID=block_id)
        await bot.send(event, f"✅插入成功\nℹ️id {block_id2}")

listdocs = on_command("列出文档", aliases={}, priority=10, block=True)
@listdocs.handle()
async def handle_function(event: GroupMessageEvent):
    files_count, file_names = await listDocsByPath()
    log_user(event, "列出文档")
    bot = get_bot()
    await bot.send(event, f"一共有{files_count}个文件, 分别名为{file_names}")

insert = on_command("插入", aliases={}, priority=10, block=True)
@insert.handle()
async def insert_handler(data: Message = CommandArg()):
    add_async_task(insert_data(data))

async def insert_data(data: Message):
    bot = get_bot()
    files_count, files_dict = await listDocsByPath()
    name = str(datetime.datetime.now().strftime("%Y-%m-%d"))
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if name in files_dict:
        file_id = files_dict[name]
        previous_id = await getDoc(file_id)
        block_id = await insertBlock(data=current_time, previousID=previous_id)
        block_id2 = await insertBlock(data=str(data), previousID=block_id)
        await bot.send(insert_handler, f"插入成功。子块id:{block_id2}")
    else:
        file_id = await createDoc(title=name)
        previous_id = await getDoc(file_id)
        block_id = await insertBlock(data=current_time, previousID=previous_id)
        block_id2 = await insertBlock(data=str(data), previousID=block_id)
        await bot.send(insert_handler, f"插入成功。子块id:{block_id2}")

create = on_command("创建文档", aliases={}, priority=10, block=True)
@create.handle()
async def create_doc_handler(event: GroupMessageEvent, name: Message = CommandArg()):
    add_async_task(create_doc(name, event))

async def create_doc(name: Message, event: GroupMessageEvent):
    bot = get_bot()
    files_count, files_dict = await listDocsByPath()
    if str(name).strip() in files_dict:
        file_id = files_dict[str(name).strip()]
        await bot.send(event, f"文档名重复了！已有文档id:{file_id}")
    elif str(name).strip() == "":
        await bot.send(event, "没名字创建什么文档？")
    else:
        await createDoc(title=str(name).strip())
        log_user(event, f"创建文档 {name}")
        await bot.send(event, f"成功创建文档：{name}")
