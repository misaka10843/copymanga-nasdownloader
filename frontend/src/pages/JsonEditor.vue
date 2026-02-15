<template>
  <v-card border class="fill-height rounded-xl" elevation="0" flat>
    <v-toolbar class="border-b px-2" color="surface" density="compact">
      <v-icon class="ml-2" color="primary" start>mdi-code-json</v-icon>
      <v-toolbar-title class="text-body-2 font-weight-bold">updater.json (直接编辑)</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn color="primary" variant="text" @click="saveJson">保存更改</v-btn>
    </v-toolbar>
    <v-textarea
        v-model="jsonStr"
        auto-grow
        class="json-editor pa-0"
        flat
        hide-details
        rows="25"
        variant="solo"
    ></v-textarea>
  </v-card>
</template>

<script setup>
import {ref, onMounted, inject} from 'vue'
import axios from 'axios'

const showMsg = inject('showMsg')
const jsonStr = ref('{}')

const init = async () => {
  try {
    const res = await axios.get('/api/config')
    jsonStr.value = JSON.stringify(res.data || {}, null, 2)
  } catch (e) {
    showMsg('获取JSON失败', 'error')
  }
}

const saveJson = async () => {
  try {
    const data = JSON.parse(jsonStr.value)
    await axios.post('/api/config', data)
    showMsg('JSON 配置已保存')
  } catch (e) {
    showMsg('JSON 格式错误或保存失败', 'error')
  }
}

onMounted(init)
</script>

<style scoped>
.json-editor :deep(.v-field__input) {
  font-family: 'Fira Code', 'Roboto Mono', monospace !important;
  font-size: 13px;
  line-height: 1.5;
  color: #333;
}
</style>