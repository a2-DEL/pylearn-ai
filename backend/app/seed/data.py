"""初始知识库与题目数据（阶段一：基础层知识点 + 训练场题目）。"""

# 三级知识架构 - 基础层（必学）
KNOWLEDGE_POINTS: list[dict] = [
    {
        "layer": "basic",
        "category": "基础语法",
        "slug": "variables-types",
        "title": "变量与数据类型",
        "difficulty": "easy",
        "order_index": 1,
        "content": (
            "变量是数据的名字，Python 是动态类型语言，无需声明类型即可赋值。\n"
            "常见基础类型：int（整数）、float（浮点）、str（字符串）、bool（布尔）、"
            "list（列表）、tuple（元组）、dict（字典）、set（集合）。\n\n"
            "要点：\n"
            "1. 变量名由字母、数字、下划线组成，不能以数字开头；\n"
            "2. 区分大小写；\n"
            "3. 使用 type() 查看类型，使用 str()/int()/float() 等做类型转换。"
        ),
        "example_code": (
            "name = 'PyLearn'\n"
            "age = 18\n"
            "score = 95.5\n"
            "passed = True\n"
            "skills = ['Python', 'SQL', 'Viz']\n"
            "info = {'name': name, 'age': age}\n"
            "print(type(name), type(age), type(skills))\n"
            "print(f'{name} 今年 {age} 岁，掌握 {len(skills)} 项技能')"
        ),
    },
    {
        "layer": "basic",
        "category": "基础语法",
        "slug": "condition-loop",
        "title": "条件与循环",
        "difficulty": "easy",
        "order_index": 2,
        "content": (
            "条件：if / elif / else 根据布尔表达式分支执行。\n"
            "循环：for 遍历可迭代对象，while 按条件重复执行。\n"
            "配合 break（跳出）、continue（跳过本次）、range() 使用。\n\n"
            "要点：Python 用缩进来划分代码块（通常 4 个空格），缩进错误会导致语法错误。"
        ),
        "example_code": (
            "for i in range(1, 6):\n"
            "    if i % 2 == 0:\n"
            "        print(f'{i} 是偶数')\n"
            "    else:\n"
            "        print(f'{i} 是奇数')\n"
            "\n"
            "n = 1\n"
            "while n <= 3:\n"
            "    print('count', n)\n"
            "    n += 1"
        ),
    },
    {
        "layer": "basic",
        "category": "基础语法",
        "slug": "functions",
        "title": "函数",
        "difficulty": "easy",
        "order_index": 3,
        "content": (
            "函数用 def 定义，用于封装可复用逻辑。支持位置参数、默认参数、*args、**kwargs。\n"
            "函数可通过 return 返回值；不写 return 默认返回 None。\n"
            "lambda 用于定义匿名单行函数。\n\n"
            "要点：函数是一等公民，可作为参数传递、作为返回值，是后续高阶编程的基础。"
        ),
        "example_code": (
            "def add(a, b=0):\n"
            "    return a + b\n"
            "\n"
            "square = lambda x: x * x\n"
            "\n"
            "print(add(3, 5))\n"
            "print(square(4))\n"
            "print(list(map(square, [1, 2, 3])))"
        ),
    },
    {
        "layer": "basic",
        "category": "面向对象",
        "slug": "class-object",
        "title": "类与对象",
        "difficulty": "medium",
        "order_index": 4,
        "content": (
            "类是创建对象的蓝图，封装数据与行为。\n"
            "class 定义类，__init__ 为构造方法，self 表示实例自身。\n"
            "支持继承、多态与方法重写。\n\n"
            "要点：面向对象适合建模复杂业务（如学生、作业、班级），提升代码组织度。"
        ),
        "example_code": (
            "class Student:\n"
            "    def __init__(self, name, score=0):\n"
            "        self.name = name\n"
            "        self.score = score\n"
            "\n"
            "    def greet(self):\n"
            "        return f'我是 {self.name}，成绩 {self.score}'\n"
            "\n"
            "s = Student('小明', 88)\n"
            "print(s.greet())"
        ),
    },
    {
        "layer": "basic",
        "category": "IO",
        "slug": "file-io",
        "title": "文件操作",
        "difficulty": "medium",
        "order_index": 5,
        "content": (
            "使用 open() 打开文件，配合 with 语句可自动关闭。\n"
            "模式：'r' 读、'w' 写（覆盖）、'a' 追加、'b' 二进制。\n"
            "read()/readline()/readlines() 读取，write() 写入。\n\n"
            "要点：始终用 with 管理文件，避免资源泄漏；注意编码 encoding='utf-8'。"
        ),
        "example_code": (
            "with open('note.txt', 'w', encoding='utf-8') as f:\n"
            "    f.write('Hello PyLearn\\n')\n"
            "\n"
            "with open('note.txt', 'r', encoding='utf-8') as f:\n"
            "    for line in f:\n"
            "        print(line.strip())"
        ),
    },
    {
        "layer": "basic",
        "category": "异常处理",
        "slug": "exception",
        "title": "异常处理",
        "difficulty": "medium",
        "order_index": 6,
        "content": (
            "try/except 捕获运行时异常，避免程序中断。\n"
            "可配合 else（无异常时执行）、finally（始终执行）。\n"
            "常见异常：ZeroDivisionError、TypeError、ValueError、FileNotFoundError。\n\n"
            "要点：只捕获预期异常，不要用裸 except 吞掉所有错误，便于排查问题。"
        ),
        "example_code": (
            "def safe_div(a, b):\n"
            "    try:\n"
            "        return a / b\n"
            "    except ZeroDivisionError:\n"
            "        return '除数不能为 0'\n"
            "    finally:\n"
            "        print('计算结束')\n"
            "\n"
            "print(safe_div(10, 2))\n"
            "print(safe_div(10, 0))"
        ),
    },
    {
        "layer": "basic",
        "category": "工程化",
        "slug": "module-package",
        "title": "模块与包",
        "difficulty": "medium",
        "order_index": 7,
        "content": (
            "模块即一个 .py 文件，包是含 __init__.py 的目录。\n"
            "import 导入模块，from ... import ... 导入指定对象。\n"
            "使用 if __name__ == '__main__' 区分被导入与直接运行。\n\n"
            "要点：合理拆分模块是工程化第一步；避免循环导入。"
        ),
        "example_code": (
            "# math_demo.py\n"
            "import math\n"
            "from random import randint\n"
            "\n"
            "print(math.sqrt(16))\n"
            "print('随机点数：', randint(1, 6))"
        ),
    },
    # ---------------- 工具层（选学） ----------------
    {
        "layer": "tool",
        "category": "数据分析",
        "slug": "numpy-basics",
        "title": "NumPy 数组入门",
        "difficulty": "medium",
        "order_index": 8,
        "content": (
            "NumPy 提供高性能多维数组 ndarray，是数据分析与科学计算基石。\n"
            "常用：np.array 创建、reshape 变形、切片索引、向量化运算（无需循环）。\n"
            "要点：向量化比纯 Python 循环快得多；注意广播（broadcast）规则。"
        ),
        "example_code": (
            "import numpy as np\n"
            "a = np.array([1, 2, 3])\n"
            "b = np.array([4, 5, 6])\n"
            "print(a + b)            # 向量化加法\n"
            "print(a * 2)\n"
            "m = a.reshape(1, 3)\n"
            "print(m.shape)"
        ),
    },
    {
        "layer": "tool",
        "category": "数据分析",
        "slug": "pandas-basics",
        "title": "Pandas 数据处理",
        "difficulty": "medium",
        "order_index": 9,
        "content": (
            "Pandas 提供 DataFrame（表格）与 Series，擅长数据清洗与分析。\n"
            "常用：read_csv 读取、df.head 预览、df.groupby 分组聚合、df.describe 统计。\n"
            "要点：DataFrame 是二维带列名结构，类似 Excel 表；缺失值用 dropna/fillna 处理。"
        ),
        "example_code": (
            "import pandas as pd\n"
            "df = pd.DataFrame({'name': ['A', 'B'], 'score': [90, 80]})\n"
            "print(df.describe())\n"
            "print(df[df['score'] >= 85])\n"
            "print(df['score'].mean())"
        ),
    },
    {
        "layer": "tool",
        "category": "数据可视化",
        "slug": "matplotlib-basics",
        "title": "Matplotlib 可视化",
        "difficulty": "easy",
        "order_index": 10,
        "content": (
            "Matplotlib 是最常用的绘图库，pyplot 接口类似 MATLAB。\n"
            "常用：plot 折线、scatter 散点、bar 柱状、show/savefig 输出。\n"
            "要点：在沙箱中绘图需加 matplotlib.use('Agg') 并使用 savefig，避免无界面报错。"
        ),
        "example_code": (
            "import matplotlib\n"
            "matplotlib.use('Agg')\n"
            "import matplotlib.pyplot as plt\n"
            "plt.plot([1, 2, 3], [1, 4, 9])\n"
            "plt.title('平方曲线')\n"
            "plt.savefig('line.png')\n"
            "print('已保存 line.png')"
        ),
    },
    {
        "layer": "tool",
        "category": "网络爬虫",
        "slug": "requests-basics",
        "title": "Requests 网络请求",
        "difficulty": "medium",
        "order_index": 11,
        "content": (
            "Requests 让 HTTP 请求变得简单：get/post 获取网页与接口数据。\n"
            "常用：resp.text 文本、resp.json() JSON、headers 携带请求头、params 查询参数。\n"
            "要点：爬虫需遵守 robots 协议与目标站点频率限制；本地沙箱默认无网络。"
        ),
        "example_code": (
            "import requests\n"
            "r = requests.get('https://httpbin.org/get', timeout=5)\n"
            "print(r.status_code)\n"
            "print(r.json().get('url'))"
        ),
    },
    # ---------------- 工具层（选学）·补充 ----------------
    {
        "layer": "tool",
        "category": "数据可视化",
        "slug": "seaborn-basics",
        "title": "Seaborn 统计图表",
        "difficulty": "medium",
        "order_index": 12,
        "content": (
            "Seaborn 基于 Matplotlib，专为统计可视化设计，一行代码出精美图。\n"
            "常用：sns.barplot / sns.lineplot / sns.scatterplot / sns.heatmap 热力图。\n"
            "要点：DataFrame 列名即映射；做图前先 set_style 设置主题。"
        ),
        "example_code": (
            "import matplotlib\n"
            "matplotlib.use('Agg')\n"
            "import matplotlib.pyplot as plt\n"
            "import seaborn as sns\n"
            "import pandas as pd\n"
            "df = pd.DataFrame({'x':[1,2,3,4],'y':[2,4,1,5]})\n"
            "sns.barplot(data=df, x='x', y='y')\n"
            "plt.savefig('bar.png')\n"
            "print('ok')"
        ),
    },
    {
        "layer": "tool",
        "category": "数据可视化",
        "slug": "pyecharts-basics",
        "title": "Pyecharts 交互式图表",
        "difficulty": "medium",
        "order_index": 13,
        "content": (
            "Pyecharts 把 ECharts 封装成 Python 接口，生成可在浏览器交互的 HTML 图表。\n"
            "常用：Bar / Line / Pie / WordCloud；通过 .add_xaxis / .add_yaxis 配置数据。\n"
            "要点：render('chart.html') 输出独立网页；适合做可交互的报表。"
        ),
        "example_code": (
            "from pyecharts.charts import Bar\n"
            "from pyecharts import options as opts\n"
            "bar = Bar().add_xaxis(['A','B','C']).add_yaxis('分数', [90,80,70])\n"
            "bar.render('bar.html')\n"
            "print('已生成 bar.html')"
        ),
    },
    {
        "layer": "tool",
        "category": "办公自动化",
        "slug": "openpyxl-basics",
        "title": "OpenPyXL 读写 Excel",
        "difficulty": "easy",
        "order_index": 14,
        "content": (
            "OpenPyXL 让 Python 直接读写 .xlsx 文件，是办公自动化的核心库。\n"
            "常用：Workbook() 新建、ws.append() 追加行、wb.save() 保存；load_workbook 打开已有文件。\n"
            "要点：工作表下标从 1 开始，不是 0。"
        ),
        "example_code": (
            "from openpyxl import Workbook\n"
            "wb = Workbook()\n"
            "ws = wb.active\n"
            "ws.append(['姓名','分数'])\n"
            "ws.append(['小明', 95])\n"
            "ws.append(['小红', 88])\n"
            "wb.save('scores.xlsx')\n"
            "print('已生成 scores.xlsx')"
        ),
    },
    {
        "layer": "tool",
        "category": "网络爬虫",
        "slug": "bs4-basics",
        "title": "BeautifulSoup 解析网页",
        "difficulty": "medium",
        "order_index": 15,
        "content": (
            "BeautifulSoup 把 HTML 字符串解析成 DOM 树，按标签/CSS 选择器提取数据。\n"
            "常用：soup.select('div.item')、soup.get_text()、tag['href']。\n"
            "要点：爬虫需遵守目标站点 robots 协议与频率限制；本地沙箱默认无网络。"
        ),
        "example_code": (
            "from bs4 import BeautifulSoup\n"
            "html = '<html><body><a href=\"/x\">链接</a></body></html>'\n"
            "soup = BeautifulSoup(html, 'html.parser')\n"
            "a = soup.find('a')\n"
            "print(a.text, a['href'])"
        ),
    },
    # ---------------- 应用层（实战） ----------------
    {
        "layer": "app",
        "category": "综合项目",
        "slug": "word-cloud",
        "title": "简历词云（综合案例）",
        "difficulty": "hard",
        "order_index": 16,
        "content": (
            "应用层实战：结合文件读取、jieba 分词与 wordcloud 生成词云图。\n"
            "流程：读取文本 -> 分词 -> 过滤停用词 -> 生成词云并保存图片。\n"
            "要点：中文分词需要 jieba；词云输出图片用 savefig/Agg 后端。"
        ),
        "example_code": (
            "from wordcloud import WordCloud\n"
            "import jieba\n"
            "text = 'Python 数据分析 可视化 Python 编程 学习'\n"
            "words = ' '.join(jieba.lcut(text))\n"
            "wc = WordCloud(width=400, height=200, font_path=None).generate(words)\n"
            "wc.to_file('cloud.png')\n"
            "print('已生成 cloud.png')"
        ),
    },
    {
        "layer": "app",
        "category": "趣味案例",
        "slug": "love-heart",
        "title": "爱心函数（趣味可视化）",
        "difficulty": "easy",
        "order_index": 17,
        "content": (
            "用 Matplotlib 绘制经典心形曲线，体会数学与可视化的结合。\n"
            "心形线参数方程：x=16sin^3(t)，y=13cos(t)-5cos(2t)-2cos(3t)-cos(4t)。\n"
            "要点：用 numpy 生成参数点，plt.plot 连线；在沙箱中务必 use('Agg') 并 savefig。"
        ),
        "example_code": (
            "import matplotlib\n"
            "matplotlib.use('Agg')\n"
            "import matplotlib.pyplot as plt\n"
            "import numpy as np\n"
            "t = np.linspace(0, 2*np.pi, 200)\n"
            "x = 16*np.sin(t)**3\n"
            "y = 13*np.cos(t)-5*np.cos(2*t)-2*np.cos(3*t)-np.cos(4*t)\n"
            "plt.plot(x, y, color='red', linewidth=2)\n"
            "plt.savefig('heart.png')\n"
            "print('已生成 heart.png')"
        ),
    },
    {
        "layer": "app",
        "category": "趣味案例",
        "slug": "hacker-rain",
        "title": "黑客代码雨（字符动画）",
        "difficulty": "medium",
        "order_index": 18,
        "content": (
            "用终端 ANSI 转义序列模拟《黑客帝国》代码雨。\n"
            "核心思路：在若干列上随机下落字符，用光标归位 + 清屏，配合 time.sleep 控制帧率。\n"
            "要点：在沙箱批量输出即可看到效果；实际动画需在终端运行。"
        ),
        "example_code": (
            "import time, random\n"
            "chars = '01アイウエオカキクケコ'\n"
            "for i in range(20):\n"
            "    line = ''.join(random.choice(chars) for _ in range(40))\n"
            "    print(line)\n"
            "    time.sleep(0.05)\n"
            "print('代码雨播放完毕')"
        ),
    },
    {
        "layer": "app",
        "category": "数据分析",
        "slug": "sales-analysis",
        "title": "销售数据透视（Pandas 实战）",
        "difficulty": "medium",
        "order_index": 19,
        "content": (
            "模拟一份月度销售流水，用 Pandas 做分组聚合与透视，回答'哪个产品最赚钱'。\n"
            "流程：构造 DataFrame -> groupby 产品求和 -> 排序 -> 输出结论。\n"
            "要点：真实工作中这一步通常是 pd.read_csv('sales.csv')，这里用内置数据演示。"
        ),
        "example_code": (
            "import pandas as pd\n"
            "df = pd.DataFrame({\n"
            "  'product':['A','B','A','C','B','A'],\n"
            "  'amount':[100,200,150,80,120,300]})\n"
            "r = df.groupby('product')['amount'].sum().sort_values(ascending=False)\n"
            "print(r)"
        ),
    },
]

