<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { PluginOut, listPlugins, updatePlugin } from '@/api/plugins'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const plugins = ref<PluginOut[]>([])
const loading = ref(false)

onMounted(load)

async function load() {
  loading.value = true
  try {
    plugins.value = await listPlugins()
  } catch {
    /* ignore */
  } finally {
    loading.value = false
  }
}

async function toggle(p: PluginOut, val: boolean) {
  try {
    const r = await updatePlugin(p.name, { enabled: val })
    p.enabled = r.enabled
    ElMessage.success(val ? `已启用 ${p.name}` : `已停用 ${p.name}`)
  } catch {
    p.enabled = !val
  }
}
</script>

<template>
  <div class="py-container market">
    <h2 class="py-section-title">插件市场</h2>
    <p class="py-section-sub">
      轻量插件生态：启用模型 / 知识点 / 评测插件以扩展平台能力。当前为教师可管理。
      <span v-if="!userStore.isTeacher" class="tip">（示例中 demo-model 为内置模型插件，已自动注册）</span>
    </p>

    <el-button :loading="loading" @click="load">刷新</el-button>

    <el-skeleton v-if="loading" :rows="4" />
    <div v-else-if="!plugins.length" class="empty">暂无已加载插件</div>
    <div v-else class="grid">
      <div class="py-card plugin" v-for="p in plugins" :key="p.name">
        <div class="p-head">
          <div>
            <b>{{ p.display_name }}</b>
            <el-tag size="small" class="cat">{{ p.category }}</el-tag>
            <span class="ver">v{{ p.version }}</span>
          </div>
          <el-switch :model-value="p.enabled" @change="(v: any) => toggle(p, v)" />
        </div>
        <p class="desc">{{ p.description }}</p>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; margin-top: 14px; }
.plugin { padding: 16px 18px; }
.p-head { display: flex; justify-content: space-between; align-items: center; }
.cat { margin: 0 8px; }
.ver { font-size: 12px; color: var(--text-sub); }
.desc { color: var(--text-main); font-size: 13px; line-height: 1.6; margin: 10px 0 0; }
.tip { color: var(--text-sub); }
.empty { color: var(--text-sub); text-align: center; padding: 30px 0; }
@media (max-width: 860px) { .grid { grid-template-columns: 1fr; } }
</style>
