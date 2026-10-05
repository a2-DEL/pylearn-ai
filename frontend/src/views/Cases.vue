<script setup lang="ts">
import { ref } from 'vue'

interface CaseItem {
  title: string
  category: string
  difficulty: string
  duration: string
  desc: string
  points: string
}

const categories = ['全部', '趣味可视化', '办公自动化', '网络爬虫', '数据分析', '小游戏', 'AI 应用']
const activeCat = ref('全部')

const cases: CaseItem[] = [
  { title: '黑客代码雨', category: '趣味可视化', difficulty: 'easy', duration: '20 分钟', desc: '用字符下落模拟《黑客帝国》代码雨，理解循环与终端控制。', points: 'while / 随机 / 终端输出' },
  { title: '爱心函数', category: '趣味可视化', difficulty: 'easy', duration: '15 分钟', desc: '用隐函数绘制跳动爱心，浪漫又练手。', points: '数学函数 / 打印排版' },
  { title: '贪吃蛇游戏', category: '小游戏', difficulty: 'medium', duration: '45 分钟', desc: '终端版贪吃蛇，掌握键盘监听与游戏主循环。', points: '列表 / 循环 / 状态机' },
  { title: '二维码生成器', category: '办公自动化', difficulty: 'easy', duration: '15 分钟', desc: '一键把文字/链接生成二维码图片。', points: '第三方库 / 文件输出' },
  { title: '简历词云', category: '数据分析', difficulty: 'medium', duration: '30 分钟', desc: '读取简历文本生成词云，直观看关键词分布。', points: 'jieba 分词 / wordcloud' },
  { title: '天气爬虫', category: '网络爬虫', difficulty: 'medium', duration: '35 分钟', desc: '抓取公开天气数据并保存为 CSV。', points: 'requests / BeautifulSoup' },
  { title: 'Excel 报表自动化', category: '办公自动化', difficulty: 'medium', duration: '30 分钟', desc: '批量生成带样式的 Excel 周报。', points: 'openpyxl / 循环写入' },
  { title: 'AI 文本摘要', category: 'AI 应用', difficulty: 'hard', duration: '40 分钟', desc: '调用大模型 API 对长文做摘要，体验 AI 协作。', points: 'API 调用 / 提示词' },
  { title: 'NumPy 数组运算', category: '数据分析', difficulty: 'medium', duration: '25 分钟', desc: '向量化计算学生成绩均值与标准差，理解 ndarray 与广播。', points: 'np.array / 向量化' },
  { title: 'Pandas 数据清洗', category: '数据分析', difficulty: 'medium', duration: '30 分钟', desc: '读取成绩表，处理缺失值并按平均分排名。', points: 'DataFrame / groupby' },
]

const filtered = ref(cases)
function pick(c: string) {
  activeCat.value = c
  filtered.value = c === '全部' ? cases : cases.filter((x) => x.category === c)
}
pick('全部')

const dialogVisible = ref(false)
const current = ref<CaseItem | null>(null)
function openCase(c: CaseItem) {
  current.value = c
  dialogVisible.value = true
}
</script>

<template>
  <div class="py-container cases">
    <h2 class="py-section-title">趣味案例库</h2>
    <p class="py-section-sub">边玩边学，覆盖可视化 / 爬虫 / 数据分析 / 小游戏 / AI 应用</p>

    <div class="cats">
      <button
        v-for="c in categories"
        :key="c"
        class="cat"
        :class="{ active: activeCat === c }"
        @click="pick(c)"
      >
        {{ c }}
      </button>
    </div>

    <div class="grid">
      <div v-for="c in filtered" :key="c.title" class="py-card card" @click="openCase(c)">
        <div class="card-top">
          <span class="cat-tag">{{ c.category }}</span>
          <span class="diff" :class="c.difficulty">{{ c.difficulty === 'easy' ? '简单' : c.difficulty === 'medium' ? '中等' : '较难' }}</span>
        </div>
        <h3>{{ c.title }}</h3>
        <p>{{ c.desc }}</p>
        <div class="card-foot">
          <span>⏱ {{ c.duration }}</span>
          <span class="points">{{ c.points }}</span>
        </div>
      </div>
    </div>

    <el-dialog v-model="dialogVisible" :title="current?.title" width="520px">
      <template v-if="current">
        <el-tag>{{ current.category }}</el-tag>
        <p class="dlg-desc">{{ current.desc }}</p>
        <el-descriptions :column="1" border size="small">
          <el-descriptions-item label="难度">{{ current.difficulty === 'easy' ? '简单' : current.difficulty === 'medium' ? '中等' : '较难' }}</el-descriptions-item>
          <el-descriptions-item label="预计时长">{{ current.duration }}</el-descriptions-item>
          <el-descriptions-item label="知识点">{{ current.points }}</el-descriptions-item>
        </el-descriptions>
        <div class="dlg-tip">
          提示：在「编程训练场」新建文件，粘贴代码后即可运行体验。
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped lang="scss">
.cats {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 22px;
}
.cat {
  padding: 8px 16px;
  border-radius: 999px;
  border: 1px solid rgba(31, 42, 61, 0.12);
  background: #fff;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
}
.cat:hover {
  border-color: var(--primary);
  color: var(--primary);
}
.cat.active {
  background: linear-gradient(120deg, #2f6bff, #1e4fd6);
  color: #fff;
  border-color: transparent;
}
.grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 18px;
}
.card {
  padding: 20px;
  cursor: pointer;
  h3 {
    margin: 12px 0 8px;
    font-size: 17px;
  }
  p {
    color: var(--text-sub);
    font-size: 13px;
    line-height: 1.6;
    min-height: 56px;
  }
}
.card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.cat-tag {
  font-size: 12px;
  color: var(--primary);
  background: var(--el-color-primary-light-9);
  padding: 3px 10px;
  border-radius: 8px;
}
.diff {
  font-size: 12px;
  padding: 3px 8px;
  border-radius: 8px;
  &.easy {
    color: #16a34a;
    background: #e7f6ec;
  }
  &.medium {
    color: #d97706;
    background: #fef3e2;
  }
  &.hard {
    color: #e5484d;
    background: #fdeced;
  }
}
.card-foot {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--text-sub);
  margin-top: 10px;
}
.points {
  color: var(--primary);
}
.dlg-desc {
  margin: 14px 0;
  line-height: 1.7;
  color: var(--text-main);
}
.dlg-tip {
  margin-top: 14px;
  padding: 10px 12px;
  background: var(--el-color-primary-light-9);
  border-radius: 8px;
  font-size: 13px;
  color: var(--text-sub);
}
@media (max-width: 980px) {
  .grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
@media (max-width: 640px) {
  .grid {
    grid-template-columns: 1fr;
  }
}
</style>
