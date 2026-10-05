<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { listKnowledge, type KnowledgePoint } from '@/api/knowledge'
import CodeEditor from '@/components/CodeEditor.vue'

const points = ref<KnowledgePoint[]>([])
const activeId = ref<number | null>(null)

const groups = computed(() => {
  const map = new Map<string, KnowledgePoint[]>()
  for (const p of points.value) {
    const arr = map.get(p.category) || []
    arr.push(p)
    map.set(p.category, arr)
  }
  return Array.from(map.entries())
})

const active = computed(() => points.value.find((p) => p.id === activeId.value) || null)

const difficultyType: Record<string, string> = {
  easy: 'success',
  medium: 'warning',
  hard: 'danger',
}

onMounted(async () => {
  points.value = await listKnowledge()
  if (points.value.length) activeId.value = points.value[0].id
})
</script>

<template>
  <div class="py-container learn">
    <div class="learn-layout">
      <aside class="tree py-card">
        <div class="tree-title">基础层（必学）</div>
        <div v-for="[cat, items] in groups" :key="cat" class="tree-group">
          <div class="tree-cat">{{ cat }}</div>
          <div
            v-for="it in items"
            :key="it.id"
            class="tree-item"
            :class="{ active: it.id === activeId }"
            @click="activeId = it.id"
          >
            {{ it.title }}
          </div>
        </div>
      </aside>

      <section class="detail py-card" v-if="active">
        <div class="detail-head">
          <h2>{{ active.title }}</h2>
          <el-tag :type="(difficultyType[active.difficulty] as 'success' | 'warning' | 'danger') || 'info'">
            {{ active.difficulty === 'easy' ? '简单' : active.difficulty === 'medium' ? '中等' : '较难' }}
          </el-tag>
        </div>
        <div class="detail-content">{{ active.content }}</div>

        <h3 class="block-title">可运行示例</h3>
        <div class="example-box">
          <CodeEditor :model-value="active.example_code" language="python" :read-only="true" />
        </div>
      </section>

      <section class="detail py-card empty" v-else>
        <el-empty description="加载中…" />
      </section>
    </div>
  </div>
</template>

<style scoped lang="scss">
.learn-layout {
  display: grid;
  grid-template-columns: 260px 1fr;
  gap: 20px;
  align-items: start;
}
.tree {
  padding: 14px;
  position: sticky;
  top: 84px;
  max-height: calc(100vh - 110px);
  overflow-y: auto;
}
.tree-title {
  font-weight: 600;
  font-size: 13px;
  color: var(--primary);
  margin-bottom: 10px;
}
.tree-cat {
  font-size: 12px;
  color: var(--text-sub);
  margin: 12px 0 6px;
}
.tree-item {
  padding: 9px 12px;
  border-radius: 9px;
  cursor: pointer;
  font-size: 13.5px;
  color: var(--text-main);
  transition: all 0.18s;
}
.tree-item:hover {
  background: var(--el-color-primary-light-9);
}
.tree-item.active {
  background: linear-gradient(120deg, #2f6bff, #1e4fd6);
  color: #fff;
  font-weight: 500;
}
.detail {
  padding: 24px 28px;
  min-height: 420px;
}
.detail-head {
  display: flex;
  align-items: center;
  gap: 12px;
  h2 {
    margin: 0;
    font-size: 22px;
  }
}
.detail-content {
  white-space: pre-wrap;
  line-height: 1.85;
  color: var(--text-main);
  margin: 16px 0 8px;
}
.block-title {
  margin: 22px 0 10px;
  font-size: 16px;
}
.example-box {
  height: 280px;
  border: 1px solid rgba(31, 42, 61, 0.1);
  border-radius: 12px;
  overflow: hidden;
}
@media (max-width: 860px) {
  .learn-layout {
    grid-template-columns: 1fr;
  }
  .tree {
    position: static;
    max-height: none;
  }
}
</style>
