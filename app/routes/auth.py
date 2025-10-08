from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import db
from app.models import User
from app.utils.decorators import login_required
from werkzeug.security import generate_password_hash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """用户注册"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # 验证输入
        if not username or not email or not password:
            flash('请填写所有必填字段', 'error')
            return render_template('auth/register.html')
        
        if password != confirm_password:
            flash('两次输入的密码不一致', 'error')
            return render_template('auth/register.html')
        
        if len(password) < 6:
            flash('密码长度至少6位', 'error')
            return render_template('auth/register.html')
        
        # 检查用户是否已存在
        if User.query.filter_by(username=username).first():
            flash('用户名已存在', 'error')
            return render_template('auth/register.html')
        
        if User.query.filter_by(email=email).first():
            flash('邮箱已被注册', 'error')
            return render_template('auth/register.html')
        
        # 创建新用户
        user = User(username=username, email=email)
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('注册成功，请登录', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('注册失败，请重试', 'error')
            return render_template('auth/register.html')
    
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录"""
    if request.method == 'POST':
        username_or_email = request.form.get('username_or_email')
        password = request.form.get('password')
        
        if not username_or_email or not password:
            flash('请填写用户名/邮箱和密码', 'error')
            return render_template('auth/login.html')
        
        # 查找用户（支持用户名或邮箱登录）
        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash(f'欢迎回来，{user.username}！', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('用户名/邮箱或密码错误', 'error')
            return render_template('auth/login.html')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """用户登出"""
    session.clear()
    flash('已安全退出', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """用户信息管理"""
    user = User.query.get(session['user_id'])
    
    if not user:
        flash('用户不存在', 'error')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'update_profile':
            # 更新个人信息
            new_username = request.form.get('username')
            new_email = request.form.get('email')
            webhook_url = request.form.get('webhook_url')
            
            # 检查用户名和邮箱是否被其他用户使用
            if new_username != user.username:
                if User.query.filter_by(username=new_username).first():
                    flash('用户名已被使用', 'error')
                    return render_template('auth/profile.html', user=user)
                user.username = new_username
            
            if new_email != user.email:
                if User.query.filter_by(email=new_email).first():
                    flash('邮箱已被使用', 'error')
                    return render_template('auth/profile.html', user=user)
                user.email = new_email
            
            user.webhook_url = webhook_url
            
            try:
                db.session.commit()
                session['username'] = user.username
                flash('个人信息更新成功', 'success')
            except Exception as e:
                db.session.rollback()
                flash('更新失败，请重试', 'error')
        
        elif action == 'change_password':
            # 修改密码
            old_password = request.form.get('old_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            
            if not user.check_password(old_password):
                flash('原密码错误', 'error')
                return render_template('auth/profile.html', user=user)
            
            if new_password != confirm_password:
                flash('两次输入的新密码不一致', 'error')
                return render_template('auth/profile.html', user=user)
            
            if len(new_password) < 6:
                flash('新密码长度至少6位', 'error')
                return render_template('auth/profile.html', user=user)
            
            user.set_password(new_password)
            
            try:
                db.session.commit()
                flash('密码修改成功', 'success')
            except Exception as e:
                db.session.rollback()
                flash('密码修改失败，请重试', 'error')
        
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/profile.html', user=user)
