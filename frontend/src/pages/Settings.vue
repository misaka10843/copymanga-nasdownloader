<template>
  <div class="d-flex justify-center">
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
          <v-icon size="small" start>mdi-bell-ring</v-icon>
          消息推送 (Message Pusher)
        </div>

        <v-row>
          <v-col cols="12">
            <v-switch
                v-model="sysSettings.push_enable"
                color="primary"
                hide-details
                inset
                label="开启消息推送"
            ></v-switch>
          </v-col>

          <template v-if="sysSettings.push_enable">
            <v-col cols="12" md="8">
              <v-text-field
                  v-model="sysSettings.push_server"
                  density="comfortable"
                  label="服务器地址"
                  placeholder="http://..."
                  variant="outlined"
                  hint="Message Pusher 的部署地址"
              ></v-text-field>
            </v-col>
            <v-col cols="12" md="4">
              <v-text-field
                  v-model="sysSettings.push_user"
                  density="comfortable"
                  label="用户名"
                  variant="outlined"
              ></v-text-field>
            </v-col>
            <v-col cols="12">
              <v-text-field
                  v-model="sysSettings.push_token"
                  density="comfortable"
                  label="Token"
                  type="password"
                  variant="outlined"
              ></v-text-field>
            </v-col>

            <v-col cols="12" md="6">
              <v-switch
                  v-model="sysSettings.push_summary_only"
                  color="primary"
                  hide-details
                  inset
                  label="启用汇总模式 (推荐)"
              >
                <template v-slot:details>
                  任务结束后统一发送一条消息，包含更新列表和错误汇总。关闭则会实时推送每一条下载消息。
                </template>
              </v-switch>
            </v-col>
            <v-col cols="12" md="6">
              <v-switch
                  v-model="sysSettings.push_markdown"
                  color="primary"
                  hide-details
                  inset
                  label="启用 Markdown"
              ></v-switch>
            </v-col>
          </template>
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
</template>

<script setup>
import {ref, onMounted, inject} from 'vue'
import axios from 'axios'

const showMsg = inject('showMsg')
const sysSettings = ref({})
const savingSettings = ref(false)

const init = async () => {
  try {
    const res = await axios.get('/api/settings/system')
    sysSettings.value = res.data
  } catch (e) {
    showMsg('获取系统配置失败', 'error')
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
</script>