# Calculator MCP Server

一个完全符合 Model Context Protocol (MCP) 规范的数学计算服务器。

## ✨ 特性

- 🔢 **数学计算工具**: 加法、减法、乘法、除法、幂运算
- 📚 **数学资源**: 数学常数、公式、数据等
- 🤖 **智能提示**: 数学问题解决助手

## 🚀 快速开始

### 安装

```bash
# 克隆项目
git clone https://github.com/tengmmvp/Calculator_MCP.git
cd Calculator_MCP

# 安装依赖
pip install -r requirements.txt

# 开发环境安装（可选，升级到最新版本）
pip install -r requirements.txt --upgrade
```

### 配置 Claude Desktop

#### 方法 1：使用项目配置文件（推荐）

```bash
# 复制配置文件到 Claude 配置目录
cp config/claude_desktop_config.json "%APPDATA%\Claude\claude_desktop_config.json"
```

#### 方法 2：手动配置

将以下配置添加到 Claude Desktop 配置文件中：

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Linux**: `~/.config/claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "calculator": {
      "command": "python",
      "args": ["src/server.py"],
      "cwd": "YOUR_PROJECT_PATH",
      "description": "Mathematical calculator with tools, resources, and prompts"
    }
  }
}
```

### 运行服务器

```bash
# 直接运行
python src/server.py

# 开发环境运行（推荐，更好的调试支持）
fastmcp dev src/server.py
```

## 📁 项目结构

```
Calculator_MCP/
├── src/                          # 🔧 源代码
│   ├── __init__.py               # 包初始化文件
│   └── server.py                 # 主服务器（包含所有 MCP 功能）
├── docs/                         # 📚 文档
│   └── API.md                    # API 详细文档
├── config/                       # ⚙️ 配置文件目录
│   └── claude_desktop_config.json # 🖥️ Claude Desktop 配置
├── requirements.txt              # 📋 依赖管理
├── README.md                     # 📖 项目文档
├── CLAUDE.md                     # 🤖 Claude Code 开发指南
└── .gitignore                    # 🚫 Git 忽略规则
```

## 🔧 可用工具

### 基础数学运算

- `calculator_add(numbers: List[float])` - 加法运算，支持多个数字
- `calculator_subtract(numbers: List[float])` - 顺序减法运算
- `calculator_multiply(numbers: List[float])` - 乘法运算，支持多个数字
- `calculator_divide(numerator: float, denominator: float)` - 除法运算
- `calculator_power(base: float, exponent: float)` - 幂运算

### 高级功能

- `calculator_statistics(numbers: List[float], operation: str)` - 统计计算
  - 支持操作: `mean`, `median`, `mode`, `stdev`, `variance`
- `calculator_batch_calculations(operations: List[Dict])` - 批量计算
  - 支持混合多种运算类型
- `calculator_evaluate_expression(expression: str)` - 安全的混合表达式计算
  - 支持复杂数学表达式，如 `(2 + 3) * 4 - 1`，包含 AST 安全验证
- `calculator_solve_linear_equation(equation: str, variable: str = "x")` - 线性方程求解
  - 支持一元线性方程，如 `2x + 3 = 7`

### 资源

- `calculator://constants` - 数学常数库 (π, e, φ, √2, √3)
- `calculator://formulas` - 常用数学公式库

### 提示

- `math_problem_solver(problem: str)` - 数学问题解决助手
- `calculation_checker(calculation: str)` - 计算验证和解释

## 💡 使用示例

### 基础计算

```python
# 加法
result = calculator_add([1, 2, 3, 4])  # 返回: 10.0

# 减法 (顺序执行)
result = calculator_subtract([10, 3, 2])  # 返回: 5.0 (10 - 3 - 2)

# 乘法
result = calculator_multiply([2, 3, 4])  # 返回: 24.0

# 除法
result = calculator_divide(10, 2)  # 返回: 5.0

# 幂运算
result = calculator_power(2, 3)  # 返回: 8.0
```

### 统计计算

```python
# 计算均值
result = calculator_statistics([1, 2, 3, 4, 5], "mean")  # 返回: 3.0

# 计算标准差
result = calculator_statistics([1, 2, 3, 4, 5], "stdev")  # 返回: 1.58

# 计算中位数
result = calculator_statistics([1, 2, 3, 4], "median")  # 返回: 2.5
```

### 批量计算

```python
operations = [
    {"tool": "add", "args": {"numbers": [1, 2, 3]}},
    {"tool": "multiply", "args": {"numbers": [2, 3]}},
    {"tool": "divide", "args": {"numerator": 10, "denominator": 2}}
]
results = calculator_batch_calculations(operations)
# 返回: [6.0, 6.0, 5.0]
```

### 混合表达式计算

```python
# 基础混合运算（带 AST 安全验证）
result = calculator_evaluate_expression("2 + 3 * 4 - 1")  # 返回: 13.0

# 带括号的运算
result = calculator_evaluate_expression("(2 + 3) * 4")    # 返回: 20.0

# 安全的数学函数（sin, cos, sqrt, abs 等）
result = calculator_evaluate_expression("sqrt(16) + sin(0)")  # 返回: 4.0

# 数学常数（pi, e, tau）
result = calculator_evaluate_expression("2 * pi")         # 返回: 6.283185...

# 注意：表达式通过 AST 解析防止代码注入攻击
```

### 线性方程求解

```python
# 简单方程
result = calculator_solve_linear_equation("2x + 3 = 7")    # 返回: 2.0

# 负系数
result = calculator_solve_linear_equation("-3x + 6 = 0")   # 返回: 2.0

# 小数系数
result = calculator_solve_linear_equation("1.5x + 2 = 8")  # 返回: 4.0

# 自定义变量名
result = calculator_solve_linear_equation("3y + 1 = 7", "y")  # 返回: 2.0
```

## 📝 许可证

MIT License

## 📦 安装

### 从源码安装

```bash
git clone https://github.com/tengmmvp/Calculator_MCP.git
cd Calculator_MCP
pip install -e .
```

### 使用 uvx 直接运行（推荐）

```bash
# 直接从 GitHub 运行
uvx git+https://github.com/tengmmvp/Calculator_MCP

# 或者指定版本
uvx git+https://github.com/tengmmvp/Calculator_MCP@v1.1.0

# 或者运行命令
uvx git+https://github.com/tengmmvp/Calculator_MCP -- calculator-mcp-server
```

### 开发环境安装

```bash
git clone https://github.com/tengmmvp/Calculator_MCP.git
cd Calculator_MCP
./scripts/setup-dev.sh
```

## 🚀 部署

### Docker 部署

```bash
docker pull tengmmvp/calculator-mcp-server:latest
docker run -p 8080:8080 tengmmvp/calculator-mcp-server
```

### Claude Desktop 配置

将以下配置添加到 Claude Desktop：

**方法 1：使用 uvx 安装的命令**

```json
{
  "mcpServers": {
    "calculator": {
      "command": "uvx",
      "args": ["git+https://github.com/tengmmvp/Calculator_MCP"],
      "description": "Mathematical calculator with tools, resources, and prompts"
    }
  }
}
```

**方法 2：使用本地路径**

```json
{
  "mcpServers": {
    "calculator": {
      "command": "python",
      "args": ["src/server.py"],
      "cwd": "YOUR_PROJECT_PATH",
      "description": "Mathematical calculator with tools, resources, and prompts"
    }
  }
}
```

**注意**：

- 方法 1（推荐）：使用 uvx 自动管理依赖，无需手动安装
- 方法 2：请将 `YOUR_PROJECT_PATH` 替换为你克隆项目的实际路径
