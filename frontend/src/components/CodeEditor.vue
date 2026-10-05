<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import * as monaco from 'monaco-editor'
import editorWorker from 'monaco-editor/esm/vs/editor/editor.worker?worker'

// Python 仅需基础编辑 worker，无需语言服务 worker
;(self as unknown as { MonacoEnvironment: monaco.Environment }).MonacoEnvironment = {
  getWorker: () => new editorWorker(),
}

const props = defineProps<{
  modelValue: string
  language?: string
  readOnly?: boolean
}>()

const emit = defineEmits<{ (e: 'update:modelValue', v: string): void }>()

const el = ref<HTMLElement>()
let editor: monaco.editor.IStandaloneCodeEditor | null = null

onMounted(() => {
  if (!el.value) return
  editor = monaco.editor.create(el.value, {
    value: props.modelValue,
    language: props.language || 'python',
    theme: 'vs-dark',
    automaticLayout: true,
    minimap: { enabled: false },
    fontSize: 14,
    fontFamily: "'JetBrains Mono', 'Fira Code', Consolas, monospace",
    lineNumbers: 'on',
    scrollBeyondLastLine: false,
    tabSize: 4,
    renderWhitespace: 'none',
    readOnly: props.readOnly || false,
  })
  editor.onDidChangeModelContent(() => {
    emit('update:modelValue', editor!.getValue())
  })
})

watch(
  () => props.modelValue,
  (v) => {
    if (editor && v !== editor.getValue()) editor.setValue(v)
  },
)

watch(
  () => props.language,
  (lang) => {
    if (editor && lang) monaco.editor.setModelLanguage(editor.getModel()!, lang)
  },
)

onBeforeUnmount(() => {
  editor?.dispose()
  editor = null
})
</script>

<template>
  <div ref="el" class="code-editor"></div>
</template>

<style scoped>
.code-editor {
  width: 100%;
  height: 100%;
  border-radius: 12px;
  overflow: hidden;
}
</style>
