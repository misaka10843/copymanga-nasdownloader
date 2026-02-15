<template>
  <v-card border class="fill-height rounded-xl d-flex flex-column" elevation="0" flat min-height="70vh">
    <v-toolbar class="border-b px-2" color="surface" density="compact">
      <v-icon class="ml-2" color="primary" start>mdi-text-box-outline</v-icon>
      <v-toolbar-title class="text-body-2 font-weight-bold">系统实时日志</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-switch
          v-model="autoScroll"
          color="primary"
          label="自动滚动"
          hide-details
          density="compact"
          class="mr-4"
      ></v-switch>
      <v-btn :loading="loadingLogs" color="primary" prepend-icon="mdi-refresh" variant="text" @click="fetchLogs(false)">刷新日志</v-btn>
    </v-toolbar>
    <div ref="logContainer" class="flex-grow-1 bg-grey-darken-4 pa-4 font-monospace overflow-y-auto" style="max-height: 75vh; white-space: pre-wrap; font-size: 13px; line-height: 1.4;">
      <div v-if="logs.length === 0" class="text-grey text-center mt-10">暂无日志或未获取</div>
      <div v-for="(line, i) in logs" :key="i" class="log-line">{{ line }}</div>
    </div>
  </v-card>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, inject } from 'vue'
import axios from 'axios'

const showMsg = inject('showMsg')
const logs = ref([])
const loadingLogs = ref(false)
const logContainer = ref(null)
const autoScroll = ref(true)
let pollingTimer = null

const fetchLogs = async (isBackground = false) => {
  if (!isBackground) loadingLogs.value = true
  try {
    const res = await axios.get('/api/logs')
    logs.value = res.data

    if (autoScroll.value) {
      await nextTick(() => {
        if (logContainer.value) {
          logContainer.value.scrollTop = logContainer.value.scrollHeight
        }
      })
    }
  } catch (e) {
    if (!isBackground) showMsg('获取日志失败', 'error')
  } finally {
    if (!isBackground) loadingLogs.value = false
  }
}

onMounted(() => {
  fetchLogs(false)
  pollingTimer = setInterval(() => {
    fetchLogs(true)
  }, 2000)
})

onUnmounted(() => {
  if (pollingTimer) clearInterval(pollingTimer)
})
</script>

<style scoped>
.font-monospace { font-family: 'Roboto Mono', monospace; }
</style>