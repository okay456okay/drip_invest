from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import db
from app.models import InvestmentRecord, Target
from app.utils.decorators import login_required
from datetime import datetime

record_bp = Blueprint('record', __name__)

@record_bp.route('/')
@login_required
def index():
    """定投记录列表"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # 筛选条件
    stock_code = request.args.get('stock_code', '').strip()
    start_date = request.args.get('start_date', '').strip()
    end_date = request.args.get('end_date', '').strip()
    
    query = InvestmentRecord.query.filter_by(user_id=session['user_id']).join(Target)
    
    if stock_code:
        query = query.filter(Target.code.like(f'%{stock_code}%'))
    
    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(InvestmentRecord.buy_date >= start_date_obj)
        except ValueError:
            pass
    
    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
            query = query.filter(InvestmentRecord.buy_date <= end_date_obj)
        except ValueError:
            pass
    
    records = query.order_by(InvestmentRecord.buy_date.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('record/index.html', records=records, 
                          stock_code=stock_code, start_date=start_date, end_date=end_date)

@record_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """创建定投记录"""
    if request.method == 'POST':
        target_id = request.form.get('target_id')
        buy_date = request.form.get('buy_date')
        amount = request.form.get('amount')
        quantity = request.form.get('quantity')
        price = request.form.get('price')
        fee = request.form.get('fee', '0')
        notes = request.form.get('notes', '').strip()
        
        # 验证输入
        if not all([target_id, buy_date, amount, quantity, price]):
            flash('请填写所有必填字段', 'error')
            targets = Target.query.filter_by(user_id=session['user_id'], is_active=True).all()
            return render_template('record/create.html', targets=targets)
        
        try:
            buy_date_obj = datetime.strptime(buy_date, '%Y-%m-%d')
            amount = float(amount)
            quantity = float(quantity)
            price = float(price)
            fee = float(fee) if fee else 0
        except ValueError:
            flash('日期或数字格式错误', 'error')
            targets = Target.query.filter_by(user_id=session['user_id'], is_active=True).all()
            return render_template('record/create.html', targets=targets)
        
        if amount <= 0 or quantity <= 0 or price <= 0:
            flash('金额、数量和价格必须大于0', 'error')
            targets = Target.query.filter_by(user_id=session['user_id'], is_active=True).all()
            return render_template('record/create.html', targets=targets)
        
        if fee < 0:
            flash('手续费不能为负数', 'error')
            targets = Target.query.filter_by(user_id=session['user_id'], is_active=True).all()
            return render_template('record/create.html', targets=targets)
        
        # 创建新记录
        record = InvestmentRecord(
            user_id=session['user_id'],
            target_id=target_id,
            buy_date=buy_date_obj,
            amount=amount,
            quantity=quantity,
            price=price,
            fee=fee,
            notes=notes
        )
        
        try:
            db.session.add(record)
            db.session.commit()
            flash('定投记录创建成功', 'success')
            return redirect(url_for('record.index'))
        except Exception as e:
            db.session.rollback()
            flash('创建失败，请重试', 'error')
            targets = Target.query.filter_by(user_id=session['user_id'], is_active=True).all()
            return render_template('record/create.html', targets=targets)
    
    targets = Target.query.filter_by(user_id=session['user_id'], is_active=True).all()
    return render_template('record/create.html', targets=targets)

@record_bp.route('/<int:record_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(record_id):
    """编辑定投记录"""
    record = InvestmentRecord.query.filter_by(
        id=record_id, 
        user_id=session['user_id']
    ).first_or_404()
    
    if request.method == 'POST':
        target_id = request.form.get('target_id')
        buy_date = request.form.get('buy_date')
        amount = request.form.get('amount')
        quantity = request.form.get('quantity')
        price = request.form.get('price')
        fee = request.form.get('fee', '0')
        notes = request.form.get('notes', '').strip()
        
        # 验证输入
        if not all([target_id, buy_date, amount, quantity, price]):
            flash('请填写所有必填字段', 'error')
            targets = Target.query.filter_by(user_id=session['user_id'], is_active=True).all()
            return render_template('record/edit.html', record=record, targets=targets)
        
        try:
            buy_date_obj = datetime.strptime(buy_date, '%Y-%m-%d')
            amount = float(amount)
            quantity = float(quantity)
            price = float(price)
            fee = float(fee) if fee else 0
        except ValueError:
            flash('日期或数字格式错误', 'error')
            targets = Target.query.filter_by(user_id=session['user_id'], is_active=True).all()
            return render_template('record/edit.html', record=record, targets=targets)
        
        if amount <= 0 or quantity <= 0 or price <= 0:
            flash('金额、数量和价格必须大于0', 'error')
            targets = Target.query.filter_by(user_id=session['user_id'], is_active=True).all()
            return render_template('record/edit.html', record=record, targets=targets)
        
        if fee < 0:
            flash('手续费不能为负数', 'error')
            targets = Target.query.filter_by(user_id=session['user_id'], is_active=True).all()
            return render_template('record/edit.html', record=record, targets=targets)
        
        # 更新记录
        record.target_id = target_id
        record.buy_date = buy_date_obj
        record.amount = amount
        record.quantity = quantity
        record.price = price
        record.fee = fee
        record.notes = notes
        
        try:
            db.session.commit()
            flash('定投记录更新成功', 'success')
            return redirect(url_for('record.index'))
        except Exception as e:
            db.session.rollback()
            flash('更新失败，请重试', 'error')
            targets = Target.query.filter_by(user_id=session['user_id'], is_active=True).all()
            return render_template('record/edit.html', record=record, targets=targets)
    
    targets = Target.query.filter_by(user_id=session['user_id'], is_active=True).all()
    return render_template('record/edit.html', record=record, targets=targets)

@record_bp.route('/<int:record_id>/delete', methods=['POST'])
@login_required
def delete(record_id):
    """删除定投记录"""
    record = InvestmentRecord.query.filter_by(
        id=record_id, 
        user_id=session['user_id']
    ).first_or_404()
    
    try:
        db.session.delete(record)
        db.session.commit()
        flash('定投记录删除成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash('删除失败，请重试', 'error')
    
    return redirect(url_for('record.index'))