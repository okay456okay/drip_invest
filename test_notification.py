#!/usr/bin/env python3
"""
立即测试定投提醒通知
"""

from main import app
from app import db
from app.models import User, InvestmentReminder, Target
from app.scheduler import send_reminder_notification
from datetime import datetime

def test_immediate_notification():
    """立即测试通知发送"""
    print("🚀 立即测试定投提醒通知...")
    
    with app.app_context():
        # 获取admin用户的提醒
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            print("❌ 未找到admin用户")
            return
        
        print(f"👤 用户: {admin_user.username}")
        print(f"📱 Webhook: {admin_user.webhook_url}")
        
        # 获取用户的活跃提醒
        reminders = InvestmentReminder.query.filter_by(user_id=admin_user.id, is_active=True).all()
        
        if not reminders:
            print("❌ 没有找到活跃的提醒")
            return
        
        print(f"📋 找到 {len(reminders)} 个活跃提醒")
        
        for reminder in reminders:
            print(f"\n📌 测试提醒 ID: {reminder.id}")
            print(f"   标的: {reminder.target.code if reminder.target else 'Unknown'}")
            print(f"   频率: {reminder.frequency_type} - {reminder.frequency_value}")
            print(f"   时间: {reminder.reminder_time}")
            
            # 立即发送通知
            print("📤 正在发送测试通知...")
            try:
                send_reminder_notification(reminder.id)
                print("✅ 通知发送完成")
            except Exception as e:
                print(f"❌ 通知发送失败: {e}")

if __name__ == '__main__':
    test_immediate_notification()
