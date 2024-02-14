import nonebot
from nonebot import on_command, on_message
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent, MessageEvent
from .utils import *
from ..config import config_data
from urllib.parse import quote
from ..logger import log_exception,log_user
import asyncio

__plugin_meta__ = nonebot.plugin.PluginMetadata(
    name='网易云',
    description='网易云',
    usage='',
    extra={'prefix': '插件', 'version': '1.1.0'}
)

get_url = on_command("下歌", aliases={"dl"}, priority=10, block=True)

@get_url.handle()
async def _(event: GroupMessageEvent, data: Message = CommandArg()):
    try:
        data = str(data).strip()
        get_data = await get_song_url(data)
        log_user(event, f"获取歌曲id: {data} 地址")
        await get_url.send(get_data)
    except TypeError as e:
            await get_url.send(f"获取歌曲地址出错:{str(e)}\n请检查id是否存在")
    except Exception as e:
        await get_url.send(f"获取歌曲地址出错:{str(e)}")


playlist = on_command("歌单", aliases={"pl"}, priority=10, block=True)

@playlist.handle()
async def _(event: GroupMessageEvent, data: Message = CommandArg()):
    try:
        data = str(data).strip()
        get_data = await get_playlist_detail(data)
        log_user(event, f"获取歌单id: {data} 详情")
        await playlist.send(str(get_data))
    except TypeError as e:
            await get_url.send(f"获取歌单详情出错:{str(e)}\n请检查id是否存在")
    except Exception as e:
        await playlist.send(f"获取歌单详情出错:{str(e)}")


dl_playlist = on_command("下载歌单", aliases={"dlpl"}, priority=10, block=True)

@dl_playlist.handle()
async def _(event: GroupMessageEvent, data: Message = CommandArg()):
    try:
        data = str(data).strip()
        get_data, number = await get_playlist_detail(data)
        log_user(event, f"下载歌单: {data}")
        await dl_playlist.send(f"下载歌单id: {data}\n共{number}首 请耐心等待")

        start_time = time.time()
        man_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        def format_time(seconds):
            hours, remainder = divmod(seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            return f"{int(hours)}小时 {int(minutes)}分钟 {int(seconds)}秒"
        async def other():
            try:
                await playlist_handler(playlist_id=data, song_dict_list=list(get_data))
                end_time = time.time()
                elapsed_time = end_time - start_time
                formatted_elapsed_time = format_time(elapsed_time)
                base_url = config_data['cloudmusic']['webdav_base_url']
                url = base_url.replace("dav/", "")
                encoded_url = quote(url, safe="/:")
                await dl_playlist.send(
                    f"开始于{man_time}\n歌单id:{data}下载完成\n耗时{formatted_elapsed_time}\n地址 {encoded_url}{data}"
                )
            except TypeError as e:
                await get_url.send(f"下载歌单出错:{str(e)}\n请检查id是否存在")
            except Exception as e:
                
                await dl_playlist.send(f"下载歌单出错:{str(e)}")

        asyncio.ensure_future(other())
    except Exception as e:
        await dl_playlist.send(f"下载歌单出错:{str(e)}")