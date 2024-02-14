
from nonebot import on_command,on_message
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message,GroupMessageEvent,MessageEvent
import re
import httpx
import mimetypes
from pathlib import Path
from .utils import *
from ..config import siyuan,cache_path
from ..logger import *
__plugin_meta__ = nonebot.plugin.PluginMetadata(
    name='思源',
    description='思源',
    usage='',
    extra={'prefix':'核心','version': '1.0.3'}
)

async def collect_daily(data):
    # 偷懒，收集每天的小垃圾，屎山到时候再改了
    files_count, files_dict = await listDocsByPath()
    name = str(datetime.datetime.now().strftime("%Y-%m-%d"))
    ctime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if name in files_dict:
        file_id = files_dict[name]
        #await insert.send(f"文档名重复了！已有文档id:{file_id}")
        previous_id = await getDoc(file_id)
        block_id = await insertBlock(data=ctime,previousID=previous_id)
        block_id2 = await insertBlock(data=data,previousID=block_id)
        return block_id2
    else:
        name = str(datetime.datetime.now().strftime("%Y-%m-%d"))
            # 在这里添加创建文档的逻辑，比如调用工具函数创建文档
        file_id = await createDoc(title=name)
            #await insert.send(f"成功创建文档：{name} id:{file_id}")
        previous_id = await getDoc(file_id)
        block_id = await insertBlock(data=ctime,previousID=previous_id)
        block_id2 = await insertBlock(data=data,previousID=block_id)
        return block_id2


collect = on_message(priority=9999)
@collect.handle()
async def collect_handle(group_event: GroupMessageEvent,event: MessageEvent):
    if group_event.group_id in siyuan['collect_group']:
        current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        message = str(event.get_message())
        #await collect.send(str(event.get_message()))
        pattern_image = r"\[CQ:image,file=(.*?)\]"
        match_image = re.search(pattern_image, message)
        # 目前视频，链接，文件等都识别不了    
        if match_image:
            file_content = match_image.group(1)
            file_url = file_content.split(',')[0]
            #await collect.send(str(file_url))
            image_response = httpx.get(file_url)
            content_type = image_response.headers.get('content-type', 'application/octet-stream')
            #await collect.send(content_type)
            log_user(event,f"在收集箱群上传图片 url: {file_url}")
            if image_response.status_code == 200:
                file_type = mimetypes.guess_extension(content_type)
                # 保存图片到本地
                save_path = cache_path/ 'siyuan' / 'image' /Path(f'collect_{current_time}{file_type}')
                save_path.parent.mkdir(parents=True, exist_ok=True)
                with open(save_path, 'wb') as f:
                    f.write(image_response.content)
                # 下载步骤完成
                log_plugin(f"下载图片 url: {file_url}")
                result = await upload(path=save_path,file=f,content_type=content_type)
                # 调用异步上传接口上传图片
                
                for original_name, uploaded_path in result.items():
                    block_id = await collect_daily(f'![{original_name}]({uploaded_path})')
                    await collect.send(f"✅上传成功\n🏞️ 图片 {original_name}\n⚓ 路径 {uploaded_path}\n✅插入成功\nℹ️id {block_id}")
                
        else:
            #这些是文本处理
            files_count, files_dict = await listDocsByPath()
            name = str(datetime.datetime.now().strftime("%Y-%m-%d"))
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_user(event,f"在收集箱群发送了消息 : {message}")
            if name in files_dict:
                file_id = files_dict[name]
                #await insert.send(f"文档名重复了！已有文档id:{file_id}")
                previous_id = await getDoc(file_id)
                block_id = await insertBlock(data=current_time,previousID=previous_id)
                block_id2 = await insertBlock(data=message,previousID=block_id)
                await insert.send(f"✅插入成功\nℹ️id {block_id2}")
            else:
                name = str(datetime.datetime.now().strftime("%Y-%m-%d"))
                # 在这里添加创建文档的逻辑，比如调用工具函数创建文档
                file_id = await createDoc(title=name)
                #await insert.send(f"成功创建文档：{name} id:{file_id}")
                previous_id = await getDoc(file_id)
                block_id = await insertBlock(data=current_time,previousID=previous_id)
                block_id2 = await insertBlock(data=message,previousID=block_id)
                await insert.send(f"✅插入成功\nℹ️id {block_id2}")


listdocs = on_command("列出文档", aliases={}, priority=10, block=True)
@listdocs.handle()
async def handle_function(event:GroupMessageEvent):
    files_count, file_names = await listDocsByPath()
    log_user(event,f"列出文档")
    await listdocs.send(f"一共有{files_count}个文件,分别名为{file_names}")

insert = on_command("插入", aliases={}, priority=10, block=True)
@insert.handle()
async def insert_handler(data: Message = CommandArg()):
    files_count, files_dict = await listDocsByPath()
    name = str(datetime.datetime.now().strftime("%Y-%m-%d"))
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if name in files_dict:
        file_id = files_dict[name]
        #await insert.send(f"文档名重复了！已有文档id:{file_id}")
        previous_id = await getDoc(file_id)
        block_id = await insertBlock(data=current_time,previousID=previous_id)
        block_id2 = await insertBlock(data=str(data),previousID=block_id)
        log_user("siyuan")
        await insert.send(f"插入成功。子块id:{block_id2}")
    else:
        # 在这里添加创建文档的逻辑，比如调用工具函数创建文档
        file_id = createDoc()
        #await insert.send(f"成功创建文档：{name} id:{file_id}")
        previous_id = await getDoc(file_id)
        block_id = await insertBlock(data=current_time,previousID=previous_id)
        block_id2 = await insertBlock(data=str(data),previousID=block_id)
        await insert.send(f"插入成功。子块id:{block_id2}")

create = on_command("创建文档", aliases={}, priority=10, block=True)
@create.handle()
async def create_doc_handler(event:GroupMessageEvent,name: Message = CommandArg()):
    
    files_count, files_dict = await listDocsByPath()
    if str(name).strip() in (file for file in files_dict):
        file_id = files_dict[str(name)]
        await create.send(f"文档名重复了！已有文档id:{file_id}")
    elif str(name).strip() == "":
        await create.send("没名字创建什么文档？")
    else:
        # 在这里添加创建文档的逻辑，比如调用工具函数创建文档
        await createDoc(title=str(name))
        log_user(event,f"创建文档 {name}")
        await create.send(f"成功创建文档：{name}")