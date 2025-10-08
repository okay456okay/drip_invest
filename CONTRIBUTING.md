# 贡献指南

感谢您对定投管理系统的关注！我们欢迎各种形式的贡献，包括但不限于：

- 🐛 报告Bug
- 💡 提出新功能建议
- 📝 改进文档
- 🔧 提交代码修复
- 🎨 改进用户界面

## 如何贡献

### 报告问题

如果您发现了Bug或有功能建议，请：

1. 检查[Issues](https://github.com/your-username/drip_invest/issues)中是否已有类似问题
2. 创建新的Issue，详细描述问题或建议
3. 提供复现步骤（如果是Bug）

### 提交代码

1. **Fork项目**
   ```bash
   git clone https://github.com/your-username/drip_invest.git
   cd drip_invest
   ```

2. **创建功能分支**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **设置开发环境**
   ```bash
   # 创建虚拟环境
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或 venv\Scripts\activate  # Windows
   
   # 安装依赖
   pip install -r requirements.txt
   
   # 复制环境变量文件
   cp env_example .env
   ```

4. **进行开发**
   - 遵循现有的代码风格
   - 添加必要的注释
   - 确保代码通过测试

5. **提交更改**
   ```bash
   git add .
   git commit -m "feat: 添加新功能描述"
   git push origin feature/your-feature-name
   ```

6. **创建Pull Request**
   - 在GitHub上创建Pull Request
   - 详细描述您的更改
   - 关联相关的Issue

## 代码规范

### Python代码风格
- 遵循PEP 8规范
- 使用有意义的变量和函数名
- 添加适当的注释和文档字符串

### 提交信息规范
使用以下格式：
```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

类型包括：
- `feat`: 新功能
- `fix`: Bug修复
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

### 数据库变更
- 如果需要修改数据库结构，请提供迁移脚本
- 确保向后兼容性
- 更新相关文档

## 开发环境设置

### 系统要求
- Python 3.10+
- pip
- Git

### 本地开发
1. 克隆项目
2. 创建虚拟环境
3. 安装依赖
4. 配置环境变量
5. 启动应用

### 测试
```bash
# 运行测试（如果有的话）
python -m pytest

# 手动测试功能
python main.py
```

## 文档贡献

- 保持文档的准确性和时效性
- 使用清晰易懂的语言
- 添加适当的示例和截图
- 更新README.md和相关文档

## 问题反馈

如果您在贡献过程中遇到任何问题，请：

1. 查看[FAQ](README.md#常见问题)
2. 搜索已有的Issues
3. 创建新的Issue描述问题

## 许可证

通过贡献代码，您同意您的贡献将在MIT许可证下发布。

感谢您的贡献！🎉
