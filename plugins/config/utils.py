from pathlib import Path
from typing import Union
import ruamel.yaml
import logging
import glob
import loguru,sys

logger = loguru.logger

default_format: str = (
    "<g>{time:MM-DD HH:mm:ss}</g> "
    "[<lvl>{level}</lvl>] "
    #"<c><u>{module}</u></c> | "
    # "<c>{function}:{line}</c>| "
    "{message}"
)
"""默认日志格式"""
def default_filter(record):
    """默认的日志过滤器，根据 `config.log_level` 配置改变日志等级。"""
    log_level = record["extra"].get("nonebot_log_level", "INFO")
    levelno = logger.level(log_level).no if isinstance(log_level, str) else log_level
    return record["level"].no >= levelno

logger.remove()
logger_id = logger.add(
    sys.stdout,
    level=0,
    diagnose=False,
    filter=default_filter,
    format=default_format,

)

class ConfigLoader:
    def __init__(self, config_path: Union[Path, str], encoding: str = 'utf-8'):
        self.config_path = Path(config_path)
        self.encoding = encoding
        self.logger = logger

    def load_yaml_file(self, path: Path):
        """
        读取 YAML 文件并返回数据
        """
        try:
            with path.open('r', encoding=self.encoding) as file:
                data = ruamel.yaml.YAML().load(file)
                #self.logger.opt(colors=True).info(f"<c><u>config</u></c> | ✅ 加载配置文件: {path}")
                #self.logger.info(f"成功加载配置文件: {path}")
                return data
        except Exception as e:
            self.logger.opt(colors=True).info(f"<c><u>config</u></c> | ⚠️ 加载配置文件: {path}, 错误: {e}")
            #self.logger.error(f"加载配置文件失败: {path}, 错误: {e}")
            return None

    def load_yaml_single(self, name: str, path: Union[Path, str]):
        """
        读取本地 YAML 文件，返回单个配置信息
        :param name: 配置名字
        :param path: 文件路径
        :return: 所要的配置信息，如果不存在返回 None
        """
        path = Path(path)
        data = self.load_yaml_file(path)
        return data.get(name, None) if data else None

    def load_yaml_dict(self, path: Union[Path, str]):
        """
        读取本地 YAML 文件，返回多个配置信息的字典
        :param path: 文件路径
        :return: 配置字典
        """
        path = Path(path)
        return self.load_yaml_file(path)

    def save_yaml(self, data: dict, path: Union[Path, str]):
        """
        保存字典数据到 YAML 文件
        :param data: 数据，字典类型
        :param path: 保存路径
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with path.open('w', encoding=self.encoding) as file:
                ruamel.yaml.YAML().dump(data, file, Dumper=ruamel.yaml.RoundTripDumper, default_flow_style=False, allow_unicode=True, indent=2)
                self.logger.opt(colors=True).info(f"<c><u>config</u></c> | ✅ 保存配置文件: {path}")
        except Exception as e:
            self.logger.opt(colors=True).info(f"<c><u>config</u></c> | ⚠️ 保存配置文件: {path}, 错误: {e}")
    def load_all_configs(self):
        """
        加载所有配置文件
        :return: 配置字典
        """
        configs = {}
        config_files = glob.glob(str(self.config_path / '*.yml'))
        count = 0
        for file_path in config_files:
            count += 1
            file_name = Path(file_path).stem
            configs[file_name] = self.load_yaml_dict(file_path)
        self.logger.opt(colors=True).info(f"<c><u>config</u></c> | ✅ 加载 {count} 个配置文件")
        return configs
