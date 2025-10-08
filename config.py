import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """Flask应用配置"""
    
    # Flask基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # 数据库配置 - 使用绝对路径避免Flask自动创建instance目录
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///drip_invest.db'
    if DATABASE_URL.startswith('sqlite:///'):
        # 如果是相对路径，转换为绝对路径
        db_path = DATABASE_URL.replace('sqlite:///', '')
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.abspath(db_path)}'
    else:
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 服务器配置
    HOST = os.environ.get('HOST') or '127.0.0.1'
    PORT = int(os.environ.get('PORT') or 5006)
    
    # 日志配置
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    
    # 定时任务配置
    SCHEDULER_TIMEZONE = os.environ.get('SCHEDULER_TIMEZONE') or 'Asia/Shanghai'
    
    # 调试模式
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
