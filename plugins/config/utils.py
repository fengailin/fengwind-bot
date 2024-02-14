import yaml
from typing import Union
from pathlib import Path
import ruamel.yaml
def load_yaml_single(name, path: Union[Path, str], encoding: str = 'utf-8'):
    """
    读取本地yaml文件，返回单个配置信息
    适合单配置项使用
        :param name: 配置名字
        :param path: 文件路径
        :param encoding: 编码，默认为utf-8
        :return: 所要的配置信息
    """
    path = Path(path)
    data = ruamel.yaml.YAML().load(path.read_text(encoding=encoding))
    #data = yaml.load(path.read_text(encoding=encoding),
    #                 Loader=yaml.Loader) if path.exists() else {}
        # 判断传入的配置名字是否在存在
    if name in data.keys():
        return data[name]
    else:
        return None
def load_yaml_dict(path: Union[Path, str], encoding: str = 'utf-8'):
    """
    读取本地yaml文件，返回多个配置信息的字典
    适合多配置项使用
        :param path: 文件路径
        :param encoding: 编码，默认为utf-8
        :return: 字典
    """
    path = Path(path)
    data = ruamel.yaml.YAML().load(path.read_text(encoding=encoding))
    #data = yaml.load(path.read_text(encoding=encoding),
    #                 Loader=yaml.Loader) if path.exists() else {}
    return data
def save_yaml(data: dict, path: Union[Path, str] = None, encoding: str = 'utf-8'):
    """
    保存yaml文件
        :param data: 数据[字典类型]
        :param path: 保存路径
        :param encoding: 编码，默认为utf-8
        
        效果:
        {'a': [1,2],'b':'c'}
        a:
          - 1
          - 2
        b: c

    """
    if isinstance(path, str):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('w', encoding=encoding) as f:
            ruamel.yaml.YAML().dump(data,
                             f,
                             Dumper=yaml.RoundTripDumper,default_flow_style=False,
                             allow_unicode=True, 
                             indent=2)
    #    yaml.dump(
    #        data,
    #        f,
    #        indent=2,
    #        sort_keys=False,
    #        allow_unicode=True)
