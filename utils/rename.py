import re
from typing import Tuple


def rename_series(name: str) -> Tuple[str, float, bool]:
    # 匹配 "第X话" 格式
    ep_match = re.search(r'第(\d+\.?\d*)话', name)
    if ep_match:
        num_str = ep_match.group(1)

        # 处理整数部分补零
        if '.' in num_str:
            integer_part, decimal_part = num_str.split('.', 1)
        else:
            integer_part, decimal_part = num_str, None

        formatted_integer = f"{int(integer_part):05d}"
        new_num = f"{formatted_integer}.{decimal_part}" if decimal_part else formatted_integer

        return f"Ch.{new_num}", float(num_str), False

    # 匹配 "第X卷" 格式
    vol_match = re.search(r'第(\d+\.?\d*)卷', name)
    if vol_match:
        return f"Vol.{vol_match.group(1)}", vol_match.group(1), False

    # 都不匹配的情况
    return name, 0, True


# 测试用例
if __name__ == "__main__":
    test_cases = [
        ("第1话", "Ch.00001", False),
        ("第3.5话", "Ch.00003.5", False),
        ("第03.5话", "Ch.00003.5", False),
        ("第1023话", "Ch.01023", False),
        ("第1卷", "Vol.1", False),
        ("第10.5卷", "Vol.10.5", False),
        ("试看版", "试看版", True),
        ("第1话试看", "Ch.00001", False),
        ("异常格式", "异常格式", True),
    ]

    for original, expected_name, expected_special in test_cases:
        result, num, is_special = rename_series(original)
        assert (result == expected_name) and (is_special == expected_special), \
            f"Failed: {original} -> ({result},{num} {is_special})"
        print(f"Passed: {original} -> ({result},{num} {is_special})")
