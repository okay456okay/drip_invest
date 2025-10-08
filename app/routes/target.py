from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app import db
from app.models import Target, InvestmentRecord
from app.utils.decorators import login_required
from datetime import datetime
from decimal import Decimal

target_bp = Blueprint('target', __name__)

@target_bp.route('/')
@login_required
def index():
    """投资标的管理列表"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # 筛选条件
    code = request.args.get('code', '').strip()
    market = request.args.get('market', '').strip()
    
    query = Target.query.filter_by(user_id=session['user_id'])
    
    if code:
        query = query.filter(Target.code.like(f'%{code}%'))
    
    if market:
        query = query.filter(Target.market == market)
    
    targets = query.order_by(Target.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('target/index.html', targets=targets, code=code, market=market)

@target_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """添加投资标的"""
    if request.method == 'POST':
        code = request.form.get('code', '').strip().upper()
        name = request.form.get('name', '').strip()
        current_price = request.form.get('current_price')
        price_date = request.form.get('price_date')
        market = request.form.get('market', '').strip()
        sector = request.form.get('sector', '').strip()
        notes = request.form.get('notes', '').strip()
        
        # 验证输入
        if not code or not name or not current_price or not price_date:
            flash('请填写所有必填字段', 'error')
            return render_template('target/create.html')
        
        try:
            current_price = float(current_price)
            price_date_obj = datetime.strptime(price_date, '%Y-%m-%d')
        except ValueError:
            flash('价格或日期格式错误', 'error')
            return render_template('target/create.html')
        
        if current_price <= 0:
            flash('标的价格必须大于0', 'error')
            return render_template('target/create.html')
        
        # 检查标的代码是否已存在
        existing = Target.query.filter_by(
            user_id=session['user_id'],
            code=code
        ).first()
        
        if existing:
            flash('该标的代码已存在', 'error')
            return render_template('target/create.html')
        
        # 创建新标的
        target = Target(
            user_id=session['user_id'],
            code=code,
            name=name,
            current_price=current_price,
            price_date=price_date_obj,
            market=market,
            sector=sector,
            notes=notes
        )
        
        try:
            db.session.add(target)
            db.session.commit()
            flash('投资标的添加成功', 'success')
            return redirect(url_for('target.index'))
        except Exception as e:
            db.session.rollback()
            flash('添加失败，请重试', 'error')
            return render_template('target/create.html')
    
    return render_template('target/create.html')

@target_bp.route('/<int:target_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(target_id):
    """编辑投资标的"""
    target = Target.query.filter_by(
        id=target_id, 
        user_id=session['user_id']
    ).first_or_404()
    
    if request.method == 'POST':
        code = request.form.get('code', '').strip().upper()
        name = request.form.get('name', '').strip()
        current_price = request.form.get('current_price')
        price_date = request.form.get('price_date')
        market = request.form.get('market', '').strip()
        sector = request.form.get('sector', '').strip()
        notes = request.form.get('notes', '').strip()
        
        # 验证输入
        if not code or not name or not current_price or not price_date:
            flash('请填写所有必填字段', 'error')
            return render_template('target/edit.html', target=target)
        
        try:
            current_price = float(current_price)
            price_date_obj = datetime.strptime(price_date, '%Y-%m-%d')
        except ValueError:
            flash('价格或日期格式错误', 'error')
            return render_template('target/edit.html', target=target)
        
        if current_price <= 0:
            flash('标的价格必须大于0', 'error')
            return render_template('target/edit.html', target=target)
        
        # 检查标的代码是否被其他记录使用
        existing = Target.query.filter(
            Target.user_id == session['user_id'],
            Target.code == code,
            Target.id != target_id
        ).first()
        
        if existing:
            flash('该标的代码已被使用', 'error')
            return render_template('target/edit.html', target=target)
        
        # 更新标的
        target.code = code
        target.name = name
        target.current_price = current_price
        target.price_date = price_date_obj
        target.market = market
        target.sector = sector
        target.notes = notes
        
        try:
            db.session.commit()
            flash('投资标的更新成功', 'success')
            return redirect(url_for('target.index'))
        except Exception as e:
            db.session.rollback()
            flash('更新失败，请重试', 'error')
            return render_template('target/edit.html', target=target)
    
    return render_template('target/edit.html', target=target)

@target_bp.route('/<int:target_id>/delete', methods=['POST'])
@login_required
def delete(target_id):
    """删除投资标的"""
    target = Target.query.filter_by(
        id=target_id, 
        user_id=session['user_id']
    ).first_or_404()
    
    try:
        db.session.delete(target)
        db.session.commit()
        flash('投资标的删除成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash('删除失败，请重试', 'error')
    
    return redirect(url_for('target.index'))

@target_bp.route('/<int:target_id>/toggle', methods=['POST'])
@login_required
def toggle(target_id):
    """切换标的启用状态"""
    target = Target.query.filter_by(
        id=target_id, 
        user_id=session['user_id']
    ).first_or_404()
    
    target.is_active = not target.is_active
    
    try:
        db.session.commit()
        status = '启用' if target.is_active else '禁用'
        flash(f'投资标的已{status}', 'success')
    except Exception as e:
        db.session.rollback()
        flash('状态切换失败，请重试', 'error')
    
    return redirect(url_for('target.index'))

@target_bp.route('/get-latest/<code>')
@login_required
def get_latest(code):
    """获取标的的最新价格"""
    latest_target = Target.query.filter_by(
        user_id=session['user_id'],
        code=code.upper()
    ).order_by(Target.price_date.desc()).first()
    
    if latest_target:
        return jsonify({
            'success': True,
            'code': latest_target.code,
            'name': latest_target.name,
            'price': float(latest_target.current_price),
            'date': latest_target.price_date.strftime('%Y-%m-%d'),
            'market': latest_target.market,
            'sector': latest_target.sector,
            'notes': latest_target.notes
        })
    else:
        return jsonify({
            'success': False,
            'message': '未找到该标的的价格记录'
        })

@target_bp.route('/list')
@login_required
def list_targets():
    """获取用户的标的列表（用于下拉选择）"""
    targets = Target.query.filter_by(
        user_id=session['user_id'],
        is_active=True
    ).order_by(Target.code).all()
    
    return jsonify({
        'success': True,
        'targets': [target.to_dict() for target in targets]
    })

@target_bp.route('/<int:target_id>/update-price', methods=['POST'])
@login_required
def update_price(target_id):
    """快捷更新标的价格"""
    target = Target.query.filter_by(id=target_id, user_id=session['user_id']).first()
    
    if not target:
        return jsonify({'success': False, 'message': '标的不存在'}), 404
    
    current_price = request.form.get('current_price')
    
    if not current_price:
        return jsonify({'success': False, 'message': '价格不能为空'}), 400
    
    try:
        current_price = Decimal(current_price)
        if current_price <= 0:
            return jsonify({'success': False, 'message': '价格必须大于0'}), 400
        
        # 保存原价格用于回滚
        original_price = target.current_price
        
        # 更新价格和日期
        target.current_price = current_price
        target.price_date = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'价格更新成功：¥{current_price}',
            'price_date': target.price_date.strftime('%Y-%m-%d'),
            'original_price': float(original_price)
        })
        
    except (ValueError, TypeError) as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': '价格格式错误'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新失败：{str(e)}'}), 500
