<template>
  <v-card class="cron-generator" border flat elevation="0">
    <div class="d-flex flex-row">
      <v-tabs v-model="activeTab" direction="vertical" color="primary" class="rounded-l-xl bg-grey-lighten-4">
        <v-tab value="minute">
          <v-icon start>mdi-clock-outline</v-icon>
          分
        </v-tab>
        <v-tab value="hour">
          <v-icon start>mdi-clock-time-four-outline</v-icon>
          时
        </v-tab>
        <v-tab value="day">
          <v-icon start>mdi-calendar-today</v-icon>
          日
        </v-tab>
        <v-tab value="month">
          <v-icon start>mdi-calendar-month</v-icon>
          月
        </v-tab>
        <v-tab value="week">
          <v-icon start>mdi-calendar-week</v-icon>
          周
        </v-tab>
      </v-tabs>

      <v-window v-model="activeTab" class="flex-grow-1 pa-4" style="min-height: 300px;">
        <v-window-item v-for="unit in timeUnits" :key="unit.value" :value="unit.value">
          <div class="text-h6 mb-4 font-weight-bold text-primary">{{ unit.label }}设置</div>
          <cron-unit-tab
              v-model="cronValues[unit.value]"
              :label="unit.label"
              :min="unit.min"
              :max="unit.max"
          />
        </v-window-item>
      </v-window>
    </div>

    <v-divider></v-divider>

    <div class="bg-primary-lighten-5 pa-4 d-flex align-center justify-space-between">
      <div>
        <div class="text-caption text-medium-emphasis">生成的 Cron 表达式 (分 时 日 月 周)</div>
        <div class="text-h5 font-weight-black font-monospace text-primary">{{ cronExpression }}</div>
      </div>
      <div class="text-body-2 text-right text-grey-darken-2">
        {{ humanReadable }}
      </div>
    </div>
  </v-card>
</template>

<script setup>
import {computed, onMounted, reactive, ref, watch} from 'vue'
import CronUnitTab from './CronUnitTab.vue'

const props = defineProps(['modelValue'])
const emit = defineEmits(['update:modelValue'])

const activeTab = ref('minute')

const timeUnits = [
  {value: 'minute', label: '分', min: 0, max: 59},
  {value: 'hour', label: '时', min: 0, max: 23},
  {value: 'day', label: '日', min: 1, max: 31},
  {value: 'month', label: '月', min: 1, max: 12},
  {value: 'week', label: '周', min: 0, max: 6},
]

const cronValues = reactive({
  minute: '30',
  hour: '2',
  day: '*',
  month: '*',
  week: '*'
})

onMounted(() => {
  if (props.modelValue) {
    const parts = props.modelValue.trim().split(/\s+/)
    if (parts.length === 5) {
      cronValues.minute = parts[0]
      cronValues.hour = parts[1]
      cronValues.day = parts[2]
      cronValues.month = parts[3]
      cronValues.week = parts[4]
    } else if (parts.length === 6) {
      cronValues.minute = parts[1]
      cronValues.hour = parts[2]
      cronValues.day = parts[3]
      cronValues.month = parts[4]
      cronValues.week = parts[5]
    }
  }
})

const cronExpression = computed(() => {
  return `${cronValues.minute} ${cronValues.hour} ${cronValues.day} ${cronValues.month} ${cronValues.week}`
})

const humanReadable = computed(() => {
  let text = []
  if (cronValues.day.includes('/')) text.push(`每隔 ${cronValues.day.split('/')[1]} 天`)
  else if (cronValues.day === '*') text.push("每天")
  else text.push(`${cronValues.day}日`)

  if (cronValues.hour !== '*') text.push(`${cronValues.hour}点`)
  if (cronValues.minute !== '*') text.push(`${cronValues.minute}分`)

  text.push("执行")
  return text.join(' ')
})

watch(cronExpression, (val) => {
  emit('update:modelValue', val)
})
</script>