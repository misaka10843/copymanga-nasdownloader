<template>
  <v-app class="bg-background">
    <v-navigation-drawer
        v-model="drawer"
        :location="$vuetify.display.mobile ? 'bottom' : undefined"
        :permanent="!$vuetify.display.mobile"
        :rail="!$vuetify.display.mobile && rail"
        :temporary="$vuetify.display.mobile"
        expand-on-hover
        color="primary"
    >
      <v-list density="compact" nav>
        <v-list-item
            prepend-icon="mdi-download-box"
            title="Copymanga"
            subtitle="v2.0"
            class="mb-4"
        ></v-list-item>
        <v-divider class="mb-2 opacity-20"></v-divider>

        <v-list-item
            v-for="item in menuItems"
            :key="item.value"
            :active="currentView === item.value"
            :prepend-icon="item.icon"
            :title="item.title"
            :value="item.value"
            rounded="xl"
            @click="currentView = item.value"
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

    <v-app-bar class="px-2 border-b" color="background" flat>
      <v-app-bar-nav-icon v-if="$vuetify.display.mobile" @click="drawer = !drawer"></v-app-bar-nav-icon>

      <v-app-bar-title class="text-h6 font-weight-bold text-primary pl-2">
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
        <span class="hidden-xs">立即运行</span>
        <span class="hidden-sm-and-up">运行</span>
      </v-btn>
    </v-app-bar>

    <v-main>
      <v-container class="pa-4 pa-md-6" fluid style="max-width: 1600px;">
        <v-fade-transition mode="out-in">
          <component :is="currentPageComponent" key="view" />
        </v-fade-transition>
      </v-container>
    </v-main>

    <v-dialog v-model="confirmState.show" max-width="400" persistent>
      <v-card class="rounded-xl pa-4" elevation="0" border>
        <div class="d-flex align-center mb-4">
          <v-icon color="warning" icon="mdi-alert-circle-outline" size="large" class="mr-3"></v-icon>
          <span class="text-h6 font-weight-bold">{{ confirmState.title }}</span>
        </div>
        <div class="text-body-1 text-medium-emphasis mb-6 pl-1">
          {{ confirmState.content }}
        </div>
        <div class="d-flex justify-end gap-2">
          <v-btn
              class="px-4"
              color="primary"
              variant="text"
              rounded="pill"
              @click="handleConfirm(false)"
          >
            取消
          </v-btn>
          <v-btn
              class="px-4"
              color="error"
              variant="flat"
              rounded="pill"
              @click="handleConfirm(true)"
          >
            确定删除
          </v-btn>
        </div>
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
import { computed, ref, provide, reactive } from 'vue'
import axios from 'axios'
import { useDisplay } from 'vuetify'

import Dashboard from './pages/Dashboard.vue'
import Logs from './pages/Logs.vue'
import Schedule from './pages/Schedule.vue'
import Settings from './pages/Settings.vue'
import JsonEditor from './pages/JsonEditor.vue'

const { mobile } = useDisplay()

const drawer = ref(!mobile.value)
const rail = ref(true)
const currentView = ref('dashboard')
const running = ref(false)
const snackbar = ref({show: false, text: '', color: 'success'})

const confirmState = reactive({
  show: false,
  title: '确认',
  content: '',
  resolve: null
})

// 菜单配置
const menuItems = [
  { title: '我的订阅', value: 'dashboard', icon: 'mdi-view-dashboard', component: Dashboard },
  { title: '运行日志', value: 'logs', icon: 'mdi-text-box-outline', component: Logs },
  { title: '定时任务', value: 'schedule', icon: 'mdi-clock', component: Schedule },
  { title: '系统设置', value: 'settings', icon: 'mdi-cog', component: Settings },
  { title: '高级编辑', value: 'json', icon: 'mdi-code-json', component: JsonEditor },
]

const currentPageComponent = computed(() => {
  const item = menuItems.find(i => i.value === currentView.value)
  return item ? item.component : Dashboard
})

const pageTitle = computed(() => {
  const item = menuItems.find(i => i.value === currentView.value)
  return item ? item.title : 'Dashboard'
})

const showMsg = (text, color = 'success') => {
  snackbar.value = {show: true, text, color}
}
provide('showMsg', showMsg)

const openConfirm = (title, content) => {
  confirmState.title = title
  confirmState.content = content
  confirmState.show = true
  return new Promise((resolve) => {
    confirmState.resolve = resolve
  })
}

const handleConfirm = (result) => {
  confirmState.show = false
  if (confirmState.resolve) {
    confirmState.resolve(result)
    confirmState.resolve = null
  }
}
provide('openConfirm', openConfirm)

const manualRun = async () => {
  running.value = true
  try {
    await axios.post('/api/run')
    showMsg('后台任务已启动')
  } catch (e) {
    showMsg('启动失败', 'error')
  } finally {
    setTimeout(() => running.value = false, 2000)
  }
}
</script>

<style>
html { overflow-y: auto; }
</style>