<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const mode = ref<'login' | 'register'>('login')
const loading = ref(false)
const form = reactive({
  username: '',
  password: '',
  email: '',
  roles: 'student',
})

async function submit() {
  if (!form.username || !form.password) {
    ElMessage.warning('请填写用户名与密码')
    return
  }
  if (mode.value === 'register' && form.password.length < 8) {
    ElMessage.warning('密码至少 8 位')
    return
  }
  loading.value = true
  try {
    if (mode.value === 'login') {
      await userStore.login(form.username, form.password)
      ElMessage.success('登录成功')
    } else {
      await userStore.register({ username: form.username, password: form.password, email: form.email || undefined, roles: form.roles })
      ElMessage.success('注册成功')
    }
    const redirect = (route.query.redirect as string) || '/'
    router.replace(redirect)
  } catch {
    /* 拦截器已提示 */
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth-page">
    <div class="auth-card py-card">
      <div class="auth-brand">
        <div class="brand-logo">&lt;/&gt;</div>
        <span class="brand-name">PyLearn <b>AI</b></span>
      </div>
      <el-tabs v-model="mode" class="auth-tabs">
        <el-tab-pane label="登录" name="login" />
        <el-tab-pane label="注册" name="register" />
      </el-tabs>

      <el-form label-position="top" @submit.prevent="submit">
        <el-form-item label="用户名">
          <el-input v-model="form.username" placeholder="自己起一个用户名，至少 3 位" size="large" />
        </el-form-item>
        <el-form-item v-if="mode === 'register'" label="邮箱（可选）">
          <el-input v-model="form.email" placeholder="用于找回密码" size="large" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" show-password placeholder="至少 8 位，数字字母均可" size="large" />
        </el-form-item>
        <el-form-item v-if="mode === 'register'" label="身份">
          <el-radio-group v-model="form.roles">
            <el-radio value="student">学生</el-radio>
            <el-radio value="teacher">教师</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-button type="primary" size="large" class="auth-submit" :loading="loading" @click="submit">
          {{ mode === 'login' ? '登录' : '注册并登录' }}
        </el-button>
      </el-form>
      <p class="auth-tip">游客可免登录使用训练场与 AI 答疑；注册后可加入班级、同步学习与配置。</p>
    </div>
  </div>
</template>

<style scoped lang="scss">
.auth-page {
  min-height: calc(100vh - 124px);
  display: grid;
  place-items: center;
  background: linear-gradient(160deg, #eef3ff, #f6fbff);
  padding: 40px 16px;
}
.auth-card {
  width: 420px;
  max-width: 100%;
  padding: 28px 30px 24px;
}
.auth-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
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
}
.brand-name {
  font-size: 18px;
  font-weight: 600;
  b { color: var(--primary); }
}
.auth-tabs {
  margin: 8px 0 4px;
}
.auth-submit {
  width: 100%;
  margin-top: 6px;
}
.auth-tip {
  margin-top: 16px;
  font-size: 12px;
  color: var(--text-sub);
  text-align: center;
  line-height: 1.6;
}
</style>
