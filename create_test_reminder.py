#!/usr/bin/env python3
"""
设置即将执行的测试任务
"""

from main import app
from app import db
from app.models import User, InvestmentReminder, Target
from app.scheduler import scheduler
from datetime import datetime, timedelta

def create_test_reminder():
    """创建一个即将执行的测试提醒"""
    print("🔧 创建测试提醒...")
    
    with app.app_context():
        # 获取admin用户
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            print("❌ 未找到admin用户")
            return
        
        # 获取第一个标的
        target = Target.query.filter_by(user_id=admin_user.id).first()
        if not target:
            print("❌ 未找到标的")
            return
        
        # 计算1分钟后的时间
        now = datetime.now()
        test_time = now + timedelta(minutes=1)
        
        print(f"⏰ 设置测试时间: {test_time.strftime('%H:%M')}")
        
        # 创建测试提醒
        test_reminder = InvestmentReminder(
            user_id=admin_user.id,
            target_id=target.id,
            amount=1000.00,
            frequency_type='weekly',
            frequency_value=test_time.weekday() + 1,  # 当前星期
            reminder_time=test_time.strftime('%H:%M'),
            is_active=True
        )
        
        try:
            db.session.add(test_reminder)
            db.session.commit()
            
            # 添加定时任务
            scheduler.add_reminder_job(test_reminder)
            
            print(f"✅ 测试提醒创建成功，ID: {test_reminder.id}")
            print(f"📅 将在 {test_time.strftime('%Y-%m-%d %H:%M:%S')} 执行")
            
            # 显示任务状态
            job_status = scheduler.get_job_status(test_reminder.id)
            if job_status:
                print(f"📊 任务状态:")
                print(f"   下次执行: {job_status['next_run_time']}")
                print(f"   触发器: {job_status['trigger']}")
            
        except Exception as e:
            print(f"❌ 创建失败: {e}")
            db.session.rollback()

if __name__ == '__main__':
    create_test_reminder()
