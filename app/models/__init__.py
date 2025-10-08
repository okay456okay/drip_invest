from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from decimal import Decimal

class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    webhook_url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    reminders = db.relationship('InvestmentReminder', backref='user', lazy=True, cascade='all, delete-orphan')
    records = db.relationship('InvestmentRecord', backref='user', lazy=True, cascade='all, delete-orphan')
    targets = db.relationship('Target', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'webhook_url': self.webhook_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class InvestmentReminder(db.Model):
    """定投提醒模型"""
    __tablename__ = 'investment_reminders'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    target_id = db.Column(db.Integer, db.ForeignKey('targets.id'), nullable=False)  # 标的ID
    amount = db.Column(db.Numeric(10, 2), nullable=False)  # 定投金额
    frequency_type = db.Column(db.String(10), nullable=False)  # monthly/weekly
    frequency_value = db.Column(db.Integer, nullable=False)  # 1-31日 或 1-7星期
    reminder_time = db.Column(db.String(5), default='09:00')  # 提醒时间，默认9点，格式HH:MM
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    target = db.relationship('Target', backref='reminders')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'target_id': self.target_id,
            'target_code': self.target.code if self.target else '',
            'target_name': self.target.name if self.target else '',
            'amount': float(self.amount),
            'frequency_type': self.frequency_type,
            'frequency_value': self.frequency_value,
            'reminder_time': self.reminder_time or '09:00',
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class InvestmentRecord(db.Model):
    """定投记录模型"""
    __tablename__ = 'investment_records'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    target_id = db.Column(db.Integer, db.ForeignKey('targets.id'), nullable=False)  # 标的ID
    buy_date = db.Column(db.DateTime, nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)  # 买入金额
    quantity = db.Column(db.Numeric(10, 4), nullable=False)  # 买入数量
    price = db.Column(db.Numeric(10, 4), nullable=False)  # 买入价格
    fee = db.Column(db.Numeric(10, 2), default=0)  # 手续费
    notes = db.Column(db.Text, nullable=True)  # 备注
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    target = db.relationship('Target', backref='records')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'target_id': self.target_id,
            'target_code': self.target.code if self.target else '',
            'target_name': self.target.name if self.target else '',
            'buy_date': self.buy_date.isoformat() if self.buy_date else None,
            'amount': float(self.amount),
            'quantity': float(self.quantity),
            'price': float(self.price),
            'fee': float(self.fee),
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Target(db.Model):
    """投资标的管理模型"""
    __tablename__ = 'targets'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    code = db.Column(db.String(20), nullable=False)  # 标的代码
    name = db.Column(db.String(100), nullable=False)  # 标的名称
    current_price = db.Column(db.Numeric(10, 4), nullable=False)  # 当前价格
    price_date = db.Column(db.DateTime, nullable=False)  # 价格日期
    market = db.Column(db.String(20), nullable=True)  # 市场类型 (A股/美股/港股)
    sector = db.Column(db.String(50), nullable=True)  # 行业板块
    notes = db.Column(db.Text, nullable=True)  # 备注
    is_active = db.Column(db.Boolean, default=True)  # 是否启用
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'code': self.code,
            'name': self.name,
            'current_price': float(self.current_price),
            'price_date': self.price_date.isoformat() if self.price_date else None,
            'market': self.market,
            'sector': self.sector,
            'notes': self.notes,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }