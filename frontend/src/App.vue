<template>
  <v-app class="bg-background">
    <v-navigation-drawer v-model="drawer" color="primary" expand-on-hover rail>
      <v-list density="compact" nav>
        <v-list-item class="mb-4" prepend-icon="mdi-download-box" subtitle="v2.0"
                     title="copymanga-downloader"></v-list-item>
        <v-divider class="mb-2 opacity-20"></v-divider>

        <v-list-item
            :active="currentView === 'dashboard'"
            prepend-icon="mdi-view-dashboard"
            rounded="xl"
            title="我的订阅"
            value="dashboard"
            @click="currentView = 'dashboard'"
        ></v-list-item>

        <v-list-item
            :active="currentView === 'logs'"
            prepend-icon="mdi-text-box-outline"
            rounded="xl"
            title="运行日志"
            value="logs"
            @click="currentView = 'logs'"
        ></v-list-item>

        <v-list-item
            :active="currentView === 'schedule'"
            prepend-icon="mdi-clock"
            rounded="xl"
            title="定时任务"
            value="schedule"
            @click="currentView = 'schedule'"
        ></v-list-item>

        <v-list-item
            :active="currentView === 'settings'"
            prepend-icon="mdi-cog"
            rounded="xl"
            title="系统设置"
            value="settings"
            @click="currentView = 'settings'"
        ></v-list-item>

        <v-list-item
            :active="currentView === 'json'"
            prepend-icon="mdi-code-json"
            rounded="xl"
            title="高级编辑"
            value="json"
            @click="currentView = 'json'"
        ></v-list-item>
      </v-list>

      <template v-slot:append>
        <v-list-item
            class="mb-2"
            href="https://github.com/misaka10843/copymanga-nasdownloader"
            prepend-icon="mdi-github"
            rounded="xl"
            target="_blank"
            title="GitHub"
        ></v-list-item>
      </template>
    </v-navigation-drawer>

    <v-app-bar class="px-4 border-b" color="background" flat>
      <v-app-bar-title class="text-h6 font-weight-bold text-primary">
        {{ pageTitle }}
      </v-app-bar-title>
      <v-spacer></v-spacer>

      <v-btn
          :loading="running"
          class="text-none"
          color="primary"
          prepend-icon="mdi-play"
          rounded="pill"
          variant="flat"
          @click="manualRun"
      >
        立即运行
      </v-btn>
    </v-app-bar>

    <v-main>
      <v-container class="pa-6" fluid style="max-width: 1600px;">

        <v-fade-transition mode="out-in">

          <div v-if="currentView === 'dashboard'" key="dashboard">
            <div v-for="(siteSchema, siteKey) in schema" :key="siteKey" class="mb-10">
              <div class="d-flex align-center mb-6">
                <v-avatar class="mr-3" color="primary-lighten-5" size="40">
                  <span class="text-primary font-weight-bold text-uppercase">{{ siteKey.substring(0, 2) }}</span>
                </v-avatar>
                <div>
                  <h2 class="text-h6 font-weight-bold text-capitalize">{{ siteKey }}</h2>
                  <div class="text-caption text-medium-emphasis">已订阅 {{ configData[siteKey]?.length || 0 }} 个内容
                  </div>
                </div>
                <v-spacer></v-spacer>
                <v-btn
                    color="primary"
                    prepend-icon="mdi-plus"
                    rounded="pill"
                    variant="tonal"
                    @click="openAddDialog(siteKey)"
                >
                  添加订阅
                </v-btn>
              </div>

              <v-row>
                <v-col
                    v-for="(item, index) in configData[siteKey]"
                    :key="index"
                    cols="12" lg="4" md="6" xl="3"
                >
                  <v-card border class="fill-height d-flex flex-column hover-card" elevation="0" flat>
                    <v-card-item>
                      <template v-slot:prepend>
                        <v-icon color="primary" icon="mdi-book-outline" size="large"></v-icon>
                      </template>
                      <v-card-title class="font-weight-bold text-body-1">
                        {{ item.name || '未命名漫画' }}
                      </v-card-title>
                      <v-card-subtitle class="text-caption font-monospace mt-1">
                        ID: {{ item[siteSchema.id_field] || 'N/A' }}
                      </v-card-subtitle>
                    </v-card-item>

                    <v-divider class="mx-4 opacity-10"></v-divider>

                    <v-card-text class="flex-grow-1 pt-4">
                      <v-row dense>
                        <v-col v-for="(meta, fieldName) in siteSchema.fields" :key="fieldName" :cols="meta.cols || 12">
                          <div v-if="!meta.advanced || item[fieldName]" class="mb-2">
                            <div class="text-caption text-medium-emphasis mb-1">{{ meta.label }}</div>
                            <div
                                class="text-body-2 text-high-emphasis text-truncate">
                              {{ item[fieldName] || '-' }}
                            </div>
                          </div>
                        </v-col>
                      </v-row>
                    </v-card-text>

                    <v-card-actions class="px-4 pb-4">
                      <v-btn
                          color="primary"
                          prepend-icon="mdi-pencil"
                          size="small"
                          variant="text"
                          @click="openEditDialog(siteKey, index)"
                      >编辑
                      </v-btn>
                      <v-spacer></v-spacer>
                      <v-btn
                          color="error"
                          icon="mdi-delete-outline"
                          size="small"
                          variant="text"
                          @click="removeItem(siteKey, index)"
                      ></v-btn>
                    </v-card-actions>
                  </v-card>
                </v-col>

                <v-col v-if="!configData[siteKey]?.length" cols="12">
                  <v-sheet border
                           class="d-flex align-center justify-center py-12 bg-transparent border-dashed text-medium-emphasis"
                           rounded="xl">
                    <div class="text-center">
                      <v-icon class="mb-3 opacity-50" size="48">mdi-inbox-outline</v-icon>
                      <div>暂无订阅数据</div>
                    </div>
                  </v-sheet>
                </v-col>
              </v-row>
            </div>
          </div>

          <div v-else-if="currentView === 'logs'" key="logs">
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
                <v-btn :loading="loadingLogs" color="primary" prepend-icon="mdi-refresh" variant="text"
                       @click="fetchLogs(false)">刷新日志
                </v-btn>
              </v-toolbar>
              <div
                  ref="logContainer"
                  class="flex-grow-1 bg-grey-darken-4 pa-4 font-monospace overflow-y-auto"
                  style="max-height: 75vh; white-space: pre-wrap; font-size: 13px; line-height: 1.4;"
              >
                <div v-if="logs.length === 0" class="text-grey text-center mt-10">暂无日志或未获取</div>
                <div v-for="(line, i) in logs" :key="i" class="log-line">{{ line }}</div>
              </div>
            </v-card>
          </div>

          <div v-else-if="currentView === 'schedule'" key="schedule" class="d-flex justify-center">
            <div style="width: 100%; max-width: 900px;">
              <v-card border class="rounded-xl pa-2" elevation="0" flat>
                <div class="text-center my-8">
                  <v-avatar class="mb-4" color="primary-lighten-5" size="80">
                    <v-icon color="primary" size="40">mdi-clock-time-eight-outline</v-icon>
                  </v-avatar>
                  <h2 class="text-h5 font-weight-bold">定时下载策略</h2>
                  <p class="text-body-2 text-medium-emphasis mt-2">配置自动检查漫画更新的时间频率</p>
                </div>

                <cron-generator v-model="cronExpression" class="mx-4 mb-6"></cron-generator>

                <div class="d-flex justify-center gap-4 mb-6">
                  <v-btn size="large" variant="text" @click="init">重置</v-btn>
                  <v-btn class="px-8" color="primary" prepend-icon="mdi-content-save" rounded="pill" size="large"
                         @click="saveCron">保存策略
                  </v-btn>
                </div>
              </v-card>
            </div>
          </div>

          <div v-else-if="currentView === 'settings'" key="settings" class="d-flex justify-center">
            <v-card border class="rounded-xl w-100" elevation="0" flat max-width="1000">
              <v-toolbar class="px-4 border-b" color="transparent">
                <v-toolbar-title class="text-h6 font-weight-bold">系统参数配置</v-toolbar-title>
                <v-spacer></v-spacer>
                <v-btn :loading="savingSettings" color="primary" variant="flat" @click="saveSystemSettings">
                  保存并生效
                </v-btn>
              </v-toolbar>

              <v-card-text class="pa-6">
                <v-alert border="start" class="mb-6 rounded-lg" icon="mdi-information" type="info" variant="tonal">
                  此处配置优先级高于环境变量 (.env)。修改后无需重启容器，后端热重载生效。
                </v-alert>

                <div class="text-subtitle-2 font-weight-bold text-primary mb-4 d-flex align-center">
                  <v-icon size="small" start>mdi-account-circle</v-icon>
                  CopyManga设置
                </div>
                <v-row>
                  <v-col cols="12" md="6">
                    <v-text-field v-model="sysSettings.cm_username" density="comfortable" label="用户名"
                                  variant="outlined"></v-text-field>
                  </v-col>
                  <v-col cols="12" md="6">
                    <v-text-field v-model="sysSettings.cm_password" density="comfortable" label="密码" type="password"
                                  variant="outlined"></v-text-field>
                  </v-col>
                  <v-col cols="12">
                    <v-text-field v-model="sysSettings.api_url" density="comfortable" label="API 地址"
                                  placeholder="https://api.mangacopy.com" variant="outlined"></v-text-field>
                  </v-col>
                  <v-col cols="12">
                    <v-text-field v-model="sysSettings.cm_proxy" density="comfortable" hint="留空则不使用代理"
                                  label="HTTP 代理" persistent-hint placeholder="http://127.0.0.1:7890"
                                  variant="outlined"></v-text-field>
                  </v-col>
                  <v-col cols="12">
                    <v-switch
                        v-model="sysSettings.use_cm_cname"
                        color="primary"
                        hide-details
                        inset
                        label="使用 CopyManga 原文章节名"
                    ></v-switch>
                  </v-col>
                </v-row>

                <v-divider class="my-6"></v-divider>

                <div class="text-subtitle-2 font-weight-bold text-primary mb-4 d-flex align-center">
                  <v-icon size="small" start>mdi-folder</v-icon>
                  存储与路径
                </div>
                <v-row>
                  <v-col cols="12">
                    <v-text-field v-model="sysSettings.download_path" density="comfortable" hint="Docker 容器内路径"
                                  label="下载暂存路径" persistent-hint variant="outlined"></v-text-field>
                  </v-col>
                  <v-col cols="12">
                    <v-text-field v-model="sysSettings.cbz_path" density="comfortable" hint="Docker 容器内路径"
                                  label="CBZ 输出路径" persistent-hint variant="outlined"></v-text-field>
                  </v-col>
                </v-row>

                <v-divider class="my-6"></v-divider>

                <div class="text-subtitle-2 font-weight-bold text-primary mb-4 d-flex align-center">
                  <v-icon size="small" start>mdi-tune</v-icon>
                  高级选项
                </div>
                <v-row align="center">
                  <v-col cols="12" md="6">
                    <v-select
                        v-model="sysSettings.log_level"
                        :items="['DEBUG', 'INFO', 'WARNING', 'ERROR']"
                        density="comfortable"
                        label="日志等级"
                        variant="outlined"
                    ></v-select>
                  </v-col>
                </v-row>
              </v-card-text>
            </v-card>
          </div>

          <div v-else-if="currentView === 'json'" key="json">
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
          </div>

        </v-fade-transition>
      </v-container>
    </v-main>

    <v-dialog v-model="dialog.show" max-width="600px" scrollable transition="dialog-bottom-transition">
      <v-card border class="rounded-xl" elevation="0" flat>
        <v-toolbar class="px-2 border-b" color="surface">
          <v-toolbar-title class="text-h6 font-weight-bold pl-4">
            {{ dialog.isEdit ? '编辑订阅' : '新增订阅' }}
            <span class="text-caption text-medium-emphasis ml-2">{{ dialog.site }}</span>
          </v-toolbar-title>
          <v-btn icon="mdi-close" variant="text" @click="dialog.show = false"></v-btn>
        </v-toolbar>

        <v-card-text class="pt-6">
          <v-row>
            <v-col
                v-for="(meta, fieldName) in schema[dialog.site]?.fields"
                :key="fieldName"
                :cols="meta.cols || 12"
            >
              <v-text-field
                  v-if="!meta.type || meta.type === 'text'"
                  v-model="dialog.data[fieldName]"
                  :label="meta.label"
                  :placeholder="meta.placeholder"
                  :readonly="meta.type === 'readonly'"
                  color="primary"
                  density="comfortable"
                  variant="outlined"
              >
                <template v-if="meta.advanced" v-slot:append-inner>
                  <v-tooltip location="top" text="高级选项">
                    <template v-slot:activator="{ props }">
                      <v-icon color="grey" size="small" v-bind="props">mdi-cog-outline</v-icon>
                    </template>
                  </v-tooltip>
                </template>
              </v-text-field>
            </v-col>
          </v-row>
        </v-card-text>

        <v-divider></v-divider>
        <v-card-actions class="pa-4 bg-surface">
          <v-spacer></v-spacer>
          <v-btn class="px-6" rounded="pill" variant="text" @click="dialog.show = false">取消</v-btn>
          <v-btn class="px-6" color="primary" rounded="pill" variant="flat" @click="saveDialog">保存</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-snackbar
        v-model="snackbar.show"
        :color="snackbar.color"
        elevation="4"
        location="top center"
        rounded="pill"
        timeout="3000"
    >
      <div class="d-flex align-center justify-center">
        <v-icon :icon="snackbar.color === 'success' ? 'mdi-check-circle' : 'mdi-alert-circle'" class="mr-2"></v-icon>
        <span class="font-weight-medium">{{ snackbar.text }}</span>
      </div>
    </v-snackbar>
  </v-app>
