# server.py
import logging
import os
import json
import asyncio
from typing import Dict, Any, List

from fastapi import FastAPI, HTTPException, Body
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

import main
from utils import config, log as log_utils
from updater.updater import SITE_MAPPING

log_utils.configure_logging()
log = logging.getLogger("WebServer")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_FILE = os.path.join(config.DATA_PATH, "updater.json")
WEB_CONFIG_PATH = os.path.join(config.DATA_PATH, "web_config.json")

scheduler = BackgroundScheduler()


def run_downloader_task():
    log.info("触发下载任务...")
    try:
        main.main()
    except Exception as e:
        log.error(f"任务执行出错: {e}")


def load_schedule_config():
    if os.path.exists(WEB_CONFIG_PATH):
        try:
            with open(WEB_CONFIG_PATH, 'r') as f:
                return json.load(f)
        except:
            pass
    return {}


def save_schedule_config(cfg):
    with open(WEB_CONFIG_PATH, 'w') as f:
        json.dump(cfg, f)


@app.on_event("startup")
def init_scheduler():
    cfg = load_schedule_config()
    if cfg.get("type") == "interval":
        trigger_task(days=cfg.get("days", 0), hours=cfg.get("hours", 0), save=False)
    elif cfg.get("type") == "cron":
        pass
    scheduler.start()

@app.get("/api/schema")
def get_dynamic_schema():
    schema = {}
    for site_key, site_class in SITE_MAPPING.items():
        try:
            field_meta = site_class.get_field_meta()
            schema[site_key] = {
                "name": site_key,
                "fields": field_meta,
                "id_field": site_class.ID_FIELD
            }
        except Exception as e:
            log.error(f"生成站点 {site_key} 的Schema失败: {e}")
    return schema


@app.get("/api/config")
def get_config():
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        return {}


@app.post("/api/config")
def save_config(config_data: Dict[str, Any]):
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/run")
def manual_run():
    scheduler.add_job(run_downloader_task, trigger='date', run_date=datetime.now())
    return {"status": "started", "message": "任务已在后台启动"}


@app.post("/api/schedule/interval")
def set_interval_schedule(days: int = Body(0), hours: int = Body(0)):
    return trigger_task(days, hours, save=True)


def trigger_task(days, hours, save=True):
    scheduler.remove_all_jobs()

    if days == 0 and hours == 0:
        if save: save_schedule_config({"type": "none"})
        return {"status": "stopped", "message": "定时任务已关闭"}

    trigger = IntervalTrigger(days=days, hours=hours)
    scheduler.add_job(run_downloader_task, trigger, id="main_task")

    if save:
        save_schedule_config({"type": "interval", "days": days, "hours": hours})

    return {"status": "scheduled", "desc": f"每 {days} 天 {hours} 小时执行一次"}


@app.get("/api/logs")
def get_logs():
    log_dir = os.path.join(config.DATA_PATH, 'log')
    if not os.path.exists(log_dir): return []
    files = sorted([f for f in os.listdir(log_dir) if f.endswith('.log')])
    if not files: return []
    latest = files[-1]
    with open(os.path.join(log_dir, latest), 'r', encoding='utf-8') as f:
        # 只返回最后 100 行
        return f.readlines()[-100:]

if os.path.exists("spa_dist"):
    app.mount("/", StaticFiles(directory="spa_dist", html=True), name="static")

from datetime import datetime