#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import nonebot
from nonebot.adapters.onebot.v11 import Adapter as ONEBOT_V11Adapter


# 自定义日志器
# 
# from nonebot.log import logger, default_format
# logger.add("error.log",
#            rotation="00:00",
#            diagnose=False,
#            level="ERROR",
#            format=default_format)

# You can pass some keyword args config to init function
nonebot.init()
app = nonebot.get_asgi()

driver = nonebot.get_driver()
driver.register_adapter(ONEBOT_V11Adapter)


# 不要乱编辑这个文件
# As an alternative, you should use command `nb` or modify `pyproject.toml` to load plugins
#nonebot.load_from_toml("pyproject.toml")
nonebot.load_plugins("plugins")

# 修改一些配置 / config depends on loaded configs
# 
# config = driver.config
# do something...


if __name__ == "__main__":
    nonebot.logger.info("启动成功")
    nonebot.run(app="__mp_main__:app")
