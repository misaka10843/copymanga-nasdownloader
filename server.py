import logging
import os
import json
from datetime import datetime
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from pydantic import BaseModel
from typing import Dict, List, Optional

import main
from utils import config, log as log_utils

# 初始化日志配置
log_utils.configure_logging()
log = logging.getLogger("WebServer")

app = FastAPI(title="CopyManga NAS Downloader")


class AppState:
    is_running = False
    last_run_time = "未运行"
    next_run_time = "未设置"


state = AppState()
scheduler = BackgroundScheduler()

UPDATER_JSON_PATH = os.path.join(config.DATA_PATH, "updater.json")
WEB_CONFIG_PATH = os.path.join(config.DATA_PATH, "web_config.json")


def load_web_config():
    default_config = {"cron": "0 2 5 * *"}
    if os.path.exists(WEB_CONFIG_PATH):
        try:
            with open(WEB_CONFIG_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return default_config
    return default_config


def save_web_config(cfg):
    with open(WEB_CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, indent=2)


def run_downloader_task():
    if state.is_running:
        log.warning("任务正在运行中，跳过本次调度")
        return

    state.is_running = True
    state.last_run_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log.info(f"开始执行定时/手动下载任务...")

    try:
        main.main()
    except Exception as e:
        log.error(f"下载任务执行出错: {e}")
    finally:
        state.is_running = False
        log.info("下载任务执行结束")


def update_scheduler():
    cfg = load_web_config()
    cron_exp = cfg.get("cron", "0 2 * * *")

    scheduler.remove_all_jobs()
    try:
        parts = cron_exp.split()
        if len(parts) == 5:
            trigger = CronTrigger(
                minute=parts[0], hour=parts[1], day=parts[2], month=parts[3], day_of_week=parts[4]
            )
            scheduler.add_job(run_downloader_task, trigger, id="daily_download")
            state.next_run_time = str(trigger)
            log.info(f"定时任务已更新: {cron_exp}")
        else:
            log.error("Cron表达式格式错误，应为5位，如: 0 2 * * *")
    except Exception as e:
        log.error(f"设置定时任务失败: {e}")

scheduler.start()
update_scheduler()


class CronModel(BaseModel):
    cron: str

class UpdaterConfigModel(BaseModel):
    config: Dict


@app.get("/api/status")
async def get_status():
    """获取当前运行状态"""
    return {
        "is_running": state.is_running,
        "last_run": state.last_run_time,
        "next_run": state.next_run_time,
        "schedule": load_web_config().get("cron")
    }


@app.post("/api/run")
async def trigger_run(background_tasks: BackgroundTasks):
    """手动触发运行"""
    if state.is_running:
        raise HTTPException(status_code=400, detail="任务已在运行中")
    background_tasks.add_task(run_downloader_task)
    return {"message": "任务已开始后台运行"}


@app.get("/api/logs")
async def get_logs(lines: int = 100):
    """获取最新日志"""
    log_dir = os.path.join(config.DATA_PATH, 'log')
    if not os.path.exists(log_dir):
        return {"logs": ["日志目录不存在"]}

    files = [f for f in os.listdir(log_dir) if f.endswith('.log')]
    if not files:
        return {"logs": ["暂无日志文件"]}

    latest_log = sorted(files)[-1]
    log_path = os.path.join(log_dir, latest_log)

    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            content = f.readlines()
            return {"logs": content[-lines:], "filename": latest_log}
    except Exception as e:
        return {"logs": [f"读取日志失败: {e}"]}


@app.get("/api/config/updater")
async def get_updater_config():
    """读取 updater.json"""
    if not os.path.exists(UPDATER_JSON_PATH):
        return {}
    try:
        with open(UPDATER_JSON_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取配置失败: {e}")


@app.post("/api/config/updater")
async def save_updater_config(data: UpdaterConfigModel):
    """保存 updater.json"""
    try:
        with open(UPDATER_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(data.config, f, indent=2, ensure_ascii=False)
        return {"message": "配置已保存"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存配置失败: {e}")


@app.post("/api/config/schedule")
async def set_schedule(data: CronModel):
    """设置定时任务"""
    cfg = load_web_config()
    cfg['cron'] = data.cron
    save_web_config(cfg)
    update_scheduler()
    return {"message": "定时任务已更新", "next_run": state.next_run_time}

@app.get("/", response_class=HTMLResponse)
async def index():
    html_content = """
<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CopyManga NAS Downloader</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
    <script src="https://unpkg.com/axios/dist/axios.min.js"></script>
    <style>body { background-color: #f3f4f6; }</style>
</head>
<body>
    <div id="app" class="container mx-auto p-4 max-w-5xl">
        <header class="bg-white shadow rounded-lg p-6 mb-6 flex justify-between items-center">
            <div>
                <h1 class="text-2xl font-bold text-gray-800">CopyManga NAS Downloader</h1>
                <p class="text-gray-500 text-sm mt-1">Web 控制台</p>
            </div>
            <div class="flex items-center space-x-4">
                <span class="px-3 py-1 rounded-full text-sm font-semibold" 
                      :class="status.is_running ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'">
                    {{ status.is_running ? '运行中' : '空闲' }}
                </span>
                <button @click="triggerRun" :disabled="status.is_running" 
                        class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded disabled:opacity-50">
                    立即运行
                </button>
            </div>
        </header>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div class="space-y-6">
                <div class="bg-white shadow rounded-lg p-6">
                    <h2 class="text-lg font-semibold mb-4 border-b pb-2">运行状态</h2>
                    <div class="space-y-2 text-sm">
                        <p><span class="text-gray-500">上次运行:</span> {{ status.last_run }}</p>
                        <p><span class="text-gray-500">下次计划:</span> {{ status.next_run }}</p>
                        <div class="mt-4">
                            <label class="block text-gray-700 font-bold mb-2">定时任务 (Cron)</label>
                            <div class="flex space-x-2">
                                <input v-model="cronExpression" type="text" class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" placeholder="0 2 * * *">
                                <button @click="updateSchedule" class="bg-gray-600 hover:bg-gray-700 text-white px-3 rounded">保存</button>
                            </div>
                            <p class="text-xs text-gray-400 mt-1">格式: 分 时 日 月 周 (例如: 0 2 * * * 表示每天凌晨2点)</p>
                        </div>
                    </div>
                </div>

                <div class="bg-white shadow rounded-lg p-6 flex flex-col h-96">
                    <div class="flex justify-between items-center mb-4 border-b pb-2">
                         <h2 class="text-lg font-semibold">订阅配置 (JSON)</h2>
                         <button @click="saveConfig" class="text-sm bg-green-500 hover:bg-green-600 text-white px-2 py-1 rounded">保存更改</button>
                    </div>
                    <textarea v-model="configJsonStr" class="flex-1 w-full p-2 border rounded font-mono text-xs resize-none focus:outline-none focus:border-blue-500" spellcheck="false"></textarea>
                </div>
            </div>

            <div class="lg:col-span-2 bg-white shadow rounded-lg p-6 flex flex-col h-[calc(100vh-200px)] min-h-[500px]">
                <div class="flex justify-between items-center mb-4 border-b pb-2">
                    <h2 class="text-lg font-semibold">系统日志 <span class="text-xs font-normal text-gray-500">({{ logFilename }})</span></h2>
                    <button @click="fetchLogs" class="text-sm text-blue-500 hover:underline">刷新</button>
                </div>
                <div class="flex-1 bg-gray-900 text-gray-200 p-4 rounded overflow-auto font-mono text-xs whitespace-pre-wrap" ref="logContainer">
                    <div v-for="(line, index) in logs" :key="index">{{ line }}</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const { createApp, ref, onMounted, nextTick } = Vue
        createApp({
            setup() {
                const status = ref({ is_running: false, last_run: '-', next_run: '-' })
                const cronExpression = ref('')
                const configJsonStr = ref('{}')
                const logs = ref([])
                const logFilename = ref('')
                const logContainer = ref(null)

                const fetchStatus = async () => {
                    try {
                        const res = await axios.get('/api/status')
                        status.value = res.data
                        if (!cronExpression.value) cronExpression.value = res.data.schedule
                    } catch (e) { console.error(e) }
                }

                const fetchConfig = async () => {
                    try {
                        const res = await axios.get('/api/config/updater')
                        configJsonStr.value = JSON.stringify(res.data, null, 2)
                    } catch (e) { console.error(e) }
                }

                const saveConfig = async () => {
                    try {
                        const json = JSON.parse(configJsonStr.value)
                        await axios.post('/api/config/updater', { config: json })
                        alert('配置保存成功')
                    } catch (e) { 
                        alert('JSON 格式错误或保存失败: ' + e) 
                    }
                }

                const updateSchedule = async () => {
                    try {
                        await axios.post('/api/config/schedule', { cron: cronExpression.value })
                        alert('定时任务已更新')
                        fetchStatus()
                    } catch (e) { alert('更新失败') }
                }

                const triggerRun = async () => {
                    if (!confirm('确定要立即开始下载任务吗？')) return
                    try {
                        await axios.post('/api/run')
                        status.value.is_running = true
                        alert('任务已在后台启动，请查看日志')
                    } catch (e) { alert('启动失败: ' + e.response.data.detail) }
                }

                const fetchLogs = async () => {
                    try {
                        const res = await axios.get('/api/logs')
                        logs.value = res.data.logs
                        logFilename.value = res.data.filename
                        nextTick(() => {
                            if (logContainer.value) logContainer.value.scrollTop = logContainer.value.scrollHeight
                        })
                    } catch (e) { console.error(e) }
                }

                onMounted(() => {
                    fetchStatus()
                    fetchConfig()
                    fetchLogs()
                    // 自动刷新状态
                    setInterval(fetchStatus, 5000)
                    setInterval(fetchLogs, 10000)
                })

                return {
                    status, cronExpression, configJsonStr, logs, logFilename, logContainer,
                    saveConfig, updateSchedule, triggerRun, fetchLogs
                }
            }
        }).mount('#app')
    </script>
</body>
</html>
    """
    return html_content