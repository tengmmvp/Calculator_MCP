# Calculator MCP Server

一个完全符合 Model Context Protocol (MCP) 规范的数学计算服务器。

## 🔄 版本 1.1.0 重大更新

**从 v1.0 到 v1.1.0，我们进行了重大架构改进：**

- ✨ **统一工具架构**：将 9 个独立工具合并为 1 个智能的 `calculate` 工具
- 🧠 **智能类型识别**：工具自动检测表达式类型并执行相应计算
- 📊 **双格式输出**：支持 Markdown 和 JSON 两种输出格式
- 🛡️ **增强的安全性**：改进的输入验证和 AST 解析
- 📝 **更好的文档**：详细的 docstrings 和使用示例

## ✨ 特性

- 🧮 **单一统一工具**：一个 `calculate` 工具处理所有数学运算
- 🤖 **自动类型检测**：智能识别基础运算、统计计算、方程求解、批量处理
- 📐 **丰富的函数支持**：20+ 内置数学函数和统计函数
- 📊 **双输出格式**：Markdown（人类可读）和 JSON（机器可读）
- 📚 **资源系统**：数学常数和公式库
- 💡 **智能提示**：数学问题解决和计算验证助手

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
    "calculator_mcp": {
      "command": "python",
      "args": ["<PROJECT_PATH>/calculator_mcp/server.py"],
      "env": {
        "PYTHONPATH": "<PROJECT_PATH>"
      },
      "description": "Unified mathematical calculator with expression auto-detection"
    }
  }
}
```

### 运行服务器

```bash
# 直接运行
python calculator_mcp/server.py

