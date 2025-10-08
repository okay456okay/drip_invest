# 快速开始指南

本指南将帮助您在5分钟内快速部署和运行定投管理系统。

## 🎯 目标

通过本指南，您将能够：
- 成功部署定投管理系统
- 创建第一个用户账户
- 配置企业微信通知
- 添加投资标的和定投提醒

## 📋 前置条件

确保您的系统已安装：
- Python 3.10 或更高版本
- pip 包管理器
- Git（用于克隆项目）

## 🚀 快速部署

### 步骤1: 获取项目

```bash
# 克隆项目
git clone https://github.com/your-username/drip_invest.git
cd drip_invest
```

### 步骤2: 设置环境

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Linux/Mac:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 步骤3: 配置应用

```bash
# 复制环境变量模板
cp env_example .env

# 编辑配置文件（可选）
# 默认配置已经可以正常运行
```

### 步骤4: 启动应用

```bash
# 启动应用
python main.py
```

看到以下输出表示启动成功：
```
INFO:apscheduler.scheduler:Scheduler started
INFO:app.scheduler:定时任务调度器已启动
 * Running on http://127.0.0.1:5006
```

### 步骤5: 访问应用

打开浏览器访问：`http://127.0.0.1:5006`

## 👤 首次使用

### 1. 注册账户

1. 点击"注册"按钮
2. 填写用户名、邮箱和密码
3. 点击"注册"完成账户创建

### 2. 配置企业微信通知（可选）

1. 登录后点击右上角用户名
2. 选择"个人设置"
3. 在"企业微信Webhook"字段输入群机器人URL
4. 点击"保存设置"

> 💡 **获取企业微信Webhook URL**：
> 1. 在企业微信群中添加群机器人
> 2. 复制机器人的Webhook URL
> 3. 粘贴到个人设置中

### 3. 添加投资标的

1. 点击"标的管理"菜单
2. 点击"添加标的"按钮
3. 填写标的信息：
   - 标的代码：如 `000001`（平安银行）
   - 标的名称：如 `平安银行`
   - 当前价格：如 `12.50`
   - 市场类型：选择 `A股`
4. 点击"保存"

### 4. 设置定投提醒

1. 点击"定投提醒"菜单
2. 点击"添加提醒"按钮
3. 填写提醒信息：
   - 投资标的：选择刚才添加的标的
   - 定投金额：如 `1000`
   - 定投频率：选择 `按月定投`
   - 频率值：如 `15`（每月15日）
   - 提醒时间：如 `09:30`
4. 点击"保存"

### 5. 记录定投交易

1. 点击"定投记录"菜单
2. 点击"添加记录"按钮
3. 填写交易信息：
   - 投资标的：选择标的
   - 买入日期：选择交易日期
   - 买入金额：如 `1000`
   - 买入数量：如 `80`
   - 买入价格：如 `12.50`
4. 点击"保存"

### 6. 查看分析

1. 点击"成本分析"查看投资成本
2. 点击"收益分析"查看盈亏情况

## 🔧 高级配置

### 修改端口

```bash
# 方法1: 环境变量
PORT=8080 python main.py

# 方法2: 修改.env文件
echo "PORT=8080" >> .env
python main.py
```

### 修改数据库位置

在 `.env` 文件中设置：
```env
DATABASE_URL=sqlite:///path/to/your/database.db
```

### 生产环境部署

1. 设置生产环境变量：
```env
DEBUG=False
SECRET_KEY=your-production-secret-key
```

2. 使用生产级WSGI服务器：
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5006 main:app
```

## 🆘 故障排除

### 常见问题

**问题**: `ModuleNotFoundError: No module named 'flask'`
**解决**: 确保已激活虚拟环境并安装依赖

**问题**: `sqlite3.OperationalError: unable to open database file`
**解决**: 检查数据库文件权限，确保应用有写入权限

**问题**: 企业微信通知收不到
**解决**: 检查webhook URL是否正确，确保群机器人已启用

### 获取帮助

如果遇到问题，请：
1. 查看[常见问题](README.md#常见问题)
2. 搜索[Issues](https://github.com/your-username/drip_invest/issues)
3. 创建新的Issue描述问题

## 🎉 完成！

恭喜！您已经成功部署并配置了定投管理系统。现在您可以：

- ✅ 管理投资标的
- ✅ 设置定投提醒
- ✅ 记录交易历史
- ✅ 分析投资成本与收益
- ✅ 接收企业微信通知

开始您的智能定投之旅吧！🚀
