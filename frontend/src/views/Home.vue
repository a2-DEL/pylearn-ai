<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const features = [
  {
    name: 'learn',
    icon: 'Reading',
    title: '知识体系',
    desc: '三级知识架构，从变量循环到 Pandas 可视化，配套可运行示例与常见坑点。',
    color: '#2F6BFF',
  },
  {
    name: 'practice',
    icon: 'Monitor',
    title: '编程训练场',
    desc: 'Monaco 编辑器在线写代码，一键运行，AI 实时答疑与分步提示。',
    color: '#00C2D1',
  },
  {
    name: 'advisor',
    icon: 'Guide',
    title: '学习规划师',
    desc: '告诉 AI 你的专业与目标，生成模块权重、阶段计划与推荐案例。',
    color: '#7C5CFF',
  },
  {
    name: 'prompt-train',
    icon: 'Cpu',
    title: 'AI 协作训练',
    desc: '四种模式：需求拆解、Prompt 编程、找 Bug、结对编程，对接企业 AI Coding 面试。',
    color: '#F59E0B',
  },
  {
    name: 'debug-train',
    icon: 'Bug',
    title: '找 Bug 实战',
    desc: 'AI 埋雷你来排雷，测试用例全过才揭示参考答案，模拟真实 code review。',
    color: '#E5484D',
  },
  {
    name: 'class-center',
    icon: 'School',
    title: '班级教学',
    desc: '教师建班布置作业，自动批改与学情看板；学生凭邀请码加入。',
    color: '#16A34A',
  },
]

const steps = [
  { t: '配置 AI', d: '在「AI 设置」填入你的 API Key（也可先用 Mock 体验）' },
  { t: '挑选练习', d: '从知识体系或训练场选择题目，或浏览趣味案例' },
  { t: '编码运行', d: '在 Monaco 编辑器中编写并运行 Python 代码' },
  { t: 'AI 辅导', d: '报错即问 AI，获取思路而非答案，真正掌握' },
]
</script>

<template>
  <div class="home">
    <section class="hero">
      <div class="py-container hero-inner">
        <div class="hero-text">
          <span class="badge">开源 · MIT · 用户自备算力</span>
          <h1>
            用 <span class="py-gradient-text">AI 协作</span><br />
            学好 Python 编程
          </h1>
          <p class="hero-sub">
            PyLearn AI 是面向零基础与进阶学习者的开源智能学习平台。
            在线写代码、即时运行、AI 答疑与双轨训练，浏览器里即可开始。
          </p>
          <div class="hero-actions">
            <el-button type="primary" size="large" @click="router.push('/practice')">
              <el-icon><Monitor /></el-icon>&nbsp;进入训练场
            </el-button>
            <el-button size="large" @click="router.push('/learn')">
              <el-icon><Reading /></el-icon>&nbsp;浏览知识体系
            </el-button>
          </div>
          <div class="hero-stats">
            <div><b>19+</b><span>知识点 / 案例</span></div>
            <div><b>4</b><span>AI 协作训练模式</span></div>
            <div><b>0</b><span>内置收费逻辑</span></div>
          </div>
        </div>
        <div class="hero-art">
          <div class="code-window">
            <div class="code-bar">
              <span></span><span></span><span></span>
              <em>main.py</em>
            </div>
            <pre class="code-content"><code><span class="c-kw">def</span> <span class="c-fn">fib</span>(n):
    a, b = <span class="c-num">0</span>, <span class="c-num">1</span>
    <span class="c-kw">for</span> _ <span class="c-kw">in</span> <span class="c-fn">range</span>(n):
        a, b = b, a + b
    <span class="c-kw">return</span> a

<span class="c-fn">print</span>(<span class="c-fn">fib</span>(<span class="c-num">10</span>))  <span class="c-com"># 55</span></code></pre>
          </div>
          <div class="float-chip c1"><el-icon><ChatDotRound /></el-icon> AI 答疑</div>
          <div class="float-chip c2"><el-icon><MagicStick /></el-icon> 思路提示</div>
        </div>
      </div>
    </section>

    <section class="py-container blocks">
      <h2 class="py-section-title">四大核心能力</h2>
      <p class="py-section-sub">独立编程与 AI 协作并重，匹配当下企业需求</p>
      <div class="feature-grid">
        <div
          v-for="f in features"
          :key="f.name"
          class="py-card feature"
          @click="router.push({ name: f.name })"
        >
          <div class="feature-icon" :style="{ background: f.color + '1a', color: f.color }">
            <el-icon :size="26"><component :is="f.icon" /></el-icon>
          </div>
          <h3>{{ f.title }}</h3>
          <p>{{ f.desc }}</p>
          <span class="feature-link">立即体验 →</span>
        </div>
      </div>
    </section>

    <section class="py-container blocks">
      <h2 class="py-section-title">四步快速开始</h2>
      <p class="py-section-sub">无需本地环境，开箱即用</p>
      <div class="steps">
        <div v-for="(s, i) in steps" :key="i" class="step py-card">
          <div class="step-no">{{ i + 1 }}</div>
          <h4>{{ s.t }}</h4>
          <p>{{ s.d }}</p>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped lang="scss">
