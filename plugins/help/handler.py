from ..config import root as root_path

import os
import re

plugin_dir = root_path / 'plugins'

# 定义不检查的文件夹
exclude_dirs = {"__pycache__", "禁用"}

async def get_all_plugins_detail():
    """获得所有插件的信息"""
    plugin_info = {}

    # 遍历目录
    for root, dirs, files in os.walk(plugin_dir):
        # 过滤掉不检查的文件夹
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                    # 查找插件元数据
                    plugin_meta_match = re.search(
                        r'__plugin_meta__\s*=\s*PluginMetadata\s*\(\s*name\s*=\s*["\'](.*?)["\'].*?extra\s*=\s*\{.*?["\']prefix["\']\s*:\s*["\'](核心|隐藏|功能)["\'].*?\}',
                        content, re.DOTALL)
                    if plugin_meta_match:
                        # 如果插件的prefix是核心或隐藏，跳过此插件
                        continue

                    # 查找插件名
                    plugin_name_match = re.search(r'PluginMetadata\s*\(\s*name\s*=\s*["\'](.*?)["\']', content)
                    if plugin_name_match:
                        plugin_name = plugin_name_match.group(1)
                    else:
                        continue

                    if plugin_name not in plugin_info:
                        plugin_info[plugin_name] = {}

                    # 查找on_command定义
                    command_pattern = re.compile(
                        r'on_command\s*\(\s*["\'](\w+)["\']\s*(?:,\s*aliases\s*=\s*\{([^}]*)\})?\s*(?:,\s*priority\s*=\s*\d+)?\s*(?:,\s*block\s*=\s*(?:True|False))?\s*(?:,\s*permission\s*=\s*\w+)?\s*\)',
                        re.DOTALL
                    )
                    commands = command_pattern.findall(content)
                    for command in commands:
                        command_name = command[0]
                        aliases = command[1].replace('"', '').replace("'", "").split(',') if command[1] else []
                        doc_comments_match = re.search(rf'{command_name}\s*.*?"""(.*?)"""', content, re.DOTALL)
                        doc_comments = doc_comments_match.group(1).strip() if doc_comments_match else ""

                        if command_name not in plugin_info[plugin_name]:
                            plugin_info[plugin_name][command_name] = {
                                "aliases": aliases,
                                "doc_comments": doc_comments
                            }

    # 生成输出信息
    output = ""
    for plugin_name, commands in plugin_info.items():
        output += f"{plugin_name}\n"
        for command_name, details in commands.items():
            aliases_str = ', '.join(details['aliases'])
            doc_comments_str = details['doc_comments']
            output += f"├ {command_name} / {aliases_str}\n"
            output += f"└ {doc_comments_str}\n"
        output += "\n"
    return output


async def get_single_plugin_detail(name: str):
    """获得特定插件信息"""
    plugin_info = {}

    plugin_dir = '.'  # Specify your plugin directory
    exclude_dirs = []  # Specify any directories to exclude

    # 遍历目录
    for root, dirs, files in os.walk(plugin_dir):
        # 过滤掉不检查的文件夹
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                    # 查找插件元数据
                    plugin_meta_match = re.search(
                        rf'__plugin_meta__\s*=\s*PluginMetadata\s*\(\s*name\s*=\s*["\']{name}["\'].*?description\s*=\s*["\'](.*?)["\'].*?usage\s*=\s*["\'](.*?)["\'].*?extra\s*=\s*\{{(.*?)\}}\s*\)',
                        content, re.DOTALL)
                    if plugin_meta_match:
                        description = plugin_meta_match.group(1)
                        usage = plugin_meta_match.group(2)
                        extra_str = plugin_meta_match.group(3)
                        extra = dict(re.findall(r'["\'](.*?)["\']\s*:\s*["\'](.*?)["\']', extra_str))

                        if extra.get('prefix') in ['核心', '隐藏']:
                            continue

                        plugin_info = {
                            'description': description,
                            'usage': usage,
                            'extra': extra,
                            'commands': {}
                        }

                        # 查找on_command定义
                        command_pattern = re.compile(
                        r'on_command\s*\(\s*["\'](\w+)["\']\s*(?:,\s*aliases\s*=\s*\{([^}]*)\})?\s*(?:,\s*priority\s*=\s*\d+)?\s*(?:,\s*block\s*=\s*(?:True|False))?\s*(?:,\s*permission\s*=\s*\w+)?\s*\)',
                        re.DOTALL
                    )
                        commands = command_pattern.findall(content)
                        for command in commands:
                            command_name = command[0]
                            aliases = command[1].replace('"', '').replace("'", "").split(',') if command[1] else []
                            doc_comments_match = re.search(rf'{command_name}\s*.*?"""(.*?)"""', content, re.DOTALL)
                            doc_comments = doc_comments_match.group(1).strip() if doc_comments_match else ""

                            if command_name not in plugin_info['commands']:
                                plugin_info['commands'][command_name] = {
                                    "aliases": aliases,
                                    "doc_comments": doc_comments
                                }

    if not plugin_info:
        return None

    info = plugin_info
    version = info['extra'].get('version')
    output = f"版本 - {version}\n"
    output += f"{info['description']}\n"
    output += f"\n用法\n{info['usage']}\n"
    output += f"\n命令\n"

    for command_name, details in info['commands'].items():
        aliases_str = ', '.join(details['aliases'])
        doc_comments_str = details['doc_comments']
        output += f"├ {command_name} / {aliases_str}\n"
        output += f"└ {doc_comments_str}\n"

    output += "\n"
    return output