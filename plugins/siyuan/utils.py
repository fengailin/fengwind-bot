import httpx
import datetime
import random
import string
from pathlib import Path
from ..config import config_data
from ..logger import log_info, log_exception, log_plugin

import tracemalloc
tracemalloc.start()

client = httpx.AsyncClient()

# 配置相关信息
host = config_data['siyuan']['host']
token = config_data['siyuan']['token']
notebook = config_data['siyuan']['notebook']
https = config_data['siyuan']['https']
address = f'https://{host}' if https else f'http://{host}'

# 请求头信息
headers = {
    'Host': host,
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
    'Accept': '*/*',
    'Accept-Language': 'zh-CN,en-US;q=0.7,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate',
    'Referer': address,
    'Origin': address,
    'DNT': '1',
    'Connection': 'keep-alive',
    'Authorization': f'Token {token}'
}

async def listDocsByPath():
    url = f"{address}/api/filetree/listDocsByPath"
    json = {"notebook": notebook, "path": "/"}
    try:
        response = await client.post(url=url, headers=headers, json=json)
        response.raise_for_status()
        res = response.json()
        files_info = res['data']['files']
        files_dict = {file_info['name'].replace('.sy', ''): file_info['id'] for file_info in files_info}
        return len(files_info), files_dict
    except Exception as e:
        log_exception(f"获取文档列表出错: {str(e)}")
        return 0, {}

async def createDoc(path=None, title=None, md=""):
    current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=7))
    random_id = f"{current_time}-{random_suffix}.sy"
    path = path or f"/{random_id}"
    title = title or datetime.datetime.now().strftime("%Y-%m-%d")

    url = f"{address}/api/filetree/createDoc"
    json = {"notebook": notebook, "path": path, "title": title, "md": md}
    try:
        response = await client.post(url=url, headers=headers, json=json)
        response.raise_for_status()
        res = response.json()
        file_id = res['data']['id']
        log_plugin(f"创建文档 id: {file_id}")
        return file_id
    except Exception as e:
        log_exception(f"创建文档出错: {str(e)}")
        return None

async def insertBlock(data, previousID=None, parentID=None, nextID=None):
    url = f"{address}/api/block/insertBlock"
    json = {"dataType": "markdown", "data": data}
    if previousID: json["previousID"] = previousID
    if parentID: json["parentID"] = parentID
    if nextID: json["nextID"] = nextID

    try:
        response = await client.post(url=url, headers=headers, json=json)
        response.raise_for_status()
        res = response.json()
        block_id = res['data'][0]['doOperations'][0]['id']
        log_plugin(f"插入块 id: {block_id}")
        return block_id
    except Exception as e:
        log_exception(f"插入块出错: {str(e)}")
        return None

async def getDoc(id, startID="", endID=""):
    url = f"{address}/api/filetree/getDoc"
    json = {"id": id, "startID": startID, "endID": endID}
    try:
        response = await client.post(url=url, headers=headers, json=json)
        response.raise_for_status()
        res = response.json()
        blocks = res['data'].get('content')
        if blocks:
            block_id = blocks.split('data-node-id="')[-1].split('"')[0]
            return block_id
        else:
            log_exception("获取文档出错: 没有内容")
            return None
    except Exception as e:
        log_exception(f"获取文档出错: {str(e)}")
        return None

async def upload(path: Path, file, content_type):
    url = f"{address}/api/asset/upload"
    files = {'file': (path, file, content_type)}
    try:
        response = await client.post(url=url, headers=headers, files={'file[]': (path.name, path.open('rb'))}, json={'assetsDirPath': '/assets/'})
        response.raise_for_status()
        res = response.json()
        err_files = res['data']['errFiles']
        succ_map = res['data']['succMap']
        if not err_files:
            for original_name, uploaded_path in succ_map.items():
                log_plugin(f"上传文件 路径: {uploaded_path}")
            return succ_map
        else:
            log_exception(f"上传文件出错: {err_files}")
            return None
    except Exception as e:
        log_exception(f"上传文件出错: {str(e)}")
        return None

