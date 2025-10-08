"""
定时任务管理模块
负责管理定投提醒的自动发送
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from flask import current_app
from app import db
from app.models import User, InvestmentReminder
from datetime import datetime, time
import requests
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_reminder_notification(reminder_id):
    """发送定投提醒通知 - 独立函数，避免序列化问题"""
    from app import create_app
    app = create_app()
    
    with app.app_context():
        try:
            # 获取提醒信息
            reminder = InvestmentReminder.query.get(reminder_id)
            if not reminder:
                logger.error(f"提醒不存在: {reminder_id}")
                return
            
            # 检查提醒是否启用
            if not reminder.is_active:
                logger.info(f"提醒已禁用，跳过发送: {reminder_id}")
                return
            
            # 获取用户信息
            user = User.query.get(reminder.user_id)
            if not user or not user.webhook_url:
                logger.error(f"用户webhook未配置: {reminder.user_id}")
                return
            
            # 构建提醒消息
            frequency_text = "每月" if reminder.frequency_type == 'monthly' else "每周"
            frequency_value_text = f"{reminder.frequency_value}日" if reminder.frequency_type == 'monthly' else f"星期{reminder.frequency_value}"
            
            message = {
                "msgtype": "text",
                "text": {
                    "content": f"【定投提醒】\n标的：{reminder.target.code} ({reminder.target.name})\n金额：¥{reminder.amount}\n频率：{frequency_text}{frequency_value_text}\n时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n请及时执行定投操作！"
                }
            }
            
            # 发送通知
            response = requests.post(user.webhook_url, json=message, timeout=10)
            if response.status_code == 200:
                logger.info(f"定投提醒发送成功: {reminder_id}")
            else:
                logger.error(f"定投提醒发送失败: {reminder_id}, 状态码: {response.status_code}")
                
        except Exception as e:
            logger.error(f"发送定投提醒失败: {e}")

class ReminderScheduler:
    """定投提醒定时任务管理器"""
    
    def __init__(self, app=None):
        self.scheduler = None
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """初始化调度器"""
        self.app = app
        
        # 配置作业存储
        jobstores = {
            'default': SQLAlchemyJobStore(url=app.config['SQLALCHEMY_DATABASE_URI'])
        }
        
        # 配置执行器
        executors = {
            'default': ThreadPoolExecutor(20)
        }
        
        # 配置作业默认参数
        job_defaults = {
            'coalesce': False,
            'max_instances': 3
        }
        
        # 创建调度器
        self.scheduler = BackgroundScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone='Asia/Shanghai'
        )
        
        # 启动调度器
        self.scheduler.start()
        logger.info("定时任务调度器已启动")
    
    def add_reminder_job(self, reminder):
        """添加定投提醒任务"""
        if not self.scheduler:
            logger.error("调度器未初始化")
            return False
        
        try:
            # 构建任务ID
            job_id = f"reminder_{reminder.id}"
            
            # 删除已存在的任务
            self.remove_reminder_job(reminder.id)
            
            # 构建cron表达式
            if reminder.frequency_type == 'monthly':
                # 每月定投：每月指定日期的指定时间
                trigger = CronTrigger(
                    day=reminder.frequency_value,
                    hour=int(reminder.reminder_time.split(':')[0]),
                    minute=int(reminder.reminder_time.split(':')[1]),
                    timezone='Asia/Shanghai'
                )
            elif reminder.frequency_type == 'weekly':
                # 每周定投：每周指定星期的指定时间
                trigger = CronTrigger(
                    day_of_week=reminder.frequency_value - 1,  # APScheduler中0=周一
                    hour=int(reminder.reminder_time.split(':')[0]),
                    minute=int(reminder.reminder_time.split(':')[1]),
                    timezone='Asia/Shanghai'
                )
            else:
                logger.error(f"不支持的频率类型: {reminder.frequency_type}")
                return False
            
            # 添加任务 - 使用独立函数而不是实例方法
            self.scheduler.add_job(
                func=send_reminder_notification,
                trigger=trigger,
                args=[reminder.id],
                id=job_id,
                name=f"定投提醒-{reminder.target.code}",
                replace_existing=True
            )
            
            logger.info(f"已添加定投提醒任务: {job_id}")
            return True
            
        except Exception as e:
            logger.error(f"添加定投提醒任务失败: {e}")
            return False
    
    def remove_reminder_job(self, reminder_id):
        """删除定投提醒任务"""
        if not self.scheduler:
            return False
        
        try:
            job_id = f"reminder_{reminder_id}"
            self.scheduler.remove_job(job_id)
            logger.info(f"已删除定投提醒任务: {job_id}")
            return True
        except Exception as e:
            logger.error(f"删除定投提醒任务失败: {e}")
            return False
    
    def update_reminder_job(self, reminder):
        """更新定投提醒任务"""
        return self.add_reminder_job(reminder)
    
    def sync_all_reminders(self):
        """同步所有活跃的定投提醒"""
        if not self.scheduler:
            logger.error("调度器未初始化")
            return
        
        try:
            # 获取所有活跃的提醒
            active_reminders = InvestmentReminder.query.filter_by(is_active=True).all()
            
            logger.info(f"开始同步 {len(active_reminders)} 个定投提醒")
            
            for reminder in active_reminders:
                self.add_reminder_job(reminder)
            
            logger.info("定投提醒同步完成")
            
        except Exception as e:
            logger.error(f"同步定投提醒失败: {e}")
    
    def get_job_status(self, reminder_id):
        """获取任务状态"""
        if not self.scheduler:
            return None
        
        try:
            job_id = f"reminder_{reminder_id}"
            job = self.scheduler.get_job(job_id)
            if job:
                return {
                    'id': job.id,
                    'name': job.name,
                    'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
                    'trigger': str(job.trigger)
                }
            return None
        except Exception as e:
            logger.error(f"获取任务状态失败: {e}")
            return None
    
    def shutdown(self):
        """关闭调度器"""
        if self.scheduler:
            self.scheduler.shutdown()
            logger.info("定时任务调度器已关闭")

# 全局调度器实例
scheduler = ReminderScheduler()
