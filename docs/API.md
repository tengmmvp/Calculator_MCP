# Calculator MCP Server API 文档

## 概述

Calculator MCP Server 是一个完全符合 Model Context Protocol (MCP) 规范的数学计算服务器，提供基础数学运算、统计计算、批量处理和数学问题解决功能。

## 架构

基于 FastMCP 框架构建：

- **FastMCP 2.13.1+** - 现代化 MCP 服务器框架
- **Pydantic 验证** - 自动类型验证和序列化
- **异步处理** - 原生支持并发操作
- **结构化输出** - 标准化响应格式

## 工具 API

### 基础数学运算

#### calculator_add

执行加法运算，支持多个数字相加。

**参数:**

- `numbers: List[float]` - 待相加的数字列表

**返回:** `CalculationResult`

```python
{
    "operation": "addition",
    "result": 10.0,
    "numbers": [1.0, 2.0, 3.0, 4.0],
    "timestamp": "2025-11-29T10:30:00"
}
```

**示例:**

```python
result = calculator_add([1, 2, 3, 4])  # 返回: 10.0
```

**错误处理:**

- 空列表返回 0.0
- 自动类型转换支持

#### calculator_subtract

执行顺序减法运算：第一个数 - 第二个数 - 第三个数...

**参数:**

- `numbers: List[float]` - 待相减的数字列表，至少包含一个数字

**返回:** `CalculationResult`

**示例:**

```python
result = calculator_subtract([10, 3, 2])  # 返回: 5.0 (10 - 3 - 2)
```

**错误处理:**

- 空列表抛出 `ValueError`
- 单个数字直接返回

#### calculator_multiply

执行乘法运算，支持多个数字相乘。

**参数:**

- `numbers: List[float]` - 待相乘的数字列表

**返回:** `CalculationResult`

**示例:**

```python
result = calculator_multiply([2, 3, 4])  # 返回: 24.0
```

**错误处理:**

- 空列表返回 1.0
- 包含零时返回 0.0

#### calculator_divide

执行除法运算。

**参数:**

- `numerator: float` - 被除数
- `denominator: float` - 除数

**返回:** `CalculationResult`

**示例:**

```python
result = calculator_divide(10, 2)  # 返回: 5.0
```

**错误处理:**

- 除数为零时抛出 `ValueError: "Division by zero is not allowed"`

#### calculator_power

执行幂运算。

**参数:**

- `base: float` - 底数
- `exponent: float` - 指数

**返回:** `CalculationResult`

**示例:**

```python
result = calculator_power(2, 3)    # 返回: 8.0
result = calculator_power(9, 0.5)  # 返回: 3.0 (平方根)
result = calculator_power(2, -2)   # 返回: 0.25
```

### 统计计算

#### calculator_statistics

执行统计计算。

**参数:**

- `numbers: List[float]` - 用于统计的数字列表
- `operation: str` - 统计操作类型

**支持的操作:**

- `"mean"` - 算术平均值
- `"median"` - 中位数
- `"mode"` - 众数
- `"stdev"` - 标准差
- `"variance"` - 方差

**返回:** `StatisticsResult`

```python
{
    "operation": "statistics_mean",
    "result": 3.0,
    "data": [1.0, 2.0, 3.0, 4.0, 5.0],
    "count": 5
}
```

**示例:**

```python
# 计算均值
result = calculator_statistics([1, 2, 3, 4, 5], "mean")      # 返回: 3.0

# 计算中位数
result = calculator_statistics([1, 2, 3, 4], "median")        # 返回: 2.5

# 计算标准差
result = calculator_statistics([1, 2, 3, 4, 5], "stdev")     # 返回: 1.58

# 计算方差
result = calculator_statistics([1, 2, 3, 4, 5], "variance")  # 返回: 2.5
```

**错误处理:**

- 空列表抛出 `ValueError: "Numbers list cannot be empty"`
- 无效操作抛出 `ValueError: "Unknown operation: {operation}"`
- 单个元素的方差和标准差返回 0

### 批量计算

#### calculator_batch_calculations

执行批量计算，支持混合多种运算类型。

**参数:**

- `operations: List[Dict[str, Any]]` - 批量操作列表

**操作格式:**

```python
{
    "tool": "add|subtract|multiply|divide|power",
    "args": {
        # 根据工具类型提供相应参数
        "numbers": [1, 2, 3],              # for add, subtract, multiply
        "numerator": 10, "denominator": 2, # for divide
        "base": 2, "exponent": 3           # for power
    }
}
```

**返回:** `List[CalculationResult]`

**示例:**

```python
operations = [
    {"tool": "add", "args": {"numbers": [1, 2, 3]}},
    {"tool": "multiply", "args": {"numbers": [2, 3]}},
    {"tool": "divide", "args": {"numerator": 10, "denominator": 2}},
    {"tool": "power", "args": {"base": 2, "exponent": 3}}
]
results = calculator_batch_calculations(operations)
# 返回: [6.0, 6.0, 5.0, 8.0]
```

**错误处理:**

- 空操作列表抛出 `ValueError: "At least one calculation is required"`
- 无效操作格式抛出详细错误信息
- 操作失败返回 `nan` 结果，不中断整个批处理

