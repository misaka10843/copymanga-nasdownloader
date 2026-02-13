<template>
  <v-app class="bg-background">
    <v-navigation-drawer v-model="drawer" rail expand-on-hover color="primary">
      <v-list density="compact" nav>
        <v-list-item prepend-icon="mdi-download-box" title="copymanga-downloader" subtitle="v2.0"
                     class="mb-4"></v-list-item>
        <v-divider class="mb-2"></v-divider>

        <v-list-item
            prepend-icon="mdi-view-dashboard"
            title="我的订阅"
            value="dashboard"
            @click="currentView = 'dashboard'"
            :active="currentView === 'dashboard'"
        ></v-list-item>

        <v-list-item
            prepend-icon="mdi-clock"
            title="定时任务"
            value="schedule"
            @click="currentView = 'schedule'"
            :active="currentView === 'schedule'"
        ></v-list-item>

        <v-list-item
            prepend-icon="mdi-code-json"
            title="高级配置"
            value="json"
            @click="currentView = 'json'"
            :active="currentView === 'json'"
        ></v-list-item>
      </v-list>

      <template v-slot:append>
        <v-list-item
            prepend-icon="mdi-github"
            title="GitHub"
            href="https://github.com/misaka10843/copymanga-nasdownloader"
            target="_blank"
        ></v-list-item>
      </template>
    </v-navigation-drawer>

    <v-app-bar flat color="background" class="px-4">
      <v-app-bar-title class="text-h6 font-weight-bold text-primary">
        {{ pageTitle }}
      </v-app-bar-title>
      <v-spacer></v-spacer>

      <v-btn
          prepend-icon="mdi-play"
          color="primary"
          variant="elevated"
          class="mr-4"
          :loading="running"
          @click="manualRun"
      >
        立即运行
      </v-btn>
    </v-app-bar>

    <v-main>
      <v-container fluid class="pa-6" style="max-width: 1600px;">

        <v-fade-transition mode="out-in">
          <div v-if="currentView === 'dashboard'" key="dashboard">
            <div v-for="(siteSchema, siteKey) in schema" :key="siteKey" class="mb-10">
              <div class="d-flex align-center mb-4 pl-2 border-s-lg border-primary">
                <h2 class="text-h5 font-weight-bold text-secondary ml-3 text-capitalize">{{ siteKey }}</h2>
                <v-chip class="ml-4 font-weight-bold" color="secondary" variant="flat" size="small">
                  {{ configData[siteKey]?.length || 0 }}
                </v-chip>
                <v-spacer></v-spacer>
                <v-btn
                    variant="text"
                    color="primary"
                    prepend-icon="mdi-plus"
                    @click="openAddDialog(siteKey)"
                >
                  添加订阅
                </v-btn>
              </div>

              <v-row>
                <v-col
                    v-for="(item, index) in configData[siteKey]"
                    :key="index"
                    cols="12" md="6" lg="4" xl="3"
                >
                  <v-card class="fill-height d-flex flex-column hover-card">
                    <v-card-item>
                      <template v-slot:prepend>
                        <v-avatar color="primary-lighten-4" icon="mdi-book-open-variant"
                                  class="text-primary"></v-avatar>
                      </template>
                      <v-card-title class="font-weight-bold">
                        {{ item.name || '未命名漫画' }}
                      </v-card-title>
                      <v-card-subtitle>
                        ID: {{ item[siteSchema.id_field] || '未设置' }}
                      </v-card-subtitle>
                    </v-card-item>

                    <v-divider></v-divider>

                    <v-card-text class="flex-grow-1 pt-4">
                      <v-row dense>
                        <v-col v-for="(meta, fieldName) in siteSchema.fields" :key="fieldName" :cols="meta.cols || 12">
                          <div v-if="!meta.advanced || item[fieldName]" class="mb-2">
                            <div class="text-caption text-medium-emphasis">{{ meta.label }}</div>
                            <div class="text-body-2 text-truncate">{{ item[fieldName] || '-' }}</div>
                          </div>
                        </v-col>
                      </v-row>
                    </v-card-text>

                    <v-divider></v-divider>

                    <v-card-actions>
                      <v-btn
                          variant="text"
                          color="primary"
                          prepend-icon="mdi-pencil"
                          @click="openEditDialog(siteKey, index)"
                      >编辑
                      </v-btn>
                      <v-spacer></v-spacer>
                      <v-btn
                          variant="text"
                          color="error"
                          icon="mdi-delete-outline"
                          @click="removeItem(siteKey, index)"
                      ></v-btn>
                    </v-card-actions>
                  </v-card>
                </v-col>

                <v-col v-if="!configData[siteKey]?.length" cols="12">
                  <v-sheet border rounded="xl" class="d-flex align-center justify-center py-10 bg-transparent"
                           style="border-style: dashed;">
                    <div class="text-center">
                      <v-icon size="48" color="grey-lighten-1" class="mb-2">mdi-folder-open-outline</v-icon>
                      <div class="text-grey">暂无订阅，点击上方按钮添加</div>
                    </div>
                  </v-sheet>
                </v-col>
              </v-row>
            </div>
          </div>

          <div v-else-if="currentView === 'schedule'" key="schedule" class="d-flex justify-center">
            <div style="width: 100%; max-width: 900px;">
              <div class="text-center mb-8">
                <v-icon size="64" color="primary" class="mb-4">mdi-clock-time-eight-outline</v-icon>
                <h2 class="text-h4 font-weight-bold text-secondary">定时下载策略</h2>
                <p class="text-body-1 text-grey mt-2">配置自动检查漫画更新的时间频率</p>
              </div>

              <cron-generator v-model="cronExpression" class="mb-6"></cron-generator>

              <div class="d-flex justify-center gap-4">
                <v-btn size="large" variant="tonal" @click="currentView = 'dashboard'">取消</v-btn>
                <v-btn size="large" color="primary" prepend-icon="mdi-content-save" @click="saveCron">保存策略</v-btn>
              </div>
            </div>
          </div>

          <div v-else-if="currentView === 'json'" key="json">
            <v-card class="fill-height">
              <v-toolbar color="surface" density="compact">
                <v-toolbar-title class="text-body-2">updater.json (直接编辑)</v-toolbar-title>
                <v-spacer></v-spacer>
                <v-btn icon="mdi-content-save" color="primary" @click="saveJson"></v-btn>
              </v-toolbar>
              <v-textarea
                  v-model="jsonStr"
                  variant="solo-filled"
                  hide-details
                  class="json-editor"
                  auto-grow
                  rows="25"
              ></v-textarea>
            </v-card>
          </div>
        </v-fade-transition>
      </v-container>
    </v-main>

    <v-dialog v-model="dialog.show" max-width="600px" scrollable>
      <v-card>
        <v-card-title class="bg-primary text-white py-4">
          {{ dialog.isEdit ? '编辑订阅' : '新增订阅' }}
          <v-chip class="ml-2" color="white" variant="outlined" size="small">{{ dialog.site }}</v-chip>
        </v-card-title>
        <v-card-text class="pt-4">
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
                  :hint="meta.advanced ? '高级选项' : ''"
                  persistent-hint
              ></v-text-field>
            </v-col>
          </v-row>
        </v-card-text>
        <v-divider></v-divider>
        <v-card-actions class="pa-4">
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="dialog.show = false">取消</v-btn>
          <v-btn color="primary" variant="flat" @click="saveDialog">保存</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-snackbar v-model="snackbar.show" :color="snackbar.color" location="top" timeout="3000">
      <div class="d-flex align-center">
        <v-icon :icon="snackbar.color === 'success' ? 'mdi-check-circle' : 'mdi-alert-circle'" class="mr-2"></v-icon>
        {{ snackbar.text }}
      </div>
    </v-snackbar>
  </v-app>