</template>

<script setup>
import {computed, nextTick, onMounted, onUnmounted, ref, watch} from 'vue'
import axios from 'axios'
import CronGenerator from './components/CronGenerator.vue'

const drawer = ref(true)
const currentView = ref('dashboard')
const running = ref(false)
const savingSettings = ref(false)
const schema = ref({})
const configData = ref({})
const sysSettings = ref({})
const jsonStr = ref('{}')
const cronExpression = ref('* * * * * *')
const snackbar = ref({show: false, text: '', color: 'success'})

// 日志相关
const logs = ref([])
const loadingLogs = ref(false)
const logContainer = ref(null)
const autoScroll = ref(true)
let pollingTimer = null

const dialog = ref({
  show: false,
  isEdit: false,
  site: '',
  index: -1,
  data: {}
})

const pageTitle = computed(() => {
  const map = {
    dashboard: '我的订阅',
    schedule: '定时任务策略',
    json: '高级配置编辑器',
    settings: '系统参数配置',
    logs: '运行日志监控'
  }
  return map[currentView.value]
})

watch(currentView, (newVal) => {
  if (newVal === 'logs') {
    fetchLogs(false)
    startLogPolling()
  } else {
    stopLogPolling()
  }
})

const startLogPolling = () => {
  stopLogPolling()
  pollingTimer = setInterval(() => {
    fetchLogs(true)
  }, 2000)
}

