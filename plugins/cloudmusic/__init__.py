import os
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, Event
from .pyncm_async import apis
from .pyncm_async import LoadSessionFromString
from ..config import config_path
music = on_command("下载歌曲")

# 读取登录态
async def load_login_session():
    path = config_path / 'ncm.txt'
    with open(path, "r") as file:
        session_data = file.read().strip()
    LoadSessionFromString(session_data)

@music.handle()
async def handle_first_receive(bot: Bot, event: Event):
    args = str(event.get_message()).strip()  # 获取用户输入的内容
    if args:
        await music.send("正在搜索歌曲...")
        await download_music(args)

async def download_music(song_id: str):
    # 加载登录态
    await load_login_session()
    
    # 获取歌曲音频信息
    audio_info = await apis.track.GetTrackAudio(song_id)
    
    if audio_info and audio_info['data']:
        url = audio_info['data'][0]['url']
        await music.send(f"歌曲下载链接：{url}")
    else:
        await music.send("未找到音频链接，可能需要重新登录。")
