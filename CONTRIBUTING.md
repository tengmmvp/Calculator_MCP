# 贡献指南

感谢您对 Calculator MCP Server 项目的关注！我们欢迎各种形式的贡献。

## 🤝 如何贡献

### 报告问题

如果您发现了 bug 或有功能建议，请：

1. 检查 [Issues](https://github.com/tengmmvp/Calculator_MCP/issues) 确认问题未被报告
2. 创建新的 Issue，使用适当的模板
3. 提供详细的信息：
   - 问题的详细描述
   - 重现步骤
   - 期望的行为
   - 实际的行为
   - 环境信息（Python 版本、操作系统等）

### 提交代码

1. **Fork 项目**

   ```bash
   # 在 GitHub 上 fork 项目
   git clone https://github.com/tengmmvp/Calculator_MCP.git
   ```

2. **设置开发环境**

   ```bash
   cd Calculator_MCP
   ./scripts/setup-dev.sh
   source venv/bin/activate
   ```

3. **创建功能分支**

   ```bash
   git checkout -b feature/your-feature-name
   # 或
   git checkout -b fix/your-bug-fix
   ```

4. **进行开发**

   - 遵循项目的代码风格
   - 添加测试（如果适用）
   - 更新文档（如果需要）

5. **运行测试和质量检查**

   ```bash
   # 运行测试
   pytest tests/

   # 代码格式化
   black src/

   # 代码检查
   flake8 src/

   # 安全检查
   bandit -r src/
   ```

6. **提交更改**

   ```bash
   git add .
   git commit -m "feat: add amazing feature"
   ```

   提交信息请遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

   - `feat:` 新功能
   - `fix:` bug 修复
   - `docs:` 文档更新
   - `style:` 代码格式化（不影响功能）
   - `refactor:` 代码重构
   - `test:` 添加或修改测试
   - `chore:` 构建过程或辅助工具的变动

7. **推送并创建 PR**

   ```bash
   git push origin feature/your-feature-name
   ```

   然后在 GitHub 上创建 Pull Request。

## 📝 开发指南

### 代码风格

- 使用 [Black](https://black.readthedocs.io/) 进行代码格式化
- 遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/) 规范
- 使用 [flake8](https://flake8.pycqa.org/) 进行代码检查
- 使用 [type hints](https://docs.python.org/3/library/typing.html) 提高代码可读性

### 测试

- 所有新功能都应该包含测试
- 测试覆盖率应保持在 80% 以上
- 使用描述性的测试名称
- 遵循 AAA 模式（Arrange, Act, Assert）

```python
def test_calculator_add_with_positive_numbers():
    """测试正数加法运算。"""
    # Arrange
    numbers = [1, 2, 3, 4]
    expected_result = 10.0

    # Act
    result = calculator_add(numbers)

    # Assert
    assert result.result == expected_result
    assert result.operation == "addition"
```

### 文档

- 更新相关的 README 文件
- 为新的公共函数添加 docstring
- 使用 Google 风格的 docstring

```python
def calculator_add(numbers: List[float]) -> CalculationResult:
    """执行加法运算。

    Args:
        numbers: 待相加的数字列表

    Returns:
        CalculationResult: 加法运算结果

    Raises:
        ValueError: 输入列表为空时抛出
    """
    pass
```

## 🏗️ 项目结构

```
Calculator_MCP/
├── src/                          # 源代码
│   ├── __init__.py
│   └── server.py                 # 主服务器
├── tests/                        # 测试
│   ├── __init__.py
│   ├── conftest.py
│   └── test_*.py
├── scripts/                      # 脚本
│   ├── setup-dev.sh             # 开发环境设置
│   └── release.sh               # 发布脚本
├── docs/                         # 文档
├── .github/                      # GitHub 配置
│   └── workflows/                # GitHub Actions
├── requirements.txt              # 依赖
├── pyproject.toml               # 项目配置
├── README.md                     # 项目文档
├── CHANGELOG.md                  # 变更日志
└── LICENSE                       # 许可证
```

## 🔄 发布流程

发布由维护者通过以下步骤进行：

1. 更新版本号
2. 更新 CHANGELOG.md
3. 创建发布标签
4. 自动化 CI/CD 流程会：
   - 运行测试
   - 构建包
   - 发布到 PyPI
   - 创建 Docker 镜像

## 📋 检查清单

在提交 PR 之前，请确保：

- [ ] 代码通过所有测试
- [ ] 代码符合项目的风格指南
- [ ] 添加了必要的测试
- [ ] 更新了相关文档
- [ ] 提交信息遵循规范
- [ ] 没有安全漏洞
- [ ] PR 描述清晰，说明了更改的内容和原因

## 🆘 获取帮助

如果您有任何问题或需要帮助：

1. 查看 [文档](README.md)
2. 搜索现有的 [Issues](https://github.com/tengmmvp/Calculator_MCP/issues)
3. 创建新的 Issue 或 Discussion
4. 在 PR 中提及维护者

## 📜 行为准则

请遵循我们的行为准则：

- 尊重所有参与者
- 保持友好和包容的环境
- 避免人身攻击或批评
- 专注于对事不对人

感谢您的贡献！🎉
