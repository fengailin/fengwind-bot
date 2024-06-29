import asyncio
import itertools
from nonebot import get_driver, require
from nonebot.plugin import PluginMetadata
from ..logger import log_plugin, log_exception  # 确保这些导入是正确的
import inspect, os
import traceback

__plugin_meta__ = PluginMetadata(
    name="Async Task Queue",
    description="提供一个异步任务队列，其他插件可以往该队列中添加任务",
    usage="调用 add_async_task 函数添加任务",
    extra={'prefix': '功能', 'version': '1.0.0'}
)

global_task_queue = asyncio.Queue()
task_id_counter = itertools.count(1)  # 用于生成唯一的任务ID

async def task_worker():
    while True:
        task_id, plugin_name, task_name, task = await global_task_queue.get()
        try:
            
            await log_plugin(f"任务开始 | ID: {task_id} | 名称: {task_name} | 模块: {plugin_name}")
            if asyncio.iscoroutine(task):
                await task
            else:
                await asyncio.to_thread(task)
            await log_plugin(f"任务执行成功 | ID: {task_id} | 名称: {task_name} | 模块: {plugin_name}")
        except Exception as e:
            log_exception(f"任务执行出错 | ID: {task_id} | 名称: {task_name} | 模块: {plugin_name} | 错误: {traceback.format_exc()}\n")
        finally:
            global_task_queue.task_done()

# 在插件加载时启动任务工作协程
driver = get_driver()

@driver.on_startup
async def startup():
    asyncio.create_task(task_worker())

def add_async_task(task):
    task_id = next(task_id_counter)
    current_frame = inspect.currentframe()
    caller_module = inspect.getmodule(current_frame.f_back)
        
    # 从模块信息中获取插件名
    plugin_name = os.path.basename(os.path.dirname(caller_module.__file__))
    
    #caller_frame = inspect.currentframe().f_back  # 获取调用者的栈帧
    #task_name = caller_frame.f_code.co_name
    if hasattr(task, '__name__'):
        task_name = task.__name__
    else:
        task_name = "[bug]"
    global_task_queue.put_nowait((task_id, plugin_name, task_name, task))
