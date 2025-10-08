from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def create_app():
    """创建Flask应用"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # 初始化数据库
    db.init_app(app)
    
    # 注册蓝图
    from app.routes.auth import auth_bp
    from app.routes.reminder import reminder_bp
    from app.routes.record import record_bp
    from app.routes.analysis import analysis_bp
    from app.routes.target import target_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(reminder_bp, url_prefix='/reminder')
    app.register_blueprint(record_bp, url_prefix='/record')
    app.register_blueprint(analysis_bp, url_prefix='/analysis')
    app.register_blueprint(target_bp, url_prefix='/target')
    
    # 创建数据库表
    with app.app_context():
        # 导入所有模型以确保它们被注册
        from app.models import User, InvestmentReminder, InvestmentRecord, Target
        db.create_all()
    
    # 初始化定时任务调度器
    from app.scheduler import scheduler
    scheduler.init_app(app)
    
    # 同步所有活跃的定投提醒
    with app.app_context():
        scheduler.sync_all_reminders()
    
    return app
