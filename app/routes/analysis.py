from flask import Blueprint, render_template, request, session, jsonify
from app import db
from app.models import InvestmentRecord, Target
from app.utils.decorators import login_required
from decimal import Decimal
from datetime import datetime

analysis_bp = Blueprint('analysis', __name__)

@analysis_bp.route('/cost')
@login_required
def cost_analysis():
    """成本分析"""
    # 获取所有定投记录
    records = InvestmentRecord.query.filter_by(user_id=session['user_id']).all()
    
    if not records:
        return render_template('analysis/cost.html', 
                              cost_data=[], 
                              total_investment=0, 
                              total_fee=0, 
                              total_trades=0)
    
    # 按标的代码分组计算
    cost_data = []
    stock_groups = {}
    total_investment = 0
    total_fee = 0
    total_trades = len(records)
    
    for record in records:
        stock_code = record.target.code if record.target else 'Unknown'
        if stock_code not in stock_groups:
            stock_groups[stock_code] = {
                'stock_code': stock_code,
                'stock_name': record.target.name if record.target else 'Unknown',
                'records': [],
                'total_amount': 0,
                'total_quantity': 0,
                'total_fee': 0,
                'trade_count': 0
            }
        
        stock_groups[stock_code]['records'].append(record.to_dict())
        stock_groups[stock_code]['total_amount'] += float(record.amount)
        stock_groups[stock_code]['total_quantity'] += float(record.quantity)
        stock_groups[stock_code]['total_fee'] += float(record.fee)
        stock_groups[stock_code]['trade_count'] += 1
        
        # 累计总体数据
        total_investment += float(record.amount)
        total_fee += float(record.fee)
    
    # 计算平均成本
    for stock_code, data in stock_groups.items():
        if data['total_quantity'] > 0:
            avg_cost = data['total_amount'] / data['total_quantity']
            data['avg_cost'] = round(avg_cost, 4)
            cost_data.append(data)
    
    return render_template('analysis/cost.html', 
                          cost_data=cost_data, 
                          total_investment=total_investment, 
                          total_fee=total_fee, 
                          total_trades=total_trades)

@analysis_bp.route('/profit')
@login_required
def profit_analysis():
    """收益分析"""
    # 获取所有定投记录
    records = InvestmentRecord.query.filter_by(user_id=session['user_id']).all()
    
    if not records:
        return render_template('analysis/profit.html', 
                              profit_data=[], 
                              total_cost=0, 
                              total_market_value=0, 
                              total_profit_loss=0, 
                              total_profit_rate=0)
    
    # 按标的代码分组计算
    profit_data = []
    stock_groups = {}
    total_cost = 0
    total_market_value = 0
    total_profit_loss = 0
    
    for record in records:
        stock_code = record.target.code if record.target else 'Unknown'
        if stock_code not in stock_groups:
            stock_groups[stock_code] = {
                'stock_code': stock_code,
                'stock_name': record.target.name if record.target else 'Unknown',
                'records': [],
                'total_amount': 0,
                'total_quantity': 0,
                'total_fee': 0
            }
        
        stock_groups[stock_code]['records'].append(record.to_dict())
        stock_groups[stock_code]['total_amount'] += float(record.amount)
        stock_groups[stock_code]['total_quantity'] += float(record.quantity)
        stock_groups[stock_code]['total_fee'] += float(record.fee)
    
    # 计算平均成本和收益
    for stock_code, data in stock_groups.items():
        if data['total_quantity'] > 0:
            avg_cost = data['total_amount'] / data['total_quantity']
            data['avg_cost'] = round(avg_cost, 4)
            
            # 获取最新价格
            latest_target = Target.query.filter_by(
                user_id=session['user_id'],
                code=stock_code
            ).order_by(Target.price_date.desc()).first()
            
            if latest_target:
                data['latest_price'] = float(latest_target.current_price)
                data['current_value'] = data['total_quantity'] * data['latest_price']
                data['profit_loss'] = data['current_value'] - data['total_amount']
                data['return_rate'] = (data['profit_loss'] / data['total_amount']) * 100 if data['total_amount'] > 0 else 0
                data['price_date'] = latest_target.price_date
            else:
                data['latest_price'] = 0
                data['current_value'] = 0
                data['profit_loss'] = 0
                data['return_rate'] = 0
                data['price_date'] = None
            
            # 累计总体数据
            total_cost += data['total_amount']
            total_market_value += data['current_value']
            total_profit_loss += data['profit_loss']
            
            profit_data.append(data)
    
    # 计算总体收益率
    total_profit_rate = (total_profit_loss / total_cost) * 100 if total_cost > 0 else 0
    
    return render_template('analysis/profit.html', 
                          profit_data=profit_data, 
                          total_cost=total_cost, 
                          total_market_value=total_market_value, 
                          total_profit_loss=total_profit_loss, 
                          total_profit_rate=total_profit_rate)

@analysis_bp.route('/update-price', methods=['POST'])
@login_required
def update_price():
    """更新股票价格"""
    data = request.get_json()
    stock_code = data.get('stock_code', '').strip().upper()
    current_price = data.get('current_price')
    
    if not stock_code or not current_price:
        return jsonify({'success': False, 'message': '请提供股票代码和价格'})
    
    try:
        current_price = float(current_price)
        if current_price <= 0:
            return jsonify({'success': False, 'message': '价格必须大于0'})
    except ValueError:
        return jsonify({'success': False, 'message': '价格格式错误'})
    
    # 查找或创建价格记录
    target = Target.query.filter_by(
        user_id=session['user_id'],
        code=stock_code
    ).first()
    
    if not target:
        return jsonify({'success': False, 'message': '未找到该标的，请先在标的管理中添加'})
    
    # 更新价格
    target.current_price = current_price
    target.price_date = datetime.now()
    
    try:
        db.session.commit()
        return jsonify({
            'success': True, 
            'message': '价格更新成功',
            'price': current_price,
            'date': target.price_date.strftime('%Y-%m-%d')
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'})