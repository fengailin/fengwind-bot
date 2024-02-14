from ..config import siyuan
import httpx
import datetime
import random
import string
from pathlib import Path
from ..logger import *

import tracemalloc
tracemalloc.start()

client = httpx.AsyncClient()


host = siyuan['host']
token = siyuan['token']
notebook = siyuan['notebook']
https = siyuan['https']
if https == True:
    address = f'https://{host}'
else:
    address = f'http://{host}'

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
    'Authorization': 'Token '+token
}

async def listDocsByPath():
    try:
        # 列出笔记本列表
        url = f"{address}/api/filetree/listDocsByPath"
        json = {"notebook": notebook, "path": "/"}
        response = await client.post(url=url, headers=headers, json=json)
        res = response.json()
        #log_info(res)
        files_count = len(res['data']['files'])
        files_info = res['data']['files']
        files_dict = {}
        for file_info in files_info:
            file_name = file_info['name'].replace('.sy', '')
            file_id = file_info['id']
            files_dict[file_name] = file_id
        return files_count, files_dict
    except Exception as e:
        log_exception(f"获取文档列表出错: {str(e)}")
        return None

async def createDoc(path=None, title=None, md=""):
    try:
        current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=7))
        random_id = f"{current_time}-{random_suffix}.sy"
        # 创建文档
        if title == None:
            title = datetime.datetime.now().strftime("%Y-%m-%d")
        if path == None:
            path = "/"+random_id
        url = f"{address}/api/filetree/createDoc"
        json = {"notebook": notebook, "path": path, "title": title, "md": md}
        response = await client.post(url=url, headers=headers, json=json)
        res = response.json()
        log_info(res)
        file_id = res['data']['id']
        
        log_plugin(f"创建文档 id: {file_id}")
        return file_id
    except Exception as e:
        log_exception(f"创建文档出错: {str(e)}")
        return None

async def insertBlock(data, previousID=None, parentID=None, nextID=None):
    try:
        # 插入块
        url = f"{address}/api/block/insertBlock"
        json = {"dataType": "markdown", "data": data}
        # 根据提供的ID参数添加到请求中
        if previousID is not None:
            json["previousID"] = previousID
        if parentID is not None:
            json["parentID"] = parentID
        if nextID is not None:
            json["nextID"] = nextID
        response = await client.post(url=url, headers=headers, json=json)
        res = response.json()
        #log_info(res)
        block_id = res['data'][0]['doOperations'][0]['id']
        log_plugin(f"插入块 id: {block_id}")
        return block_id
    except Exception as e:
        log_exception(f"插入块出错: {str(e)}")
        return None

async def getDoc(id, startID="", endID=""):
    try:
        url = f"{address}/api/filetree/getDoc"
        json = {"id": id, "startID": startID, "endID": endID}
        response = await client.post(url=url, headers=headers, json=json)
        res = response.json()
        #log_info(res)
        blocks = res['data'].get('content')
        if blocks:
            # 获取文档中最后一个块的 data-node-id
            block_id = blocks.split('data-node-id="')[-1].split('"')[0]
        
            return block_id
        else:
            log_exception(f"获取文档出错: 没有内容")
            return None
    except Exception as e:
        log_exception(f"获取文档出错: {str(e)}")
        return None

async def upload(path: Path, file, content_type):
    try:
        url = f"{address}/api/asset/upload"
        files = {'file': (path, file, content_type)}
        files = {'file[]': (path.name, path.open('rb'))}
        json = {'assetsDirPath': '/assets/'}
        response = await client.post(url=url, headers=headers, files=files, json=json)
        res = response.json()
        #log_info(f"上传返回 {res}")
        err_files = res['data']['errFiles']
        succ_map = res['data']['succMap']
        if not err_files:
            # 上传成功
            for original_name, uploaded_path in succ_map.items():
                log_plugin(f"上传文件 路径: {uploaded_path}")
            return succ_map
        else:
            # 上传失败，返回错误信息或其他适当的处理
            log_exception(f"上传文件出错: {err_files}")
            return None
    except Exception as e:
        log_exception(f"上传文件出错: {str(e)}")
        return None
