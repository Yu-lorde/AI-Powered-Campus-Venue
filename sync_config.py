#!/usr/bin/env python3
"""同步 config.example.py 的新增配置到 config.py

保留 config.py 中的自定义值（如 API Key），只添加 example 中新增的配置项。
用法: python sync_config.py
"""

import re
import sys
from pathlib import Path


def extract_vars(content):
    """提取文件中的所有变量定义 {name: line_text}"""
    vars_dict = {}
    for line in content.split('\n'):
        # 匹配大写变量名赋值，如 API_KEY = "xxx" 或 USE_KNOWLEDGE_BASE = True
        match = re.match(r'^([A-Z_][A-Z_0-9]*)\s*=\s*(.+)$', line.strip())
        if match and not line.strip().startswith('#'):
            name = match.group(1)
            vars_dict[name] = line
    return vars_dict


def sync_config():
    root = Path(__file__).parent
    example_path = root / 'config.example.py'
    config_path = root / 'config.py'

    if not example_path.exists():
        print("❌ config.example.py 不存在")
        sys.exit(1)

    if not config_path.exists():
        print("config.py 不存在，直接从 example 复制...")
        config_path.write_text(example_path.read_text(encoding='utf-8'), encoding='utf-8')
        print("✓ 已创建 config.py，请编辑填入你的 API Key")
        return

    example_content = example_path.read_text(encoding='utf-8')
    config_content = config_path.read_text(encoding='utf-8')

    example_vars = extract_vars(example_content)
    config_vars = extract_vars(config_content)

    # 找出 example 中有但 config 中没有的变量
    new_vars = []
    for name, line in example_vars.items():
        if name not in config_vars:
            new_vars.append(line)

    if not new_vars:
        print("✓ config.py 已是最新，无需更新")
        return

    # 在 config.py 末尾添加新变量
    with open(config_path, 'a', encoding='utf-8') as f:
        f.write('\n\n# ===== 自动同步新增配置（来自 config.example.py）=====\n')
        for line in new_vars:
            f.write(line + '\n')

    print(f"✓ 已添加 {len(new_vars)} 个新配置项到 config.py:")
    for line in new_vars:
        print(f"  + {line.strip()}")
    print("\n提示: 请检查新增配置是否需要修改默认值")


if __name__ == '__main__':
    sync_config()
