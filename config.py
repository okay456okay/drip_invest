import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """Flask应用配置"""
    
    # Flask基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///instance/drip_invest.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 服务器配置
    HOST = os.environ.get('HOST') or '127.0.0.1'
    PORT = int(os.environ.get('PORT') or 5000)
    
    # 日志配置
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    
    # 定时任务配置
    SCHEDULER_TIMEZONE = os.environ.get('SCHEDULER_TIMEZONE') or 'Asia/Shanghai'
    
    # 调试模式
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
