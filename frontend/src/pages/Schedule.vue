<template>
  <div class="d-flex justify-center">
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
</template>

<script setup>
import {inject, onMounted, ref} from 'vue'
import axios from 'axios'
import CronGenerator from '../components/CronGenerator.vue'

const showMsg = inject('showMsg')
const cronExpression = ref('* * * * *')

const init = async () => {
  try {
    const res = await axios.get('/api/schedule/config')
    if (res.data && res.data.cron) {
      cronExpression.value = res.data.cron
    } else {
      cronExpression.value = '30 2 * * *'
    }
  } catch (e) {
    showMsg('获取定时任务失败', 'error')
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

onMounted(init)
</script>