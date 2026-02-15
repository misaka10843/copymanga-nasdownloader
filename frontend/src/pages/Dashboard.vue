<template>
  <div class="dashboard-page">
    <div v-for="(siteSchema, siteKey) in schema" :key="siteKey" class="mb-10">
      <div class="d-flex align-center mb-6">
        <v-avatar class="mr-3" color="primary-lighten-5" size="40">
          <span class="text-primary font-weight-bold text-uppercase">{{ siteKey.substring(0, 2) }}</span>
        </v-avatar>
        <div>
          <h2 class="text-h6 font-weight-bold text-capitalize">{{ siteKey }}</h2>
          <div class="text-caption text-medium-emphasis">已订阅 {{ configData[siteKey]?.length || 0 }} 个内容</div>
        </div>
        <v-spacer></v-spacer>
        <v-btn
            class="hidden-xs"
            color="primary"
            prepend-icon="mdi-plus"
            rounded="pill"
            variant="tonal"
            @click="openAddDialog(siteKey)"
        >
          添加订阅
        </v-btn>
        <v-btn
            class="hidden-sm-and-up"
            color="primary"
            icon="mdi-plus"
            rounded="circle"
            size="small"
            variant="tonal"
            @click="openAddDialog(siteKey)"
        ></v-btn>
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
                    <div class="text-body-2 text-high-emphasis text-truncate">
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
            <template v-if="schema[dialog.site]">
              <v-col
                  v-for="(meta, fieldName) in schema[dialog.site].fields"
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
            </template>
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
  </div>
</template>

<script setup>
import {inject, onMounted, ref} from 'vue'
import axios from 'axios'

const showMsg = inject('showMsg')
const openConfirm = inject('openConfirm')

const schema = ref({})
const configData = ref({})

const dialog = ref({
  show: false,
  isEdit: false,
  site: '',
  index: -1,
  data: {}
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
  } catch (e) {
    showMsg('Dashboard初始化失败: ' + (e.response?.data?.detail || e.message), 'error')
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

const removeItem = async (siteKey, idx) => {
  const confirmed = await openConfirm('删除订阅', '确定要删除这个订阅吗？此操作无法撤销。')
  if (!confirmed) return

  configData.value[siteKey].splice(idx, 1)
  await saveToServer()
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
  } catch (e) {
    showMsg('保存失败', 'error')
  }
}

onMounted(init)
</script>

<style scoped>
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