const stopLogPolling = () => {
  if (pollingTimer) {
    clearInterval(pollingTimer)
    pollingTimer = null
  }
}

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

const init = async () => {
  try {
    const [sRes, cRes, sysRes, schedRes] = await Promise.all([
      axios.get('/api/schema'),           // 表单结构
      axios.get('/api/config'),           // 订阅数据
      axios.get('/api/settings/system'),  // 系统配置
      axios.get('/api/schedule/config')   // 定时任务
    ])
    schema.value = sRes.data
    const data = cRes.data || {}
    for (const key in sRes.data) {
      if (!data[key]) data[key] = []
    }
    configData.value = data
    jsonStr.value = JSON.stringify(data, null, 2)

    sysSettings.value = sysRes.data

    if (schedRes.data && schedRes.data.cron) {
      cronExpression.value = schedRes.data.cron
    } else {
      cronExpression.value = '0 30 2 * * *'
    }

  } catch (e) {
    showMsg('初始化失败: ' + (e.response?.data?.detail || e.message), 'error')
  }
}

const showMsg = (text, color = 'success') => {
  snackbar.value = {show: true, text, color}
}

const manualRun = async () => {
  running.value = true
  try {
    await axios.post('/api/run')
    showMsg('后台任务已启动')
    // 如果当前在日志页，稍微延迟后刷新一下
    if (currentView.value === 'logs') {
      setTimeout(() => fetchLogs(true), 1000)
    }
  } catch (e) {
    showMsg('启动失败', 'error')
  } finally {
    setTimeout(() => running.value = false, 2000)
  }
}

