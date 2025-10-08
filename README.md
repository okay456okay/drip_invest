# 定投管理工具 MVP

一个基于 Python Flask 的股票定投管理工具，帮助用户管理定投计划、记录交易历史、分析投资成本与收益。

## 技术栈

- **后端**: Python 3.10+ + Flask
- **数据库**: SQLite + SQLAlchemy ORM
- **前端**: Bootstrap 5 (前后端不分离)
- **配置管理**: python-dotenv
- **定时任务**: APScheduler
- **HTTP请求**: requests
- **其他**: Jinja2 模板引擎

## 核心功能

### 1. 用户管理模块

#### 1.1 用户注册
- 用户名（唯一）
- 邮箱地址（唯一）
- 密码（加密存储）
- 注册时间记录

#### 1.2 用户登录/登出
- 用户名/邮箱 + 密码登录
- 会话管理
- 登录状态保持
- 安全登出

#### 1.3 用户信息管理
- 查看个人信息
- 修改密码
- 账户设置

### 2. 投资标的管理模块

#### 2.1 标的设置
- **标的代码**: 支持A股、美股、港股、加密货币代码格式
- **标的名称**: 投资标的的显示名称
- **当前价格**: 最新价格（支持4位小数精度）
- **市场类型**: A股/美股/港股/加密货币
- **行业板块**: 标的所属行业分类
- **价格更新**: 支持快捷更新价格功能
- **状态管理**: 启用/禁用标的

#### 2.2 标的管理功能
- 创建新的投资标的
- 编辑现有标的信息
- 删除标的
- 查看所有标的列表
- 按市场类型筛选
- 快捷价格更新

### 3. 定投提醒管理模块

#### 3.1 定投提醒设置
- **投资标的**: 从标的管理中选择（下拉选择）
- **定投金额**: 每次定投的金额（人民币）
- **定投频率**: 
  - 按月定投：每月定投的具体日期（1-31日）
  - 按周定投：每周定投的具体星期（周一至周日）
- **提醒时间**: 具体提醒时间点（HH:MM格式）
- **提醒方式**: 企业微信群机器人webhook（用户级别配置）
- **状态管理**: 启用/禁用提醒

#### 3.2 提醒管理功能
- 创建新的定投提醒
- 编辑现有提醒设置
- 删除提醒
- 查看所有提醒列表
- 提醒状态切换
- 测试webhook功能
- 手动发送提醒

#### 3.3 企业微信集成
- 用户级别配置群机器人webhook URL
- 定时发送定投提醒消息
- 提醒消息模板定制
- 所有定投提醒共享同一个webhook配置
- 自动定时任务调度

### 4. 定投记录管理模块

#### 4.1 定投交易记录
- **买入时间**: 交易执行日期时间
- **投资标的**: 从标的管理中选择（下拉选择）
- **买入金额**: 本次定投金额
- **买入数量**: 实际买入的股数
- **买入价格**: 成交均价
- **手续费**: 交易费用（可选）
- **备注**: 交易备注信息

#### 4.2 记录管理功能
- 添加新的定投记录
- 编辑历史记录
- 删除记录
- 按时间范围筛选
- 按投资标的筛选
- 记录详情查看

### 5. 成本分析模块

#### 5.1 成本计算
- **平均成本价**: 总投入金额 ÷ 总持股数量
- **总投入金额**: 所有定投金额的累计
- **总持股数量**: 所有买入数量的累计
- **交易次数**: 定投执行次数统计

#### 5.2 成本分析展示
- 按投资标的分组显示成本信息
- 成本趋势图表
- 投入金额分布统计

### 6. 收益分析模块

#### 6.1 收益计算
- **当前价格**: 从标的管理获取最新价格
- **持仓价值**: 当前价格 × 持股数量
- **盈亏金额**: 持仓价值 - 总投入金额
- **收益率**: 盈亏金额 ÷ 总投入金额 × 100%

#### 6.2 收益分析展示
- 按投资标的分组显示收益情况
- 总体投资组合收益概览
- 收益趋势图表
- 盈亏明细列表

## 数据库设计

### 用户表 (users)
```sql
- id: 主键
- username: 用户名（唯一）
- email: 邮箱（唯一）
- password_hash: 密码哈希
- webhook_url: 企业微信webhook URL
- created_at: 创建时间
- updated_at: 更新时间
```

### 投资标的管理表 (targets)
```sql
- id: 主键
- user_id: 用户ID（外键）
- code: 标的代码（股票代码/加密货币代码等）
- name: 标的名称
- current_price: 当前价格（支持4位小数）
- price_date: 价格更新日期
- market: 市场类型（A股/美股/港股/加密货币）
- sector: 行业板块
- notes: 备注
- is_active: 是否启用
- created_at: 创建时间
- updated_at: 更新时间
```

### 定投提醒表 (investment_reminders)
```sql
- id: 主键
- user_id: 用户ID（外键）
- target_id: 投资标的ID（外键）
- amount: 定投金额
- frequency_type: 定投频率类型（monthly/weekly）
- frequency_value: 定投频率值（1-31日 或 1-7星期）
- reminder_time: 提醒时间（HH:MM格式）
- is_active: 是否启用
- created_at: 创建时间
- updated_at: 更新时间
```

