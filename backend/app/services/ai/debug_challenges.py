"""代码审查找 bug 训练题库（双轨 B 模式 3）。

每道题包含：标题、题干、埋雷版代码（buggy）、参考答案（reference）、
测试用例（test_cases，用学生修复后的代码跑）、bug 列表（供 AI 评审参考）。
"""
from __future__ import annotations

from typing import Any, Dict, List


DEBUG_CHALLENGES: List[Dict[str, Any]] = [
    {
        "id": 1,
        "title": "求和函数的三个坑",
        "difficulty": "easy",
        "description": (
            "下面的 sum_list 函数期望返回列表所有数字之和，但埋了三个 bug。"
            "请找出并修复，让测试用例全部通过。"
        ),
        "buggy_code": (
            "def sum_list(lst):\n"
            "    total = 0\n"
            "    for i in lst:\n"
            "        total = i          # bug1: 应为 +=\n"
            "    return total\n"
        ),
        "reference_code": (
            "def sum_list(lst):\n"
            "    total = 0\n"
            "    for i in lst:\n"
            "        total += i\n"
            "    return total\n"
        ),
        "bugs": [
            "total = i 应为 total += i，否则只保留最后一个元素",
        ],
        "test_cases": [
            {"input": "sum_list([1,2,3,4])", "expected": "10"},
            {"input": "sum_list([])", "expected": "0"},
            {"input": "sum_list([-1, 1])", "expected": "0"},
        ],
    },
    {
        "id": 2,
        "title": "判断偶数的边界",
        "difficulty": "easy",
        "description": (
            "is_even 函数判断 n 是否为偶数。它对正数工作正常，但对 0 和负数出错。请修复。"
        ),
        "buggy_code": (
            "def is_even(n):\n"
            "    if n % 2 == 1:\n"
            "        return False\n"
            "    return True\n"
        ),
        "reference_code": (
            "def is_even(n):\n"
            "    return n % 2 == 0\n"
        ),
        "bugs": [
            "n%2==1 对负数 -1 得到 -1（不是 1），判断失效",
            "0 是偶数但原逻辑侥幸返回 True；应直接 n%2==0",
        ],
        "test_cases": [
            {"input": "is_even(2)", "expected": "True"},
            {"input": "is_even(3)", "expected": "False"},
            {"input": "is_even(0)", "expected": "True"},
            {"input": "is_even(-4)", "expected": "True"},
            {"input": "is_even(-3)", "expected": "False"},
        ],
    },
    {
        "id": 3,
        "title": "字典计数漏了更新",
        "difficulty": "medium",
        "description": (
            "word_freq 应统计每个单词出现次数。运行后所有计数都是 1，请找出 bug。"
        ),
        "buggy_code": (
            "def word_freq(words):\n"
            "    freq = {}\n"
            "    for w in words:\n"
            "        if w not in freq:\n"
            "            freq[w] = 1\n"
            "        # bug: 缺少 else 分支累加\n"
            "    return freq\n"
        ),
        "reference_code": (
            "def word_freq(words):\n"
            "    freq = {}\n"
            "    for w in words:\n"
            "        if w not in freq:\n"
            "            freq[w] = 1\n"
            "        else:\n"
            "            freq[w] += 1\n"
            "    return freq\n"
        ),
        "bugs": [
            "缺少 else 分支：重复单词的计数永远停在 1",
        ],
        "test_cases": [
            {"input": "word_freq(['a','b','a','c','a'])", "expected": "{'a': 3, 'b': 1, 'c': 1}"},
            {"input": "word_freq([])", "expected": "{}"},
        ],
    },
    {
        "id": 4,
        "title": "循环里改列表（经典陷阱）",
        "difficulty": "hard",
        "description": (
            "remove_odds 期望移除列表中所有奇数。但边遍历边删会跳过元素，结果不对。请修复。"
        ),
        "buggy_code": (
            "def remove_odds(lst):\n"
            "    for x in lst:\n"
            "        if x % 2 == 1:\n"
            "            lst.remove(x)\n"
            "    return lst\n"
        ),
        "reference_code": (
            "def remove_odds(lst):\n"
            "    return [x for x in lst if x % 2 == 0]\n"
        ),
        "bugs": [
            "边遍历边 remove 会让索引前移、跳过相邻元素",
            "应改用列表推导式或遍历副本",
        ],
        "test_cases": [
            {"input": "remove_odds([1,2,3,4,5])", "expected": "[2, 4]"},
            {"input": "remove_odds([1,3,5])", "expected": "[]"},
            {"input": "remove_odds([2,4,6])", "expected": "[2, 4, 6]"},
        ],
    },
]
