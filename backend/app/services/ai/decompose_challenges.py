"""需求拆解训练题库（双轨 B 模式 1）。

每道题是一个真实业务需求，学生不写代码，先写"我准备怎么拆"。
"""
from __future__ import annotations

from typing import Any, Dict, List


DECOMPOSE_CHALLENGES: List[Dict[str, Any]] = [
    {
        "id": 1,
        "title": "成绩统计小工具",
        "difficulty": "easy",
        "requirement": (
            "班主任有一个 Excel，里面是全班 45 人的期中成绩，每人一行，列有"
            "姓名、语文、数学、英语。他想要一个工具：输入 Excel 文件，自动算出"
            "每个人总分、班级平均分，并标出不及格（<60）的同学，最后导出一份新表。"
        ),
    },
    {
        "id": 2,
        "title": "招聘信息监控",
        "difficulty": "medium",
        "requirement": (
            "你是应届生，想每天早上自动收到一封邮件：昨天某招聘网上新增的、"
            "地点在你目标城市、岗位名含「Python」的职位列表，含公司名和链接。"
            "不希望有重复。"
        ),
    },
    {
        "id": 3,
        "title": "小店流水对账",
        "difficulty": "medium",
        "requirement": (
            "奶茶店老板每天有两份数据：收银系统导出的销售流水（时间、商品、金额），"
            "和外卖平台导出的订单（时间、商品、金额、平台抽成）。他要每周日自动"
            "汇总上周：堂食总额、外卖总额、平台抽成、净收入，并按销量排出 TOP5 商品。"
        ),
    },
    {
        "id": 4,
        "title": "朋友圈自动整理",
        "difficulty": "hard",
        "requirement": (
            "你想做一个小工具：把一个微信群里大家三个月发的所有文件（PDF/Word/图片）"
            "自动按月份归档到网盘，并生成一个索引页（文件名、发送人、发送时间、简介），"
            "方便日后搜索。需要能识别重复文件。"
        ),
    },
]