# 开发环境运行（推荐，更好的调试支持）
fastmcp dev calculator_mcp/server.py
```

## 📁 项目结构

```
Calculator_MCP/
├── calculator_mcp/               # 🔧 源代码目录
│   ├── __init__.py               # 包初始化文件
│   └── server.py                 # 主服务器文件（包含所有 MCP 功能）
├── docs/                         # 📚 文档目录
├── config/                       # ⚙️ 配置文件目录
│   └── claude_desktop_config.json # 🖥️ Claude Desktop 配置模板
├── requirements.txt              # 📋 Python 依赖列表
├── pyproject.toml                # 📦 项目配置文件
├── README.md                     # 📖 项目说明文档
├── CHANGELOG.md                  # 📝 版本更新日志
└── .gitignore                    # 🚫 Git 忽略文件规则
```

## 🔧 统一计算工具

### `calculate(expression: str, variable: str = "x", response_format: str = "markdown")`

一个智能计算工具，自动识别表达式类型并执行相应计算：

#### 支持的运算类型

**基础运算示例：**

- `2 + 3 * 4` - 基础算术
- `(10 + 5) / 3` - 带括号的运算
- `2**3` - 幂运算（注意：使用 `**` 而不是 `^`）

**数学函数示例：**

三角函数：

- `sin(pi/2)` - 正弦函数
- `cos(0)` - 余弦函数
- `tan(pi/4)` - 正切函数

对数函数：

- `log(100)` - 自然对数
- `log10(1000)` - 常用对数（以 10 为底）

其他函数：

- `sqrt(16)` - 平方根
- `abs(-5)` - 绝对值
- `round(3.14159)` - 四舍五入
- `pow(2, 8)` - 幂运算

聚合函数：

- `max([1, 5, 3])` - 最大值
- `min([1, 5, 3])` - 最小值
- `sum([1, 2, 3])` - 求和
- `len([1, 2, 3, 4])` - 长度

**统计计算示例：**

- `mean([1,2,3,4,5])` - 平均值
- `stdev([1,2,3,4,5])` - 标准差
- `median([1,3,5,7,9])` - 中位数

**线性方程示例：**

- `2x + 3 = 7` - 解方程
- `3*y - 5 = 10` - 使用自定义变量名

**批量计算示例：**

- `2+3; 4*5; 10/2` - 多个表达式同时计算
- `sin(pi/2); cos(0); 2**3` - 混合批量计算

#### 参数说明

- `expression` (必需): 数学表达式或方程字符串
- `variable` (可选, 默认 "x"): 线性方程中的变量名
- `response_format` (可选, 默认 "markdown"):
  - `"markdown"` - 人类可读格式
  - `"json"` - 机器可读格式

### 资源系统

- `calculator://constants` - 数学常数资源

  - π (Pi): 3.14159265359
  - e (Euler's Number): 2.71828182846
  - φ (Golden Ratio): 1.61803398875
  - √2 (Square Root of 2): 1.41421356237
  - √3 (Square Root of 3): 1.73205080757

- `calculator://formulas` - 常用数学公式资源
  - 圆的面积：A = πr²
  - 三角形面积：A = ½bh
  - 一元二次方程：x = (-b ± √(b²-4ac)) / 2a
  - 勾股定理：a² + b² = c²
  - 平面距离公式：d = √[(x₂-x₁)² + (y₂-y₁)²]
  - 直线斜率公式：m = (y₂-y₁) / (x₂-x₁)

### 提示系统

- `math_problem_solver(problem: str)` - 结构化数学问题解决助手

  - 提供五步法解题框架
  - 包含理解、分析、计算、验证和答案生成步骤

- `calculation_checker(calculation: str)` - 计算验证和解释工具
  - 验证计算的正确性
  - 提供分步解释和替代方法
  - 识别常见错误和陷阱

## 💡 使用示例

### 在 Claude Desktop 中使用

直接在 Claude 中输入数学表达式，工具会自动调用：

```
用户: 计算 2 + 3 * 4
Claude: 2 + 3 * 4 = 14

用户: 解方程 2x + 3 = 7
Claude: x = 2.0

用户: 计算数组的平均值 mean([1,2,3,4,5])
Claude: 平均值是 3.0

用户: 批量计算 2+3; 4*5; 10/2
Claude:
- 2+3 = 5
- 4*5 = 20
- 10/2 = 5
```

### 不同输出格式

**Markdown 格式（默认）:**

```python
calculate("2 + 3 * 4", response_format="markdown")
```

返回格式化的 Markdown 文本，便于阅读。

**JSON 格式（程序化处理）:**

```python
calculate("2 + 3 * 4", response_format="json")
```

返回结构化的 JSON 数据：

```json
{
  "operation": "expression",
  "expression": "2 + 3 * 4",
  "result": 14.0,
  "timestamp": "2025-12-08T10:30:00.000000",
  "steps": ["计算表达式: 2 + 3 * 4", "结果: 14.0"]
}
```

### 实际使用场景

**日常计算:**

- `calculate("15% of 240")` - 百分比计算
- `calculate("sqrt(169) + 7")` - 组合运算
- `calculate("2**10")` - 大数幂运算

**统计分析:**

- `calculate("mean([85, 90, 78, 92, 88])")` - 成绩分析
- `calculate("stdev([1,2,3,4,5,6])")` - 标准差计算

**方程求解:**

- `calculate("3x - 9 = 0")` - 简单方程
- `calculate("0.5y + 2.5 = 10", "y")` - 自定义变量

**批量处理:**

- `calculate("1*2; 3*4; 5*6; 7*8")` - 多个计算
- `calculate("sum([1,2,3]); mean([4,5,6]); max([7,8,9])")` - 混合统计

## 📝 许可证

MIT License

## 📦 安装

### 从源码安装

```bash
git clone https://github.com/tengmmvp/Calculator_MCP.git
cd Calculator_MCP
pip install -e .
```

### 本地运行（开发模式）

```bash
# 克隆项目
git clone https://github.com/tengmmvp/Calculator_MCP.git
cd Calculator_MCP

# 安装依赖
pip install -r requirements.txt

# 运行服务器
python calculator_mcp/server.py

# 或使用 FastMCP 开发模式（推荐，支持热重载）
fastmcp dev calculator_mcp/server.py
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
    "calculator_mcp": {
      "command": "uvx",
      "args": ["git+https://github.com/tengmmvp/Calculator_MCP"],
      "description": "Unified mathematical calculator with expression auto-detection"
    }
  }
}
```

**方法 2：使用本地路径**

```json
{
  "mcpServers": {
    "calculator_mcp": {
      "command": "python",
      "args": ["<PROJECT_PATH>/calculator_mcp/server.py"],
      "env": {
        "PYTHONPATH": "<PROJECT_PATH>"
      },
      "description": "Unified mathematical calculator with expression auto-detection"
    }
  }
}
```

**注意**：

- 方法 1（推荐）：使用 uvx 自动管理依赖，无需手动安装
- 方法 2：请将 `<PROJECT_PATH>` 替换为项目的实际根目录路径
  - Windows 示例：`C:\\Users\\YourName\\Projects\\Calculator_MCP`
  - macOS/Linux 示例：`/home/yourname/projects/Calculator_MCP`
  - 路径使用正斜杠或双反斜杠均可

## 🎯 功能概览

### 支持的运算类型

| 类型     | 示例            | 说明                         |
| -------- | --------------- | ---------------------------- |
| 基础运算 | `2 + 3 * 4`     | 加减乘除、幂运算、取模等     |
| 数学函数 | `sin(pi/2)`     | 三角、对数、指数等函数       |
| 统计计算 | `mean([1,2,3])` | 均值、中位数、标准差、方差等 |
| 方程求解 | `2x + 3 = 7`    | 一元线性方程求解             |
| 批量计算 | `1+2; 3*4; 5/6` | 多个表达式同时计算           |

### 支持的数学函数（共 20 个）

**三角函数**：sin, cos, tan
**对数函数**：log, log10
**其他函数**：sqrt, abs, round, pow
**聚合函数**：min, max, sum, len
**统计函数**：mean, median, mode, stdev, variance

### 安全特性

- 🔒 AST 安全解析，防止代码注入
- 🛡️ 严格的输入验证
- ⚠️ 零除保护
- 📝 清晰的错误提示