const openAddDialog = (siteKey) => {
  const fields = schema.value[siteKey].fields
  const newItem = {}
  for (const f in fields) {
    newItem[f] = fields[f].default || ''
  }
  dialog.value = {show: true, isEdit: false, site: siteKey, index: -1, data: newItem}
}

const openEditDialog = (siteKey, index) => {
  const item = JSON.parse(JSON.stringify(configData.value[siteKey][index]))
  dialog.value = {show: true, isEdit: true, site: siteKey, index: index, data: item}
}

const removeItem = (siteKey, idx) => {
  if (!confirm('确定要删除这个订阅吗？此操作无法撤销。')) return
  configData.value[siteKey].splice(idx, 1)
  saveToServer()
}

const saveDialog = () => {
  const {site, index, isEdit, data} = dialog.value
  if (isEdit) configData.value[site][index] = data
  else configData.value[site].push(data)
  dialog.value.show = false
  saveToServer()
}

const saveToServer = async () => {
  try {
    await axios.post('/api/config', configData.value)
    showMsg('订阅配置已保存')
    jsonStr.value = JSON.stringify(configData.value, null, 2)
  } catch (e) {
    showMsg('保存失败', 'error')
  }
}

const saveJson = async () => {
  try {
    configData.value = JSON.parse(jsonStr.value)
    await saveToServer()
  } catch (e) {
    showMsg('JSON 格式错误', 'error')
  }
}

const saveCron = async () => {
  try {
    await axios.post('/api/schedule/cron', {cron: cronExpression.value})
    showMsg('定时策略已保存并应用')
  } catch (e) {
    showMsg('保存 Cron 失败', 'error')
  }
}

const saveSystemSettings = async () => {
  savingSettings.value = true
  try {
    await axios.post('/api/settings/system', sysSettings.value)
    showMsg('系统配置已生效')
  } catch (e) {
    showMsg('保存系统配置失败', 'error')
  } finally {
    savingSettings.value = false
  }
}

onMounted(init)
onUnmounted(() => {
  stopLogPolling()
})
</script>

<style scoped>
.json-editor :deep(.v-field__input) {
  font-family: 'Fira Code', 'Roboto Mono', monospace !important;
  font-size: 13px;
  line-height: 1.5;
  color: #333;
}

.border-dashed {
  border-style: dashed !important;
}

.hover-card {
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.hover-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 30px -10px rgba(0, 0, 0, 0.15) !important;
  border-color: rgba(var(--v-theme-primary), 0.3) !important;
}

.font-monospace {
  font-family: 'Roboto Mono', monospace;
}
</style>