.hero {
  background: radial-gradient(1200px 500px at 80% -10%, rgba(0, 194, 209, 0.18), transparent),
    radial-gradient(900px 500px at 0% 0%, rgba(47, 107, 255, 0.18), transparent);
  padding: 56px 0 64px;
}
.hero-inner {
  display: flex;
  align-items: center;
  gap: 40px;
  flex-wrap: wrap;
}
.hero-text {
  flex: 1;
  min-width: 320px;
}
.badge {
  display: inline-block;
  padding: 6px 14px;
  border-radius: 999px;
  background: #fff;
  color: var(--primary);
  font-size: 12px;
  font-weight: 600;
  box-shadow: var(--shadow-card);
}
.hero-text h1 {
  font-size: 44px;
  line-height: 1.2;
  margin: 18px 0 14px;
  font-weight: 700;
}
.hero-sub {
  color: var(--text-sub);
  font-size: 16px;
  max-width: 520px;
  line-height: 1.7;
}
.hero-actions {
  margin: 26px 0;
  display: flex;
  gap: 14px;
}
.hero-stats {
  display: flex;
  gap: 36px;
  div {
    display: flex;
    flex-direction: column;
  }
  b {
    font-size: 26px;
    color: var(--primary);
  }
  span {
    font-size: 12px;
    color: var(--text-sub);
  }
}
.hero-art {
  position: relative;
  width: 420px;
  max-width: 100%;
}
.code-window {
  background: #0f1b33;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 24px 60px rgba(15, 27, 51, 0.4);
}
.code-bar {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 12px 14px;
  background: #16223f;
  span {
    width: 11px;
    height: 11px;
    border-radius: 50%;
    background: #ff5f57;
    &:nth-child(2) {
      background: #febc2e;
    }
    &:nth-child(3) {
      background: #28c840;
    }
  }
  em {
    margin-left: 10px;
    color: #8a9bbd;
    font-style: normal;
    font-size: 12px;
  }
}
.code-content {
  margin: 0;
  padding: 18px;
  font-family: 'JetBrains Mono', Consolas, monospace;
  font-size: 13.5px;
  line-height: 1.7;
  color: #e6edf7;
  .c-kw {
    color: #ff7edb;
  }
  .c-fn {
    color: #82aaff;
  }
  .c-num {
    color: #f78c6c;
  }
  .c-com {
    color: #637777;
  }
}
.float-chip {
  position: absolute;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border-radius: 12px;
  background: #fff;
  box-shadow: var(--shadow-hover);
  font-size: 13px;
  font-weight: 600;
  color: var(--primary);
  animation: floaty 3s ease-in-out infinite;
}
.float-chip.c1 {
  top: -16px;
  right: -10px;
}
.float-chip.c2 {
  bottom: -16px;
  left: -10px;
  color: var(--accent);
  animation-delay: 1.2s;
}
@keyframes floaty {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-8px);
  }
}
.blocks {
  margin-top: 56px;
}
.feature-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 18px;
}
.feature {
  padding: 22px;
  cursor: pointer;
  h3 {
    margin: 14px 0 8px;
    font-size: 17px;
  }
  p {
    color: var(--text-sub);
    font-size: 13px;
    line-height: 1.6;
    min-height: 62px;
  }
}
.feature-icon {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  display: grid;
  place-items: center;
}
.feature-link {
  color: var(--primary);
  font-size: 13px;
  font-weight: 600;
}
.steps {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 18px;
}
.step {
  padding: 20px;
  .step-no {
    width: 34px;
    height: 34px;
    border-radius: 10px;
    display: grid;
    place-items: center;
    background: linear-gradient(120deg, #2f6bff, #00c2d1);
    color: #fff;
    font-weight: 700;
    margin-bottom: 12px;
  }
  h4 {
    margin: 0 0 6px;
    font-size: 15px;
  }
  p {
    margin: 0;
    color: var(--text-sub);
    font-size: 13px;
    line-height: 1.6;
  }
}
@media (max-width: 980px) {
  .feature-grid,
  .steps {
    grid-template-columns: repeat(2, 1fr);
  }
  .hero-text h1 {
    font-size: 34px;
  }
}
</style>
