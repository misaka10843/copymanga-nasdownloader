<template>
  <el-container class="layout-container">
    <el-header class="header">
      <div class="logo">CopyManga NAS</div>
      <div class="actions">
        <el-button type="primary" @click="manualRun" :loading="running">立即运行</el-button>
      </div>
    </el-header>

    <el-main>
      <el-row :gutter="20">
        <el-col :span="16">
          <el-card>
            <el-tabs v-model="activeTab">
              <el-tab-pane label="订阅管理 (Card)" name="card">
                <div v-if="loadingSchema" class="loading">加载插件定义中...</div>

                <div v-else v-for="(siteSchema, siteKey) in schema" :key="siteKey" class="site-section">
                  <div class="site-header">
                    <h3>{{ siteKey }}
                      <el-tag size="small">{{ configData[siteKey]?.length || 0 }}</el-tag>
                    </h3>
                    <el-button size="small" @click="addItem(siteKey)">新增订阅</el-button>
                  </div>

                  <el-collapse>
                    <el-collapse-item
                        v-for="(item, index) in configData[siteKey]"
                        :key="index"
                        :title="item.name || '未命名漫画'"
                    >
                      <el-form label-width="120px" size="small">
                        <el-form-item
                            v-for="(meta, fieldName) in siteSchema.fields"
                            :key="fieldName"
                            :label="meta.label || fieldName"
                        >
                          <el-input
                              v-if="meta.type === 'text' || !meta.type"
                              v-model="item[fieldName]"
                              :placeholder="meta.placeholder"
                          />
                          <el-alert v-else-if="meta.type === 'readonly'" :title="item[fieldName] || '暂无'" type="info"
                                    :closable="false"/>
                        </el-form-item>

                        <el-form-item>
                          <el-button type="danger" link @click="removeItem(siteKey, index)">删除此订阅</el-button>
                        </el-form-item>
                      </el-form>
                    </el-collapse-item>
                  </el-collapse>
                </div>
              </el-tab-pane>

              <el-tab-pane label="源码编辑 (JSON)" name="json">
                <el-input
                    v-model="jsonStr"
                    type="textarea"
                    :rows="20"
                    spellcheck="false"
                    class="json-editor"
                />
              </el-tab-pane>
            </el-tabs>

            <div class="save-bar">
              <el-button type="success" @click="saveConfig">保存配置</el-button>
            </div>
          </el-card>
        </el-col>

        <el-col :span="8">
          <el-card class="mb-20">
            <template #header>定时任务设置</template>
            <el-form label-width="80px">
              <el-form-item label="间隔天数">
                <el-input-number v-model="schedule.days" :min="0"/>
              </el-form-item>
              <el-form-item label="间隔小时">
                <el-input-number v-model="schedule.hours" :min="0" :max="23"/>
              </el-form-item>
              <el-button type="primary" class="w-full" @click="saveSchedule">应用定时设置</el-button>
              <div class="tips">设置为 0 天 0 小时即为关闭自动运行</div>
            </el-form>
          </el-card>

          <el-card>
            <template #header>运行日志</template>
            <div class="log-box">
              <div v-for="(line, i) in logs" :key="i" class="log-line">{{ line }}</div>
            </div>
            <el-button size="small" @click="fetchLogs" class="mt-10">刷新日志</el-button>
          </el-card>
        </el-col>
      </el-row>
    </el-main>
  </el-container>
</template>

<script setup>
import {onMounted, ref, watch} from 'vue'
import axios from 'axios'
import {ElMessage} from 'element-plus'

const activeTab = ref('card')
const schema = ref({})
const configData = ref({})
const jsonStr = ref('{}')
const loadingSchema = ref(true)
const running = ref(false)
const schedule = ref({days: 0, hours: 0})
const logs = ref([])

watch(activeTab, (val) => {
  if (val === 'json') {
    jsonStr.value = JSON.stringify(configData.value, null, 2)
  } else {
    try {
      configData.value = JSON.parse(jsonStr.value)
    } catch (e) {
      ElMessage.error('JSON 格式错误，无法切换回卡片模式')
      activeTab.value = 'json'
    }
  }
})

const fetchData = async () => {
  try {
    const schemaRes = await axios.get('/api/schema')
    schema.value = schemaRes.data

    const configRes = await axios.get('/api/config')
    const data = configRes.data || {}
    for (const site of Object.keys(schema.value)) {
      if (!data[site]) data[site] = []
    }
    configData.value = data
    jsonStr.value = JSON.stringify(data, null, 2)
  } catch (e) {
    console.error(e)
  } finally {
    loadingSchema.value = false
  }
}

const saveConfig = async () => {
  let payload = configData.value
  if (activeTab.value === 'json') {
    try {
      payload = JSON.parse(jsonStr.value)
    } catch (e) {
      return ElMessage.error('JSON 格式错误')
    }
  }

  await axios.post('/api/config', payload)
  ElMessage.success('配置已保存')
  fetchData()
}

const addItem = (siteKey) => {
  const newItem = {}
  const fields = schema.value[siteKey].fields
  for (const key in fields) {
    newItem[key] = fields[key].default || ''
  }
  if (!configData.value[siteKey]) configData.value[siteKey] = []
  configData.value[siteKey].push(newItem)
}

const removeItem = (siteKey, index) => {
  configData.value[siteKey].splice(index, 1)
}

const saveSchedule = async () => {
  await axios.post('/api/schedule/interval', schedule.value)
  ElMessage.success('定时任务已更新')
}

const manualRun = async () => {
  running.value = true
  try {
    await axios.post('/api/run')
    ElMessage.success('任务已开始')
  } finally {
    setTimeout(() => running.value = false, 2000)
  }
}

const fetchLogs = async () => {
  const res = await axios.get('/api/logs')
  logs.value = res.data
}

onMounted(() => {
  fetchData()
  fetchLogs()
})
</script>

<style>
.header {
  background: #fff;
  border-bottom: 1px solid #ddd;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo {
  font-size: 20px;
  font-weight: bold;
}

.site-section {
  margin-bottom: 20px;
}

.site-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  border-left: 4px solid #409EFF;
  padding-left: 10px;
}

.save-bar {
  margin-top: 20px;
  text-align: right;
}

.tips {
  font-size: 12px;
  color: #999;
  margin-top: 5px;
}

.log-box {
  background: #1e1e1e;
  color: #ddd;
  height: 300px;
  overflow-y: auto;
  padding: 10px;
  font-size: 12px;
  font-family: monospace;
}

.w-full {
  width: 100%;
}

.mb-20 {
  margin-bottom: 20px;
}

.mt-10 {
  margin-top: 10px;
}
</style>