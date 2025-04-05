import re
from typing import Optional


def rename_series(name: str, ep_pattern: Optional[str], vol_pattern: Optional[str], ep_format: str = "Ch.{num}",
                  vol_format: str = "Vol.{num}") -> tuple[str, float, bool]:
    """
    根据自定义模式重命名系列名称

    :param name: 原始文件名
    :param ep_pattern: 话数匹配正则表达式，需包含一个数字捕获组
    :param vol_pattern: 卷数匹配正则表达式，需包含一个数字捕获组
    :param ep_format: 话数格式化字符串模板，可用{num}占位
    :param vol_format: 卷数格式化字符串模板，可用{num}占位
    :return: (新名称, 数值, 是否未匹配)
    """
    # 匹配自定义话数格式
    if not ep_pattern:
        # 正常检测 第x话 或是 test第x话test 这种形式
        ep_pattern = r'第\s*(\d+\.?\d*)\s*[话話]'
    if not vol_pattern:
        # 因为防止匹配到其他的卷特典啥的就直接严格按照第x卷格式进行判断
        vol_pattern = r'(?:^|[\s\-_])(?:第?\s*(\d+\.?\d*)\s*[卷巻])(?:$|[\s\-_])'
    ep_match = re.search(ep_pattern, name)
    if ep_match:
        num_str = ep_match.group(1)

        # 处理数字格式
        if '.' in num_str:
            integer_part, decimal_part = num_str.split('.', 1)
            formatted_integer = f"{int(integer_part):04d}"
            formatted_num = f"{formatted_integer}.{decimal_part}"
        else:
            formatted_num = f"{int(num_str):04d}"

        return ep_format.format(num=formatted_num), float(num_str), False

    # 匹配自定义卷数格式
    vol_match = re.search(vol_pattern, name)
    if vol_match:
        num_str = vol_match.group(1)
        return vol_format.format(num=num_str), float(num_str), False

    return name, 0, True