# 训练场题目
PROBLEMS: list[dict] = [
    {
        "title": "两数之和",
        "difficulty": "easy",
        "knowledge_point": "condition-loop",
        "description": (
            "给定一个整数列表 nums 与目标值 target，请返回两数之和等于 target 的下标（假设有且唯一一组）。\n"
            "函数签名：def two_sum(nums, target) -> list"
        ),
        "example_input": "nums=[2,7,11,15], target=9",
        "example_output": "[0,1]",
        "test_cases": [
            {"input": "two_sum([2,7,11,15], 9)", "expected": "[0, 1]"},
            {"input": "two_sum([3,2,4], 6)", "expected": "[1, 2]"},
        ],
        "hints": [
            "用两层循环枚举每一对组合。",
            "用字典记录已遍历数字的值与下标，可一次遍历完成。",
            "参考实现：\ndef two_sum(nums, target):\n    seen = {}\n    for i, v in enumerate(nums):\n        if target - v in seen:\n            return [seen[target - v], i]\n        seen[v] = i\n    return []",
        ],
    },
    {
        "title": "斐波那契数列",
        "difficulty": "easy",
        "knowledge_point": "functions",
        "description": "实现函数 fib(n)，返回前 n 项斐波那契数列（从 0 开始）。n>=1。",
        "example_input": "5",
        "example_output": "[0, 1, 1, 2, 3]",
        "test_cases": [
            {"input": "fib(5)", "expected": "[0, 1, 1, 2, 3]"},
            {"input": "fib(1)", "expected": "[0]"},
        ],
        "hints": [
            "前两项为 0、1，其后每项是前两项之和。",
            "用列表保存结果并迭代更新。",
        ],
    },
    {
        "title": "统计词频",
        "difficulty": "medium",
        "knowledge_point": "variables-types",
        "description": "实现函数 word_count(text)，返回字符串中每个单词出现次数的字典（忽略大小写，按空格切分）。",
        "example_input": "'Apple apple Banana'",
        "example_output": "{'apple': 2, 'banana': 1}",
        "test_cases": [
            {"input": "word_count('Apple apple Banana')", "expected": "{'apple': 2, 'banana': 1}"},
            {"input": "word_count('a b a c')", "expected": "{'a': 2, 'b': 1, 'c': 1}"},
        ],
        "hints": [
            "用 str.lower() 统一大小写。",
            "用 dict 计数，或 collections.Counter。",
        ],
    },
    {
        "title": "学生成绩等级",
        "difficulty": "medium",
        "knowledge_point": "class-object",
        "description": "定义 Student 类，含 name 与 scores（列表）。实现方法 average() 返回平均分，grade() 按平均分返回 A/B/C/D。",
        "example_input": "Student('小明', [90, 80, 70])",
        "example_output": "average=80.0, grade='B'",
        "test_cases": [
            {"input": "Student('x', [90, 80, 70]).grade()", "expected": "'B'"},
            {"input": "Student('x', [60, 60]).grade()", "expected": "'D'"},
        ],
        "hints": [
            "平均分 >=90 A，>=80 B，>=70 C，其余 D。",
            "在 __init__ 中保存属性，average 用 sum/len。",
        ],
    },
    {
        "title": "回文数判断",
        "difficulty": "easy",
        "knowledge_point": "condition-loop",
        "description": "实现函数 is_palindrome(n)，判断整数 n 是否为回文数（正读反读相同），返回 bool。",
        "example_input": 121,
        "example_output": "True",
        "test_cases": [
            {"input": "is_palindrome(121)", "expected": "True"},
            {"input": "is_palindrome(-121)", "expected": "False"},
            {"input": "is_palindrome(10)", "expected": "False"},
        ],
        "hints": [
            "负数一定不是回文。",
            "把数字转成字符串，与它的反转比较即可：str(n) == str(n)[::-1]。",
        ],
    },
    {
        "title": "列表去重并保持顺序",
        "difficulty": "easy",
        "knowledge_point": "variables-types",
        "description": "实现函数 dedup(lst)，去除列表中重复元素，但保留第一次出现的顺序。",
        "example_input": "[3,1,2,3,1]",
        "example_output": "[3, 1, 2]",
        "test_cases": [
            {"input": "dedup([3,1,2,3,1])", "expected": "[3, 1, 2]"},
            {"input": "dedup([])", "expected": "[]"},
            {"input": "dedup(['a','b','a','c'])", "expected": "['a', 'b', 'c']"},
        ],
        "hints": [
            "不能直接用 set()，会打乱顺序。",
            "用一个新列表，遍历原列表，元素不在新列表里才 append。",
        ],
    },
    {
        "title": "FizzBuzz",
        "difficulty": "easy",
        "knowledge_point": "condition-loop",
        "description": "实现函数 fizzbuzz(n)，返回 1..n 的列表，3 的倍数换 'Fizz'，5 的倍数换 'Buzz'，同时是 3 和 5 的倍数换 'FizzBuzz'。",
        "example_input": 15,
        "example_output": "[1, 2, 'Fizz', 4, 'Buzz', ...]",
        "test_cases": [
            {"input": "fizzbuzz(5)", "expected": "[1, 2, 'Fizz', 4, 'Buzz']"},
            {"input": "fizzbuzz(15)[-1]", "expected": "'FizzBuzz'"},
            {"input": "fizzbuzz(3)[2]", "expected": "'Fizz'"},
        ],
        "hints": [
            "先判断是否同时被 3 和 5 整除，再分别判断，顺序很重要。",
            "用列表 append 构造结果。",
        ],
    },
    {
        "title": "最大子数组和（Kadane）",
        "difficulty": "hard",
        "knowledge_point": "functions",
        "description": "实现函数 max_subarray(nums)，返回连续子数组（至少含一个元素）的最大和。",
        "example_input": "[-2,1,-3,4,-1,2,1,-5,4]",
        "example_output": "6",
        "test_cases": [
            {"input": "max_subarray([-2,1,-3,4,-1,2,1,-5,4])", "expected": "6"},
            {"input": "max_subarray([1])", "expected": "1"},
            {"input": "max_subarray([-1,-2,-3])", "expected": "-1"},
        ],
        "hints": [
            "维护当前连续和 cur，若 cur<0 则从下一个元素重新开始。",
            "用一个变量 best 记录全局最大值。",
        ],
    },
    {
        "title": "Pandas 分组均值",
        "difficulty": "medium",
        "knowledge_point": "pandas-basics",
        "description": "给定两列 DataFrame（group:str, value:float），实现函数 group_mean(df) 返回按 group 分组后 value 的均值（dict）。",
        "example_input": "DataFrame({'group':['A','A','B'], 'value':[10,20,30]})",
        "example_output": "{'A':15.0, 'B':30.0}",
        "test_cases": [
            {"input": "group_mean(pd.DataFrame({'group':['A','A','B'],'value':[10,20,30]}))", "expected": "{'A': 15.0, 'B': 30.0}"},
            {"input": "group_mean(pd.DataFrame({'group':['X'],'value':[5]}))", "expected": "{'X': 5.0}"},
        ],
        "hints": [
            "函数内部需要 import pandas as pd。",
            "用 df.groupby('group')['value'].mean().to_dict()。",
        ],
    },
]
