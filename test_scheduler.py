#!/usr/bin/env python3
"""
测试定时任务设置和状态
"""

from main import app
from app import db
from app.models import User, InvestmentReminder, Target
from app.scheduler import scheduler
from datetime import datetime

def test_scheduler_status():
    """测试调度器状态"""
    print("🔍 检查调度器状态...")
    
    with app.app_context():
        # 获取所有提醒
        reminders = InvestmentReminder.query.filter_by(user_id=1, is_active=True).all()
        
        print(f"📋 找到 {len(reminders)} 个活跃提醒:")
        
        for reminder in reminders:
            print(f"\n📌 提醒 ID: {reminder.id}")
            print(f"   标的: {reminder.target.code if reminder.target else 'Unknown'}")
            print(f"   频率: {reminder.frequency_type} - {reminder.frequency_value}")
            print(f"   时间: {reminder.reminder_time}")
            print(f"   状态: {'启用' if reminder.is_active else '禁用'}")
            
            # 获取任务状态
            job_status = scheduler.get_job_status(reminder.id)
            if job_status:
                print(f"   ✅ 任务状态:")
                print(f"      ID: {job_status['id']}")
                print(f"      名称: {job_status['name']}")
                print(f"      下次执行: {job_status['next_run_time']}")
                print(f"      触发器: {job_status['trigger']}")
            else:
                print(f"   ❌ 任务未找到")
        
        # 显示所有任务
        print(f"\n📊 调度器中的所有任务:")
        if scheduler.scheduler:
            jobs = scheduler.scheduler.get_jobs()
            for job in jobs:
                print(f"   - {job.id}: {job.name}")
                print(f"     下次执行: {job.next_run_time}")
                print(f"     触发器: {job.trigger}")
        else:
            print("   调度器未初始化")

if __name__ == '__main__':
    test_scheduler_status()
