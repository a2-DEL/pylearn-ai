"""企业 AI Coding 面试真题库（双轨 B 模式 2 的强化版）。

每道题模拟真实企业面试场景：
- 业务需求故意写得模糊（像真实 PM 提的需求）
- 学生不写代码，只写 Prompt 让 AI 生成
- 系统用隐藏测试用例跑 AI 生成的代码
- 评分维度：Prompt 是否要求了边界条件、生成代码是否过测、代码可读性

设计意图：对接 2025-2026 年大厂"AI Coding 面试"新题型——
候选人要展示的不是"我会写代码"，而是"我会指挥 AI 写出正确的代码"。
"""
from __future__ import annotations

from typing import Any, Dict, List


INTERVIEW_QUESTIONS: List[Dict[str, Any]] = [
    {
        "id": 1,
        "title": "列表去重但保持原顺序",
        "difficulty": "easy",
        "category": "数据处理",
        "requirement": (
            "运营同事给了你一个用户 ID 列表，里面有重复值。你需要写个小工具把它去重，"
            "但**第一次出现的顺序不能乱**——因为那是用户登录时间顺序。"
        ),
        "reference_keywords": ["保持顺序", "首次出现", "不要用 set 直接转"],
        "test_cases": [
            {"call": "dedupe([3, 1, 2, 3, 1, 4])", "expected": "[3, 1, 2, 4]"},
            {"call": "dedupe([])", "expected": "[]"},
            {"call": "dedupe([5])", "expected": "[5]"},
        ],
    },
    {
        "id": 2,
        "title": "高频词统计",
        "difficulty": "easy",
        "category": "文本处理",
        "requirement": (
            "产品经理想分析客服聊天记录里用户最常抱怨什么。给你一段英文文本，"
            "请统计每个单词出现次数，忽略大小写，去掉常见标点，返回出现次数最多的前 3 个词。"
        ),
        "reference_keywords": ["lower", "strip", "标点", "top 3", "排序"],
        "test_cases": [
            {
                "call": "top_words('Hello hello world! World world this is a test.', 3)",
                "expected": "['world', 'hello', 'this']",
            },
        ],
    },
    {
        "id": 3,
        "title": "手机号中间四位脱敏",
        "difficulty": "easy",
        "category": "办公自动化",
        "requirement": (
            "HR 要把一份员工通讯录发到群里，但手机号不能明文。请写个函数，"
            "输入 11 位手机号字符串，输出中间 4 位替换成星号的格式，比如 13812345678 → 138****5678。"
            "如果输入不是 11 位数字，原样返回。"
        ),
        "reference_keywords": ["11 位", "中间四位", "异常输入"],
        "test_cases": [
            {"call": "mask_phone('13812345678')", "expected": "'138****5678'"},
            {"call": "mask_phone('123')", "expected": "'123'"},
            {"call": "mask_phone('138123456789')", "expected": "'138123456789'"},
        ],
    },
    {
        "id": 4,
        "title": "两个字典合并",
        "difficulty": "easy",
        "category": "数据处理",
        "requirement": (
            "你有两个配置字典：默认配置和用户自定义配置。用户配置优先级更高，"
            "请写个函数合并它们——同 key 时用户配置覆盖默认，不同 key 都保留。"
        ),
        "reference_keywords": ["默认", "用户覆盖", "不要改原字典"],
        "test_cases": [
            {
                "call": "merge_cfg({'a':1,'b':2}, {'b':3,'c':4})",
                "expected": "{'a': 1, 'b': 3, 'c': 4}",
            },
        ],
    },
    {
        "id": 5,
        "title": "判断回文（忽略大小写和标点）",
        "difficulty": "medium",
        "category": "字符串",
        "requirement": (
            "写个函数判断一句话是不是回文（正读反读一样）。要求：忽略大小写，"
            "忽略空格和标点（比如逗号、句号、感叹号），只比较字母数字。"
            "例如 'A man, a plan, a canal: Panama.' 应该返回 True。"
        ),
        "reference_keywords": ["isalnum", "lower", "标点", "反转"],
        "test_cases": [
            {"call": "is_palindrome('A man, a plan, a canal: Panama.')", "expected": "True"},
            {"call": "is_palindrome('hello')", "expected": "False"},
            {"call": "is_palindrome('')", "expected": "True"},
        ],
    },
    {
        "id": 6,
        "title": "扁平化嵌套列表",
        "difficulty": "medium",
        "category": "数据结构",
        "requirement": (
            "前端给你的接口返回了一个深度未知的嵌套列表，比如 [1, [2, [3, 4], 5], 6]。"
            "请写个函数把它彻底拍平成一维列表 [1,2,3,4,5,6]。"
        ),
        "reference_keywords": ["递归", "isinstance list", "可迭代"],
        "test_cases": [
            {"call": "flatten([1, [2, [3, 4], 5], 6])", "expected": "[1, 2, 3, 4, 5, 6]"},
            {"call": "flatten([])", "expected": "[]"},
            {"call": "flatten([[1],[2],[3]])", "expected": "[1, 2, 3]"},
        ],
    },
    {
        "id": 7,
        "title": "找出现次数最多的元素",
        "difficulty": "medium",
        "category": "算法",
        "requirement": (
            "销售记录里你想知道哪个商品卖得最好。给你一个列表，返回出现次数最多的那个元素。"
            "如果并列最多，返回最先出现的那个。空列表返回 None。"
        ),
        "reference_keywords": ["max", "count", "并列", "None"],
        "test_cases": [
            {"call": "most_frequent(['a','b','a','c','a','b'])", "expected": "'a'"},
            {"call": "most_frequent(['x','x','y','y'])", "expected": "'x'"},
            {"call": "most_frequent([])", "expected": "None"},
        ],
    },
    {
        "id": 8,
        "title": "金额千分位格式化",
        "difficulty": "medium",
        "category": "办公自动化",
        "requirement": (
            "财务报表里金额要按会计习惯显示：1234567.5 → '1,234,567.50'。"
            "保留两位小数，千分位用逗号。输入可能是 int、float 或数字字符串。"
        ),
        "reference_keywords": ["format", "千分位", "两位小数", "字符串输入"],
        "test_cases": [
            {"call": "money(1234567.5)", "expected": "'1,234,567.50'"},
            {"call": "money(100)", "expected": "'100.00'"},
            {"call": "money('9999.9')", "expected": "'9,999.90'"},
        ],
    },
    {
        "id": 9,
        "title": "学生成绩等级",
        "difficulty": "medium",
        "category": "业务逻辑",
        "requirement": (
            "老师要把分数转成等级：>=90 A，>=80 B，>=70 C，>=60 D，<60 F。"
            "写个函数输入分数（可能是 0-100 之间的数字），返回等级字母。"
            "分数超出范围（比如 105 或 -5）返回 'X'。"
        ),
        "reference_keywords": ["边界", ">=90", "异常", "F"],
        "test_cases": [
            {"call": "grade(95)", "expected": "'A'"},
            {"call": "grade(72)", "expected": "'C'"},
            {"call": "grade(55)", "expected": "'F'"},
            {"call": "grade(105)", "expected": "'X'"},
        ],
    },
    {
        "id": 10,
        "title": "日期范围内工作日",
        "difficulty": "hard",
        "category": "真实业务",
        "requirement": (
            "运营要算一次活动持续了多少个工作日（周一到周五，不算周末）。"
            "给你两个日期字符串 'YYYY-MM-DD'，返回之间的工作日天数（含首尾）。"
        ),
        "reference_keywords": ["datetime", "weekday", "迭代"],
        "test_cases": [
            {"call": "workdays('2026-10-05', '2026-10-09')", "expected": "5"},
            {"call": "workdays('2026-10-10', '2026-10-11')", "expected": "0"},
            {"call": "workdays('2026-10-05', '2026-10-05')", "expected": "1"},
        ],
    },
]
