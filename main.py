from flask import Flask, render_template, redirect, url_for, session
from app import create_app
from app.models import db
from config import Config

app = create_app()

@app.route('/')
def index():
    """首页"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('auth.login'))

@app.route('/dashboard')
def dashboard():
    """仪表板"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    from app.models import InvestmentReminder, InvestmentRecord
    
    # 获取用户数据统计
    reminders_count = InvestmentReminder.query.filter_by(user_id=session['user_id']).count()
    records_count = InvestmentRecord.query.filter_by(user_id=session['user_id']).count()
    
    # 获取最近的定投记录
    recent_records = InvestmentRecord.query.filter_by(user_id=session['user_id'])\
        .order_by(InvestmentRecord.buy_date.desc()).limit(5).all()
    
    # 获取活跃的定投提醒
    active_reminders = InvestmentReminder.query.filter_by(
        user_id=session['user_id'], 
        is_active=True
    ).limit(5).all()
    
    return render_template('dashboard.html',
                         reminders_count=reminders_count,
                         records_count=records_count,
                         recent_records=recent_records,
                         active_reminders=active_reminders)

if __name__ == '__main__':
    # 使用配置文件中的HOST和PORT
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )