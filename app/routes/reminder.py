from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app import db
from app.models import InvestmentReminder, User, Target
from app.utils.decorators import login_required
from datetime import datetime
import requests

reminder_bp = Blueprint('reminder', __name__)

@reminder_bp.route('/')
@login_required
def index():
    """定投提醒列表"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # 筛选条件
    stock_code = request.args.get('stock_code', '').strip()
    
    query = InvestmentReminder.query.filter_by(user_id=session['user_id']).join(Target)
    
    if stock_code:
        query = query.filter(Target.code.like(f'%{stock_code}%'))
    
    reminders = query.order_by(InvestmentReminder.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('reminder/index.html', reminders=reminders, stock_code=stock_code)

@reminder_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """创建定投提醒"""
    if request.method == 'POST':
        target_id = request.form.get('target_id')
        amount = request.form.get('amount')
        frequency_type = request.form.get('frequency_type')
        frequency_value = request.form.get('frequency_value')
        reminder_time = request.form.get('reminder_time')
        
        # 验证输入
        if not target_id or not amount or not frequency_type or not frequency_value or not reminder_time:
            flash('请填写所有必填字段', 'error')
            targets = Target.query.filter_by(user_id=session['user_id'], is_active=True).all()
            return render_template('reminder/create.html', targets=targets)
        
        try:
            amount = float(amount)
            frequency_value = int(frequency_value)
        except ValueError:
            flash('金额和频率值必须是数字', 'error')
            targets = Target.query.filter_by(user_id=session['user_id'], is_active=True).all()
            return render_template('reminder/create.html', targets=targets)
        
        if amount <= 0:
            flash('定投金额必须大于0', 'error')
            targets = Target.query.filter_by(user_id=session['user_id'], is_active=True).all()
            return render_template('reminder/create.html', targets=targets)
        
        if frequency_type == 'monthly':
            if not (1 <= frequency_value <= 31):
                flash('月度定投日期必须在1-31之间', 'error')
                targets = Target.query.filter_by(user_id=session['user_id'], is_active=True).all()
                return render_template('reminder/create.html', targets=targets)
        elif frequency_type == 'weekly':
            if not (1 <= frequency_value <= 7):
                flash('周度定投星期必须在1-7之间', 'error')
                targets = Target.query.filter_by(user_id=session['user_id'], is_active=True).all()
                return render_template('reminder/create.html', targets=targets)
        else:
            flash('无效的频率类型', 'error')
            targets = Target.query.filter_by(user_id=session['user_id'], is_active=True).all()
            return render_template('reminder/create.html', targets=targets)
        
        # 检查是否已存在相同的提醒
        existing = InvestmentReminder.query.filter_by(
            user_id=session['user_id'],
            target_id=target_id,
            frequency_type=frequency_type,
            frequency_value=frequency_value
        ).first()
        
        if existing:
            flash('该标的的定投提醒已存在', 'error')
            targets = Target.query.filter_by(user_id=session['user_id'], is_active=True).all()
            return render_template('reminder/create.html', targets=targets)
        
        # 创建新提醒
        reminder = InvestmentReminder(
            user_id=session['user_id'],
            target_id=target_id,
            amount=amount,
            frequency_type=frequency_type,
            frequency_value=frequency_value,
            reminder_time=reminder_time
        )
        
        try:
            db.session.add(reminder)
            db.session.commit()
            
            # 添加定时任务
            from app.scheduler import scheduler
            scheduler.add_reminder_job(reminder)
            
            flash('定投提醒创建成功', 'success')
            return redirect(url_for('reminder.index'))
        except Exception as e:
            db.session.rollback()
            flash('创建失败，请重试', 'error')
            targets = Target.query.filter_by(user_id=session['user_id'], is_active=True).all()
            return render_template('reminder/create.html', targets=targets)
    
    targets = Target.query.filter_by(user_id=session['user_id'], is_active=True).all()
    return render_template('reminder/create.html', targets=targets)

@reminder_bp.route('/<int:reminder_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(reminder_id):
    """编辑定投提醒"""
    reminder = InvestmentReminder.query.filter_by(
        id=reminder_id, 
        user_id=session['user_id']
    ).first_or_404()
    
    if request.method == 'POST':
        target_id = request.form.get('target_id')
        amount = request.form.get('amount')
        frequency_type = request.form.get('frequency_type')
        frequency_value = request.form.get('frequency_value')
        reminder_time = request.form.get('reminder_time')
        
        # 验证输入
        if not target_id or not amount or not frequency_type or not frequency_value or not reminder_time:
            flash('请填写所有必填字段', 'error')
            targets = Target.query.filter_by(user_id=session['user_id'], is_active=True).all()
            return render_template('reminder/edit.html', reminder=reminder, targets=targets)
        
        try:
            amount = float(amount)
            frequency_value = int(frequency_value)
        except ValueError:
            flash('金额和频率值必须是数字', 'error')
            targets = Target.query.filter_by(user_id=session['user_id'], is_active=True).all()
            return render_template('reminder/edit.html', reminder=reminder, targets=targets)
        
        if amount <= 0:
            flash('定投金额必须大于0', 'error')
            targets = Target.query.filter_by(user_id=session['user_id'], is_active=True).all()
            return render_template('reminder/edit.html', reminder=reminder, targets=targets)
        
        if frequency_type == 'monthly':
            if not (1 <= frequency_value <= 31):
                flash('月度定投日期必须在1-31之间', 'error')
                targets = Target.query.filter_by(user_id=session['user_id'], is_active=True).all()
                return render_template('reminder/edit.html', reminder=reminder, targets=targets)
        elif frequency_type == 'weekly':
            if not (1 <= frequency_value <= 7):
                flash('周度定投星期必须在1-7之间', 'error')
                targets = Target.query.filter_by(user_id=session['user_id'], is_active=True).all()
                return render_template('reminder/edit.html', reminder=reminder, targets=targets)
        else:
            flash('无效的频率类型', 'error')
            targets = Target.query.filter_by(user_id=session['user_id'], is_active=True).all()
            return render_template('reminder/edit.html', reminder=reminder, targets=targets)
        
        # 检查是否已存在相同的提醒（排除当前提醒）
        existing = InvestmentReminder.query.filter(
            InvestmentReminder.user_id == session['user_id'],
            InvestmentReminder.target_id == target_id,
            InvestmentReminder.frequency_type == frequency_type,
            InvestmentReminder.frequency_value == frequency_value,
            InvestmentReminder.id != reminder_id
        ).first()
        
        if existing:
            flash('该标的的定投提醒已存在', 'error')
            targets = Target.query.filter_by(user_id=session['user_id'], is_active=True).all()
            return render_template('reminder/edit.html', reminder=reminder, targets=targets)
        
        # 更新提醒
        reminder.target_id = target_id
        reminder.amount = amount
        reminder.frequency_type = frequency_type
        reminder.frequency_value = frequency_value
        reminder.reminder_time = reminder_time
        
        try:
            db.session.commit()
            
            # 更新定时任务
            from app.scheduler import scheduler
            scheduler.update_reminder_job(reminder)
            
            flash('定投提醒更新成功', 'success')
            return redirect(url_for('reminder.index'))
        except Exception as e:
            db.session.rollback()
            flash('更新失败，请重试', 'error')
            targets = Target.query.filter_by(user_id=session['user_id'], is_active=True).all()
            return render_template('reminder/edit.html', reminder=reminder, targets=targets)
    
    targets = Target.query.filter_by(user_id=session['user_id'], is_active=True).all()
    return render_template('reminder/edit.html', reminder=reminder, targets=targets)

@reminder_bp.route('/<int:reminder_id>/delete', methods=['POST'])
@login_required
def delete(reminder_id):
    """删除定投提醒"""
    reminder = InvestmentReminder.query.filter_by(
        id=reminder_id, 
        user_id=session['user_id']
    ).first_or_404()
    
    try:
        # 删除定时任务
        from app.scheduler import scheduler
        scheduler.remove_reminder_job(reminder_id)
        
        db.session.delete(reminder)
        db.session.commit()
        flash('定投提醒删除成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash('删除失败，请重试', 'error')
    
    return redirect(url_for('reminder.index'))

@reminder_bp.route('/<int:reminder_id>/toggle', methods=['POST'])
@login_required
def toggle(reminder_id):
    """切换提醒启用状态"""
    reminder = InvestmentReminder.query.filter_by(
        id=reminder_id, 
        user_id=session['user_id']
    ).first_or_404()
    
    reminder.is_active = not reminder.is_active
    
    try:
        db.session.commit()
        
        # 更新定时任务
        from app.scheduler import scheduler
        if reminder.is_active:
            scheduler.add_reminder_job(reminder)
        else:
            scheduler.remove_reminder_job(reminder_id)
        
        status = '启用' if reminder.is_active else '禁用'
        flash(f'定投提醒已{status}', 'success')
    except Exception as e:
        db.session.rollback()
        flash('状态切换失败，请重试', 'error')
    
    return redirect(url_for('reminder.index'))

@reminder_bp.route('/test-webhook', methods=['POST'])
@login_required
def test_webhook():
    """测试企业微信webhook"""
    user = User.query.get(session['user_id'])
    
    if not user or not user.webhook_url:
        return jsonify({
            'success': False,
            'message': '请先在个人设置中配置企业微信webhook'
        })
    
    # 发送测试消息
    message = {
        "msgtype": "text",
        "text": {
            "content": "【定投管理工具】\n这是一条测试消息，您的webhook配置正常！\n时间：" + datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    }
    
    try:
        response = requests.post(user.webhook_url, json=message, timeout=10)
        if response.status_code == 200:
            return jsonify({
                'success': True,
                'message': '测试消息发送成功！'
            })
        else:
            return jsonify({
                'success': False,
                'message': f'发送失败，状态码：{response.status_code}'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'发送失败：{str(e)}'
        })

@reminder_bp.route('/send-reminder/<int:reminder_id>', methods=['POST'])
@login_required
def send_reminder(reminder_id):
    """手动发送定投提醒"""
    reminder = InvestmentReminder.query.filter_by(
        id=reminder_id, 
        user_id=session['user_id']
    ).first_or_404()
    
    user = User.query.get(session['user_id'])
    
    if not user or not user.webhook_url:
        return jsonify({
            'success': False,
            'message': '请先在个人设置中配置企业微信webhook'
        })
    
    # 构建提醒消息
    frequency_text = "每月" if reminder.frequency_type == 'monthly' else "每周"
    frequency_value_text = f"{reminder.frequency_value}日" if reminder.frequency_type == 'monthly' else f"星期{reminder.frequency_value}"
    
    message = {
        "msgtype": "text",
        "text": {
            "content": f"【定投提醒】\n标的：{reminder.target.code} ({reminder.target.name})\n金额：¥{reminder.amount}\n频率：{frequency_text}{frequency_value_text}\n时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        }
    }
    
    try:
        response = requests.post(user.webhook_url, json=message, timeout=10)
        if response.status_code == 200:
            return jsonify({
                'success': True,
                'message': '定投提醒发送成功！'
            })
        else:
            return jsonify({
                'success': False,
                'message': f'发送失败，状态码：{response.status_code}'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'发送失败：{str(e)}'
        })

@reminder_bp.route('/job-status/<int:reminder_id>', methods=['GET'])
@login_required
def get_job_status(reminder_id):
    """获取定时任务状态"""
    reminder = InvestmentReminder.query.filter_by(
        id=reminder_id, 
        user_id=session['user_id']
    ).first_or_404()
    
    from app.scheduler import scheduler
    job_status = scheduler.get_job_status(reminder_id)
    
    if job_status:
        return jsonify({
            'success': True,
            'job_status': job_status
        })
    else:
        return jsonify({
            'success': False,
            'message': '定时任务不存在或已停止'
        })