## 资源 API

### calculator://constants

提供常用数学常数。

**返回:** Markdown 格式的数学常数列表

**内容:**

- π (Pi): 3.14159265359
- e (Euler's Number): 2.71828182846
- φ (Golden Ratio): 1.61803398875
- √2 (Square Root of 2): 1.41421356237
- √3 (Square Root of 3): 1.73205080757

**示例:**

```python
constants = get_mathematical_constants()
print(constants)
# 输出:
# # Mathematical Constants
#
# - **π (Pi)**: 3.14159265359
# - **e (Euler's Number)**: 2.71828182846
# ...
```

### calculator://formulas

提供常用数学公式。

**返回:** Markdown 格式的数学公式列表

**内容:**

- Area of Circle: A = πr²
- Area of Triangle: A = ½bh
- Quadratic Formula: x = (-b ± √(b²-4ac)) / 2a
- Pythagorean Theorem: a² + b² = c²
- Distance Formula: d = √[(x₂-x₁)² + (y₂-y₁)²]
- Slope Formula: m = (y₂-y₁) / (x₂-x₁)

## 提示 API

### math_problem_solver

生成数学问题的结构化解题方法。

**参数:**

- `problem: str` - 数学问题描述

**返回:** 包含结构化解题方法的提示文本

**结构包含:**

1. **Understand the Problem** - 问题理解
2. **Identify the Method** - 方法识别
3. **Step-by-step Solution** - 分步解答
4. **Final Answer** - 最终答案

**示例:**

```python
prompt = math_problem_solver("Find the area of a circle with radius 5")
# 返回详细的解题指导，包含步骤和验证方法
```

### calculation_checker

生成数学计算的验证和解释提示。

**参数:**

- `calculation: str` - 待验证的数学计算表达式

**返回:** 包含计算验证和解释的提示文本

**内容包含:**

1. **Verification** - 计算正确性验证
2. **Step-by-step breakdown** - 分步解析
3. **Method explanation** - 方法原理
4. **Alternative approaches** - 替代方法
5. **Common pitfalls** - 常见错误

**示例:**

```python
prompt = calculation_checker("2 + 2 = 4")
# 返回详细的验证和解释
```

## 数据模型

### CalculationResult

```python
{
    "operation": str,     # 操作类型
    "result": float,      # 计算结果
    "numbers": List[float],  # 参与计算的数字
    "timestamp": str      # 计算时间戳 (ISO 8601格式)
}
```

### StatisticsResult

```python
{
    "operation": str,     # 操作类型 (statistics_{op})
    "result": float,      # 统计结果
    "data": List[float],  # 原始数据
    "count": int          # 数据点数量
}
```

## 性能特性

### 响应时间

- **简单运算**: < 1ms
- **统计计算**: < 5ms
- **批量操作**: < 100ms (100 个操作)
- **大数据集**: < 1s (1000 个数字)

### 并发支持

- **原生异步**: 支持 100+并发请求
- **内存优化**: 优化的 FastMCP 框架
- **无状态设计**: 支持水平扩展

### 错误恢复

- **优雅降级**: 部分失败不中断整体操作
- **详细错误信息**: 便于调试和问题定位
- **输入验证**: 完整的参数验证机制

## MCP 合规性

### 100% 合规特性

- ✅ **工具注册**: 完整的工具描述和参数验证
- ✅ **资源提供**: 标准化的资源访问接口
- ✅ **提示系统**: 符合 MCP 规范的提示功能
- ✅ **错误处理**: 标准化的错误响应格式
- ✅ **类型安全**: 完整的 Pydantic 模型验证

### 协议版本

- **MCP**: v1.0+
- **FastMCP**: v2.13.1+

## 集成示例

### Claude Desktop

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

### Python 客户端

```python
import asyncio
from mcp import ClientSession, StdioServerParameters

async def use_calculator():
    server_params = StdioServerParameters(
        command="python",
        args=["src/server.py"]
    )

    async with ClientSession(server_params) as session:
        # 初始化
        await session.initialize()

        # 使用工具
        result = await session.call_tool("calculator_add", {"numbers": [1, 2, 3]})
        print(f"结果: {result}")

        # 访问资源
        constants = await session.read_resource("calculator://constants")
        print(f"常数: {constants}")

        # 使用提示
        prompt = await session.get_prompt("math_problem_solver", {"problem": "2+2"})
        print(f"提示: {prompt}")

asyncio.run(use_calculator())
```

## 错误代码参考

| 错误类型        | 错误信息                               | 原因               | 解决方案           |
| --------------- | -------------------------------------- | ------------------ | ------------------ |
| ValueError      | "Division by zero is not allowed"      | 除法运算除数为零   | 检查除数参数       |
| ValueError      | "Numbers list cannot be empty"         | 统计计算输入为空   | 提供有效数字列表   |
| ValueError      | "Unknown operation: {operation}"       | 无效统计操作       | 使用有效的操作类型 |
| ValueError      | "At least one calculation is required" | 批量计算空操作列表 | 提供至少一个操作   |
| ValidationError | Pydantic 验证错误                      | 参数类型或格式错误 | 检查参数类型和格式 |