</template>

<script setup>
import {computed, onMounted, ref} from 'vue'
import axios from 'axios'
import CronGenerator from './components/CronGenerator.vue'

const drawer = ref(true)
const currentView = ref('dashboard')
const running = ref(false)
const schema = ref({})
const configData = ref({})
const jsonStr = ref('{}')
const cronExpression = ref('* * * * * *')
const snackbar = ref({show: false, text: '', color: 'success'})

// 对话框状态
const dialog = ref({
  show: false,
  isEdit: false,
  site: '',
  index: -1,
  data: {}
})

const pageTitle = computed(() => {
  const map = {dashboard: '仪表盘', schedule: '定时策略', json: 'JSON 编辑器'}
  return map[currentView.value]
})

const init = async () => {
  try {
    const [sRes, cRes] = await Promise.all([
      axios.get('/api/schema'),
      axios.get('/api/config')
    ])
    schema.value = sRes.data
    const data = cRes.data || {}
    for (const key in sRes.data) {
      if (!data[key]) data[key] = []
    }
    configData.value = data
    jsonStr.value = JSON.stringify(data, null, 2)
  } catch (e) {
    showMsg('数据加载失败: ' + e.message, 'error')
  }
}

const showMsg = (text, color = 'success') => {
  snackbar.value = {show: true, text, color}
}

const manualRun = async () => {
  running.value = true
  try {
    await axios.post('/api/run')
    showMsg('任务已在后台启动')
  } catch (e) {
    showMsg('启动失败', 'error')
  } finally {
    setTimeout(() => running.value = false, 2000)
  }
}

const removeItem = (siteKey, idx) => {
  if (!confirm('确定删除吗？')) return
  configData.value[siteKey].splice(idx, 1)
  saveToServer()
}

const openAddDialog = (siteKey) => {
  const fields = schema.value[siteKey].fields
  const newItem = {}
  for (const f in fields) {
    newItem[f] = fields[f].default || ''
  }

  dialog.value = {
    show: true,
    isEdit: false,
    site: siteKey,
    index: -1,
    data: newItem
  }
}

const openEditDialog = (siteKey, index) => {
  const item = JSON.parse(JSON.stringify(configData.value[siteKey][index]))
  dialog.value = {
    show: true,
    isEdit: true,
    site: siteKey,
    index: index,
    data: item
  }
}

const saveDialog = () => {
  const {site, index, isEdit, data} = dialog.value

  if (isEdit) {
    configData.value[site][index] = data
  } else {
    configData.value[site].push(data)
  }

  dialog.value.show = false
  saveToServer()
}

const saveToServer = async () => {
  try {
    await axios.post('/api/config', configData.value)
    showMsg('配置已保存')
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
    showMsg('定时策略已更新')
  } catch (e) {
    showMsg('更新失败', 'error')
  }
}

onMounted(init)
</script>

<style scoped>
.json-editor :deep(textarea) {
  font-family: 'Fira Code', 'Consolas', monospace !important;
  font-size: 13px;
  line-height: 1.5;
}

.hover-card {
  transition: transform 0.2s, box-shadow 0.2s;
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.hover-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1) !important;
}
</style>