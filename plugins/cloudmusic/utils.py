import hashlib,base64
from time import sleep
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from binascii import b2a_hex
import json,re,asyncio,time,datetime
import eyed3

from collections import deque
from pathlib import Path
import requests,httpx
from .apis import *
from ..logger import *
from ..config import cache_path,cloudmusic

import asyncio
import aiofiles
import traceback

save_path = cache_path/ 'cloudmusic' 
EAPI_KEY = b"e82ckenh8dichen8"
EAPI_CRYPTOR = AES.new(EAPI_KEY, AES.MODE_ECB)
def eapi_encrypt(path, params):
    try:
        """eapi
        接口参数加密
        :param str path: 请求的路径
        :param params: 请求参数
        :return str: 加密结果
        """
    # 将字符串转换为字节串
        path_bytes = path.encode()

        params = json.dumps(params, separators=(',', ':')).encode()
        sign_src = b'nobody' + path_bytes + b'use' + params + b'md5forencrypt'
        m = hashlib.md5()
        m.update(sign_src)
        sign = m.hexdigest()
        aes_src = path_bytes + b'-36cd479b6b5-' + params + b'-36cd479b6b5-' + sign.encode()
        pad = 16 - len(aes_src) % 16
        aes_src = aes_src + bytearray([pad] * pad)
        crypt = AES.new(b'e82ckenh8dichen8', AES.MODE_ECB)
        ret = crypt.encrypt(aes_src)
        params_enc = b2a_hex(ret).upper()
    #返回params可以直接用！
        return params_enc
    except Exception as e:
        log_exception(f"加密出错: {str(e)}\n{traceback.format_exc()}\n{traceback.format_exc()}")
        return None
def eapi_decrypt(params):
    try:

    #网易云params解密
        message = unpad(EAPI_CRYPTOR.decrypt(base64.b16decode(params)), 16).decode()
        path, json_val, hash_val = message.split("-36cd479b6b5-")
        return path, json.loads(json_val)
    except Exception as e:
        log_exception(f"解密params出错: {str(e)}\n{traceback.format_exc()}\n{traceback.format_exc()}")
        return None
def data_decrypt(data):
    try:
    #网易云data解密
        data = unpad(EAPI_CRYPTOR.decrypt(data), 16).decode()
        return json.loads(data)
    except Exception as e:
        log_exception(f"解密data出错: {str(e)}\n{traceback.format_exc()}\n{traceback.format_exc()}")
        return None
def get_epath(provided_path):
    #路径转换
    modified_path = provided_path.replace('/api/', '', 1)
    full_url = f"https://interface.music.163.com/eapi/{modified_path}"
    return full_url

cookies = cloudmusic['cookies']
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36 Chrome/91.0.4472.164 NeteaseMusicDesktop/3.0.6.202460',
    'mconfig-info': '{"IuRPVVmc3WWul9fT":{"version":501760,"appver":"3.0.6.202460"}}',
    'origin': 'orpheus://orpheus',
    'sec-ch-ua': '"Chromium";v="91"',
    'sec-ch-ua-mobile': '?0',
    'sec-fetch-site': 'cross-site',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'accept-language': 'en-US,en;q=0.9',
    'Content-Type': 'application/x-www-form-urlencoded',
}
header = cloudmusic['header']
async def request(path,params):
    try:
        
    #请求，路径和参数
        params_enc = eapi_encrypt(path,params)
        data = {
    'params': params_enc,}
        url = get_epath(path)
        log_plugin(f"请求地址: {url}")
        response = requests.post(url, cookies=cookies, headers=headers, data=data)
        data_hex = response.content
        data_dec = data_decrypt(data_hex)
        return data_dec
    except Exception as e:
        log_exception(f"请求出错: {str(e)}\n{traceback.format_exc()}\n{traceback.format_exc()}")
        return None

async def get_song_url(song_id):
    song_id = int(song_id)
    try:
        params = { 'e_r': True,
  'encodeType': 'mp3',
  'header': header,
  'ids': [song_id],
  'immerseType': 'c51',
  'level': 'exhigh',
  'trialMode': '-1'}
        data = await request(song_url,params)
        song_data = data.get('data', [])[0]['url']
        song_data = re.sub(r'(\?|&)authSecret=[^&]*(&|$)', r'\1', song_data)
        log_plugin(f"获取歌曲id: {song_id} 的地址: {song_data}")
    #log_info(song_data)
        return song_data
    except Exception as e:
        log_exception(f"获取歌曲地址出错: {str(e)}\n{traceback.format_exc()}\n{traceback.format_exc()}")
        return None
async def get_playlist_detail(playlist_id):
    try:
        params = {
 'checkToken': '',
  'e_r': True,
  'header': header,
  "osver":"Microsoft-Windows-10-Home-China-build-22000-64bit","X-antiCheatToken":"",
  'id': playlist_id,
  'n': '1000',
  's': '0'}
        data = await request(playlist_detail,params)
        tracks = data.get('playlist', {}).get('tracks', [])  
    # 获取 tracks 列表

        #log_info(tracks)
        id_string = ""
        name_string = ""
        result = []

        for track in tracks:
            name = track['name']
            track_id = track['id']
            artists = ','.join(artist['name'] for artist in track['ar'])
            picUrl = track['al']['picUrl']
            album = track['al']['name']
            #size = track['size']
            name_string += f"{artists} - {name}\n"
            id_string += str(track_id) + '\n'
            #result.append({track_id: f"{artists} - {name}"})
            result.append({track_id: [f"{artists} - {name}",f"{name}", f"{artists}",f"{picUrl}",f"{album}"]})
            #文件名
        #log_info(f"名字 {name} id {track_id}")
        #log_info(result)
        log_plugin(f"获取歌单id: {playlist_id} 的详情")
        return list(result),len(list(result))
    except Exception as e:
        log_exception(f"获取歌单详情出错: {str(e)}\n{traceback.format_exc()}\n{traceback.format_exc()}")
        return None

