<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const primaryMenus = [
  { name: 'home', label: '首页' },
  { name: 'learn', label: '知识体系' },
  { name: 'practice', label: '训练场' },
  { name: 'prompt-train', label: 'AI 协作' },
  { name: 'interview', label: '面试真题' },
  { name: 'debug-train', label: '找 Bug' },
  { name: 'advisor', label: '规划师' },
  { name: 'cases', label: '案例库' },
  { name: 'class-center', label: '班级中心' },
]

const moreMenus = [
  { name: 'tutor', label: 'AI 陪练' },
  { name: 'rank', label: '排行榜' },
  { name: 'works', label: '作品墙' },
  { name: 'checkin', label: '打卡' },
  { name: 'plugins', label: '插件' },
]

const activeMenu = computed(() => route.name as string)

function onLogout() {
  userStore.logout()
  ElMessage.success('已退出登录')
  router.push('/')
}
</script>

<template>
  <div class="layout">
    <header class="topbar">
      <div class="py-container topbar-inner">
        <div class="brand" @click="router.push('/')">
          <div class="brand-logo">&lt;/&gt;</div>
          <div class="brand-text">
            <span class="brand-name">PyLearn <b>AI</b></span>
            <span class="brand-tag">开源 Python 智能学习平台</span>
          </div>
        </div>

        <nav class="nav">
          <router-link
            v-for="m in primaryMenus"
            :key="m.name"
            :to="{ name: m.name }"
            class="nav-item"
            :class="{ active: activeMenu === m.name }"
          >
            {{ m.label }}
          </router-link>
          <el-dropdown trigger="hover" class="more-dropdown">
            <span class="nav-item" :class="{ active: moreMenus.some((x) => x.name === activeMenu) }">
              更多<el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item
                  v-for="m in moreMenus"
                  :key="m.name"
                  @click="router.push({ name: m.name })"
                >{{ m.label }}</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </nav>

        <div class="actions">
          <el-button text :class="{ 'active-text': activeMenu === 'ai-settings' }" @click="router.push('/settings/ai')">
            <el-icon><Setting /></el-icon>
            <span>AI 设置</span>
          </el-button>
          <el-dropdown>
            <span class="avatar">
              <el-avatar :size="34" style="background: linear-gradient(120deg, #2f6bff, #00c2d1)">
                {{ userStore.displayName.slice(0, 1) }}
              </el-avatar>
              <span class="avatar-name">{{ userStore.displayName }}</span>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <template v-if="userStore.isLogin">
                  <el-dropdown-item @click="router.push('/profile')">个人中心</el-dropdown-item>
                  <el-dropdown-item @click="router.push('/class-center')">我的班级</el-dropdown-item>
                  <el-dropdown-item @click="router.push('/settings/ai')">AI 配置</el-dropdown-item>
                  <el-dropdown-item divided @click="onLogout">退出登录</el-dropdown-item>
                </template>
                <template v-else>
                  <el-dropdown-item @click="router.push('/login')">登录 / 注册</el-dropdown-item>
                </template>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </header>

    <main class="content">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>

    <footer class="footer">
      <div class="py-container footer-inner">
        <div class="footer-brand">
          <span class="brand-name">PyLearn <b>AI</b></span>
          <p>开源 · 免费 · 用户自备算力 · 支持私有化部署</p>
        </div>
        <div class="footer-links">
          <div>
            <h4>产品</h4>
            <span>知识体系</span><span>编程训练场</span><span>案例库</span>
          </div>
          <div>
            <h4>资源</h4>
            <span>快速开始</span><span>部署文档</span><span>插件开发</span>
          </div>
          <div>
            <h4>协议</h4>
            <span>MIT License</span><span>隐私优先</span>
          </div>
        </div>
      </div>
      <div class="footer-bottom">© 2026 PyLearn AI · 由社区驱动的开源学习平台</div>
    </footer>
  </div>
</template>

<style scoped lang="scss">
.layout {
  min-height: 100%;
  display: flex;
  flex-direction: column;
}
.topbar {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(255, 255, 255, 0.82);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(31, 42, 61, 0.08);
}
.topbar-inner {
  height: 64px;
  display: flex;
  align-items: center;
  gap: 28px;
}
.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
}
.brand-logo {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: grid;
  place-items: center;
  font-family: monospace;
  font-weight: 700;
  color: #fff;
  background: linear-gradient(120deg, #2f6bff, #00c2d1);
  box-shadow: 0 6px 16px rgba(47, 107, 255, 0.35);
}
.brand-text {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}
.brand-name {
  font-size: 18px;
  font-weight: 600;
  b {
    color: var(--primary);
  }
}
.brand-tag {
  font-size: 11px;
  color: var(--text-sub);
}
.nav {
  display: flex;
  gap: 2px;
  margin-left: 12px;
  white-space: nowrap;
}
.nav-item {
  padding: 7px 12px;
  border-radius: 8px;
  color: var(--text-sub);
  font-weight: 500;
  font-size: 13px;
  transition: all 0.2s;
  cursor: pointer;
}
.nav-item:hover {
  color: var(--primary);
  background: var(--el-color-primary-light-9);
}
.nav-item.active {
  color: #fff;
  background: linear-gradient(120deg, #2f6bff, #1e4fd6);
  box-shadow: 0 6px 16px rgba(47, 107, 255, 0.3);
}
.more-dropdown .nav-item {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}
.actions {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 12px;
}
.active-text {
  color: var(--primary);
}
.avatar {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  outline: none;
}
.avatar-name {
  font-size: 13px;
  color: var(--text-main);
}
.content {
  flex: 1;
  padding: 28px 0 48px;
}
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
.footer {
  background: #0f1b33;
  color: #c7d2e6;
  padding: 40px 0 0;
}
.footer-inner {
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 24px;
}
.footer-brand .brand-name {
  color: #fff;
  b {
    color: #6ea0ff;
  }
}
.footer-brand p {
  margin: 8px 0 0;
  font-size: 12px;
  color: #8a9bbd;
}
.footer-links {
  display: flex;
  gap: 56px;
  h4 {
    color: #fff;
    font-size: 14px;
    margin: 0 0 12px;
  }
  div {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  span {
    font-size: 13px;
    color: #8a9bbd;
    cursor: pointer;
  }
  span:hover {
    color: #c7d2e6;
  }
}
.footer-bottom {
  margin-top: 32px;
  padding: 16px 0;
  text-align: center;
  font-size: 12px;
  color: #6a7a9c;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}
@media (max-width: 860px) {
  .nav {
    display: none;
  }
}
</style>