### 定投记录表 (investment_records)
```sql
- id: 主键
- user_id: 用户ID（外键）
- target_id: 投资标的ID（外键）
- buy_date: 买入日期
- amount: 买入金额
- quantity: 买入数量
- price: 买入价格
- fee: 手续费
- notes: 备注
- created_at: 创建时间
```

## 项目结构

```
drip_invest/
├── app/
│   ├── __init__.py
│   ├── models/
│   │   └── __init__.py
│   ├── routes/
│   │   ├── auth.py
│   │   ├── reminder.py
│   │   ├── record.py
│   │   ├── analysis.py
│   │   └── target.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── auth/
│   │   │   ├── login.html
│   │   │   ├── register.html
│   │   │   └── profile.html
│   │   ├── reminder/
│   │   │   ├── index.html
│   │   │   ├── create.html
│   │   │   └── edit.html
│   │   ├── record/
│   │   │   ├── index.html
│   │   │   ├── create.html
│   │   │   └── edit.html
│   │   ├── analysis/
│   │   │   ├── cost.html
│   │   │   └── profit.html
│   │   └── target/
│   │       ├── index.html
│   │       ├── create.html
│   │       └── edit.html
│   └── scheduler.py
├── drip_invest.db
├── config.py
├── main.py
├── requirements.txt
├── env_example
├── .gitignore
└── README.md
```

## 开发计划

### Phase 1: 基础框架搭建
- [ ] 项目结构初始化
- [ ] Flask应用配置
- [ ] 数据库模型定义
- [ ] 基础模板和静态资源

### Phase 2: 用户管理
- [ ] 用户注册功能
- [ ] 用户登录/登出
- [ ] 会话管理
- [ ] 用户信息管理

### Phase 3: 定投提醒
- [ ] 提醒设置CRUD
- [ ] 企业微信webhook集成
- [ ] 提醒管理界面

### Phase 4: 定投记录
- [ ] 记录管理CRUD
- [ ] 记录查询和筛选
- [ ] 记录管理界面

### Phase 5: 成本分析
- [ ] 成本计算逻辑
- [ ] 成本分析界面
- [ ] 数据可视化

### Phase 6: 收益分析
- [ ] 收益计算逻辑
- [ ] 收益分析界面
- [ ] 投资组合概览

## 环境配置

### 依赖安装
```bash
pip install flask flask-sqlalchemy python-dotenv requests apscheduler
```

### 环境变量配置

1. **复制环境变量模板**：
```bash
cp env_example .env
```

2. **修改环境变量**：
编辑 `.env` 文件，根据实际需要修改配置：

```env
# Flask 应用配置
FLASK_APP=main.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# 数据库配置
DATABASE_URL=sqlite:///drip_invest.db

# 服务器配置
HOST=127.0.0.1
PORT=5006

# 日志配置
LOG_LEVEL=INFO

# 定时任务配置
SCHEDULER_TIMEZONE=Asia/Shanghai

# 调试模式
DEBUG=True
```

### 配置说明

- **HOST**: 服务器监听地址，默认 `127.0.0.1`
- **PORT**: 服务器端口，默认 `5006`
- **SECRET_KEY**: Flask会话密钥，生产环境请使用强密码
- **DATABASE_URL**: 数据库连接URL，默认 `sqlite:///drip_invest.db`
- **SCHEDULER_TIMEZONE**: 定时任务时区，默认 `Asia/Shanghai`
- **DEBUG**: 调试模式，生产环境请设置为 `False`

## 使用说明

### 启动应用

1. **安装依赖**：
```bash
pip install -r requirements.txt
```

2. **配置环境变量**：
```bash
cp env_example .env
# 编辑 .env 文件，修改相应配置
```

3. **启动服务**：
```bash
python main.py
```

应用将在 `http://127.0.0.1:5006` 启动（端口可通过环境变量 `PORT` 修改）

### 功能使用

1. **注册账户**: 创建用户账户
2. **配置webhook**: 在用户设置中配置企业微信群机器人webhook
3. **管理标的**: 添加和管理投资标的（股票、加密货币等）
4. **设置提醒**: 配置定投提醒（投资标的、金额、频率类型、频率值、提醒时间）
5. **记录交易**: 每次定投后添加交易记录
6. **查看分析**: 查看成本分析和收益情况
7. **管理提醒**: 根据需要调整或删除提醒设置

## 注意事项

- 本工具专注于定投的核心功能，不包含复杂的市场数据分析
- 投资标的价格需要手动输入，暂不集成实时行情API
- 支持A股、美股、港股、加密货币等多种投资标的
- 企业微信webhook需要用户自行配置群机器人
- 所有金额计算使用Decimal类型确保精度
- 数据存储在本地SQLite数据库中
- 数据库文件默认存储在项目根目录下（`drip_invest.db`）
- 使用绝对路径避免Flask自动创建instance目录

## 后续扩展方向

- 集成股票行情API获取实时价格
- 添加更多技术指标分析
- 支持多币种投资
- 移动端适配
- 数据导出功能
- 投资策略回测