async def upload_playlist(file_name, path, playlist_id):
    try:
        
            # 等待文件写入完成后再进行上传

        base_url = cloudmusic['webdav_base_url']
        webdav_username = cloudmusic['webdav_username']
        webdav_password = cloudmusic['webdav_password']
        remote_path = f"{base_url}{playlist_id}/"  # 替换为实际的远程路径
        url = f"{remote_path}{file_name}.mp3"  # 替换为实际的远程路径
        headers_upload = {
            'Authorization': f'Basic {base64.b64encode(f"{webdav_username}:{webdav_password}".encode()).decode()}',
            'Content-Type': 'application/octet-stream'
        }
        async with httpx.AsyncClient() as client:  # 创建一个异步client
            mkcol_response = await client.request('MKCOL', remote_path, headers=headers_upload)

        # 如果目录已存在或者成功创建，则继续上传文件
        if mkcol_response.status_code == 201 or mkcol_response.status_code == 405:
            async with aiofiles.open(path, 'rb') as local_file:
                file_content = await local_file.read()
            async with httpx.AsyncClient() as client:  # 创建一个异步client
                response = await client.put(url=url, headers=headers_upload, content=file_content,timeout=None)
                if response.status_code == 201 or response.status_code == 302:
                    log_plugin(f"上传歌单歌曲成功: {path}")
                else:
                    log_exception(f"上传歌单歌曲失败: {path}\n{response}")

    except Exception as e:
        log_exception(f"上传歌单歌曲出错: {str(e)}\n{traceback.format_exc()}\n{traceback.format_exc()}")
        
async def download_playlist(playlist_id,song_id, file_name,name,artists="",picurl="",album="", ):
    try:
        new_filepath = save_path /  f'{playlist_id}' /f"{file_name}.mp3"
        photo = httpx.get(picurl)
        if new_filepath.exists() and new_filepath.stat().st_size > 3 * 1024 * 1024:
            
        
            log_plugin(f"下载歌单歌曲 {file_name} 已存在且大小大于3MB，跳过下载流程")
            
        else:
            new_filepath.parent.mkdir(parents=True, exist_ok=True)
            song_url = await get_song_url(song_id)
            response = httpx.get(song_url)
        
            if response.status_code == 200:
            # 构建新的文件路径和文件名
            
            
            
                async with aiofiles.open(new_filepath, 'wb') as f:
                    await f.write(response.content)
                log_plugin(f"下载歌单歌曲路径: {new_filepath}")
        while True:
            initial_size = os.path.getsize(new_filepath)
            await asyncio.sleep(0.5)
            current_size = os.path.getsize(new_filepath)
            if current_size == initial_size:
                audiofile = eyed3.load(new_filepath)

                # 设置歌手、标题和专辑信息
                audiofile.tag.artist = f"{artists}"
                audiofile.tag.title = f"{name}"
                audiofile.tag.album = f"{album}"

                # 添加图片
                # 你需要将图片文件转换为二进制数据并设置它的MIME类型
                # 这里假设你有一张名为"album_cover.jpg"的图片
                if photo.status_code == 200:
                    photopath = save_path /  f'{playlist_id}' /f"{file_name}.jpg"
                    photopath.parent.mkdir(parents=True, exist_ok=True)
                    async with aiofiles.open(photopath, 'wb') as f:
                        await f.write(photo.content)
                        with open(photopath, "rb") as image_file:
                            image_data = image_file.read()
                        audiofile.tag.images.set(3, image_data, "image/jpeg", u"Album Cover")
# 保存修改后的MP3文件
                audiofile.tag.save()

                log_plugin(f"已成功添加 {file_name} 的元信息")
                break

        await upload_playlist(file_name=file_name,path=new_filepath,playlist_id=playlist_id)
        #注释这一行即可只添加元信息

    except Exception as e:
        log_exception(f"下载歌单歌曲出错: {str(e)}\n{traceback.format_exc()}\n{traceback.format_exc()}")

async def playlist_handler(song_dict_list, playlist_id):
    try:
        log_plugin(f"开始歌单id: {playlist_id}的处理")
        #log_plugin(f"song_dict_list 类型: {type(song_dict_list)}, 内容: {song_dict_list}")
        for song_dict in song_dict_list:
            #log_plugin(f"song_dict 类型: {type(song_dict)}, 内容: {song_dict}")
            #song_dict = dict(song_di)

            for id, other_info in song_dict.items():
                song_id = id
                file_name = other_info[0]
                name = other_info[1]
                artists = other_info[2]
                picurl = other_info[3]
                album = other_info[4]
                #log_plugin(f"song {song_id} {song_title}")
                await download_playlist(song_id=song_id, playlist_id=playlist_id,file_name=file_name,name=name,artists=artists,album=album,picurl=picurl)
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_plugin(f"歌单id: {playlist_id}的处理完成")
        return True
    except Exception as e:
        log_exception(f"歌单处理出错: {str(e)}\n{traceback.format_exc()}\n{traceback.format_exc()}")