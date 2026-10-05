<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import {
  myClasses,
  createClass,
  joinClass,
  type ClassOut,
} from '@/api/classes'

const router = useRouter()
const userStore = useUserStore()
const classes = ref<ClassOut[]>([])
const loading = ref(false)

const createVisible = ref(false)
const joinVisible = ref(false)
const newClass = ref({ class_name: '', major: '', description: '' })
const inviteCode = ref('')
const creating = ref(false)
const joining = ref(false)

const taught = ref<ClassOut[]>([])
const joined = ref<ClassOut[]>([])

function split() {
  taught.value = classes.value.filter((c) => c.teacher_id === userStore.profile?.id)
  joined.value = classes.value.filter((c) => c.teacher_id !== userStore.profile?.id)
}

async function load() {
  loading.value = true
  try {
    classes.value = await myClasses()
    split()
  } catch {
    /* ignore */
  } finally {
    loading.value = false
  }
}

async function onCreate() {
  if (!newClass.value.class_name) {
    ElMessage.warning('请填写班级名称')
    return
  }
  creating.value = true
  try {
    await createClass(newClass.value)
    ElMessage.success('班级已创建')
    createVisible.value = false
    newClass.value = { class_name: '', major: '', description: '' }
    await load()
  } catch {
    /* ignore */
  } finally {
    creating.value = false
  }
}

async function onJoin() {
  if (!inviteCode.value) {
    ElMessage.warning('请输入邀请码')
    return
  }
  joining.value = true
  try {
    await joinClass(inviteCode.value)
    ElMessage.success('加入成功')
    joinVisible.value = false
    inviteCode.value = ''
    await load()
  } catch {
    /* ignore */
  } finally {
    joining.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="py-container class-center">
    <div class="cc-head">
      <div>
        <h2 class="py-section-title">班级中心</h2>
        <p class="py-section-sub">创建班级、布置作业、查看学情；或以邀请码加入班级。</p>
      </div>
      <div class="cc-actions">
        <el-button @click="joinVisible = true">加入班级</el-button>
        <el-button type="primary" @click="createVisible = true">
          <el-icon><Plus /></el-icon>&nbsp;创建班级
        </el-button>
      </div>
    </div>

    <section v-if="taught.length" class="cc-block">
      <h3 class="cc-sub">我创建的班级</h3>
      <div class="cc-grid">
        <div v-for="c in taught" :key="c.id" class="cc-card py-card" @click="router.push(`/class/${c.id}`)">
          <div class="cc-card-top">
            <span class="cc-name">{{ c.class_name }}</span>
            <el-tag size="small" type="primary">教师</el-tag>
          </div>
          <div class="cc-meta">{{ c.major || '未设置专业' }}</div>
          <div class="cc-meta">邀请码：<b class="code">{{ c.invite_code }}</b> · {{ c.student_count }} 名学生</div>
          <div class="cc-desc">{{ c.description || '暂无描述' }}</div>
        </div>
      </div>
    </section>

    <section v-if="joined.length" class="cc-block">
      <h3 class="cc-sub">我加入的班级</h3>
      <div class="cc-grid">
        <div v-for="c in joined" :key="c.id" class="cc-card py-card" @click="router.push(`/class/${c.id}`)">
          <div class="cc-card-top">
            <span class="cc-name">{{ c.class_name }}</span>
            <el-tag size="small">学生</el-tag>
          </div>
          <div class="cc-meta">{{ c.major || '未设置专业' }}</div>
          <div class="cc-meta">{{ c.student_count }} 名同学在班</div>
        </div>
      </div>
    </section>

    <el-empty v-if="!loading && !classes.length" description="还没有班级，创建一个或输入邀请码加入吧" />

    <!-- 创建班级 -->
    <el-dialog v-model="createVisible" title="创建班级" width="460px">
      <el-form label-width="80px">
        <el-form-item label="班级名称"><el-input v-model="newClass.class_name" /></el-form-item>
        <el-form-item label="所属专业"><el-input v-model="newClass.major" placeholder="如：市场营销 / 金融" /></el-form-item>
        <el-form-item label="班级描述"><el-input v-model="newClass.description" type="textarea" :rows="3" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createVisible = false">取消</el-button>
        <el-button type="primary" :loading="creating" @click="onCreate">创建</el-button>
      </template>
    </el-dialog>

    <!-- 加入班级 -->
    <el-dialog v-model="joinVisible" title="加入班级" width="420px">
      <p class="py-section-sub">输入教师提供的 6 位邀请码：</p>
      <el-input v-model="inviteCode" maxlength="6" placeholder="6 位数字邀请码" size="large" />
      <template #footer>
        <el-button @click="joinVisible = false">取消</el-button>
        <el-button type="primary" :loading="joining" @click="onJoin">加入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped lang="scss">
.cc-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  margin-bottom: 18px;
}
.cc-actions { display: flex; gap: 10px; }
.cc-block { margin-bottom: 22px; }
.cc-sub { font-size: 15px; margin: 6px 0 14px; color: var(--text-main); }
.cc-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 16px;
}
.cc-card {
  padding: 18px 20px;
  cursor: pointer;
  transition: transform 0.15s, box-shadow 0.15s;
  &:hover { transform: translateY(-3px); box-shadow: 0 12px 28px rgba(47, 107, 255, 0.16); }
}
.cc-card-top { display: flex; align-items: center; justify-content: space-between; }
.cc-name { font-size: 16px; font-weight: 600; }
.cc-meta { font-size: 13px; color: var(--text-sub); margin-top: 8px; }
.cc-meta .code { font-family: monospace; color: var(--primary); letter-spacing: 2px; }
.cc-desc { font-size: 12px; color: var(--text-sub); margin-top: 10px; line-height: 1.6;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
</style>
