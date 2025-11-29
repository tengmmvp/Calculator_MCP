#!/usr/bin/env python3
"""
Calculator MCP Server

基于 FastMCP 框架构建的数学计算服务器。
"""

import ast
from datetime import datetime
import math
import statistics
from typing import Any, Dict, List

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

# 创建 FastMCP 实例
mcp = FastMCP("Calculator MCP Server")


class CalculationResult(BaseModel):
    """计算结果模型。"""
    operation: str = Field(description="操作类型")
    result: float = Field(description="计算结果")
    numbers: List[float] = Field(description="参与计算的数字列表")
    timestamp: str = Field(description="计算时间戳")


class StatisticsResult(BaseModel):
    """统计结果模型。"""
    operation: str = Field(description="统计操作类型")
    result: float = Field(description="统计结果")
    data: List[float] = Field(description="输入数据")
    count: int = Field(description="数据点数量")


# ========== 基础算术工具 ==========

@mcp.tool()
def calculator_add(numbers: List[float]) -> CalculationResult:
    """执行加法运算。

    Args:
        numbers: 待相加的数字列表

    Returns:
        CalculationResult: 加法运算结果

    Raises:
        ValueError: 输入列表为空时抛出
    """
    result = sum(numbers)
    return CalculationResult(
        operation="addition",
        result=result,
        numbers=numbers,
        timestamp=datetime.now().isoformat()
    )


@mcp.tool()
def calculator_subtract(numbers: List[float]) -> CalculationResult:
    """执行连续减法运算。

    按顺序执行：第一个数 - 第二个数 - 第三个数...

    Args:
        numbers: 待相减的数字列表，至少包含一个数字

    Returns:
        CalculationResult: 减法运算结果

    Raises:
        ValueError: 输入列表为空时抛出
    """
    if not numbers:
        raise ValueError("At least one number is required")
    result = numbers[0]
    for num in numbers[1:]:
        result -= num
    return CalculationResult(
        operation="subtraction",
        result=result,
        numbers=numbers,
        timestamp=datetime.now().isoformat()
    )


@mcp.tool()
def calculator_multiply(numbers: List[float]) -> CalculationResult:
    """执行乘法运算。

    Args:
        numbers: 待相乘的数字列表

    Returns:
        CalculationResult: 乘法运算结果

    Raises:
        ValueError: 输入列表为空时抛出
    """
    result = 1.0
    for num in numbers:
        result *= num
    return CalculationResult(
        operation="multiplication",
        result=result,
        numbers=numbers,
        timestamp=datetime.now().isoformat()
    )


@mcp.tool()
def calculator_divide(numerator: float, denominator: float) -> CalculationResult:
    """执行除法运算。

    Args:
        numerator: 被除数
        denominator: 除数

    Returns:
        CalculationResult: 除法运算结果

    Raises:
        ValueError: 除数为零时抛出
    """
    if denominator == 0:
        raise ValueError("Division by zero is not allowed")
    result = numerator / denominator
    return CalculationResult(
        operation="division",
        result=result,
        numbers=[numerator, denominator],
        timestamp=datetime.now().isoformat()
    )


@mcp.tool()
def calculator_power(base: float, exponent: float) -> CalculationResult:
    """执行幂运算。

    Args:
        base: 底数
        exponent: 指数

    Returns:
        CalculationResult: 幂运算结果
    """
    result = base ** exponent
    return CalculationResult(
        operation="power",
        result=result,
        numbers=[base, exponent],
        timestamp=datetime.now().isoformat()
    )


class MixedExpressionResult(BaseModel):
    """混合表达式计算结果模型。"""
    operation: str = Field(description="操作类型")
    expression: str = Field(description="原始表达式")
    result: float = Field(description="计算结果")
    steps: List[str] = Field(description="计算步骤")
    timestamp: str = Field(description="计算时间戳")


# ========== 混合运算工具 ==========

@mcp.tool()
def calculator_evaluate_expression(expression: str) -> MixedExpressionResult:
    """计算数学表达式，支持混合运算和数学函数。

    支持的运算符：+, -, *, /, **, //, %
    支持的函数：sin, cos, tan, log, log10, sqrt, abs, round
    支持的常数：pi, e

    Args:
        expression: 数学表达式字符串，如 "2 + 3 * 4 - 1"

    Returns:
        MixedExpressionResult: 表达式计算结果，包含步骤说明

    Raises:
        ValueError: 表达式无效或不安全时抛出
    """

    # 安全的数学函数映射
    safe_functions = {
        'sin': math.sin,
        'cos': math.cos,
        'tan': math.tan,
        'log': math.log,
        'log10': math.log10,
        'sqrt': math.sqrt,
        'abs': abs,
        'round': round,
        'pow': pow,
        'min': min,
        'max': max,
        'sum': sum,
        'len': len,
    }

    # 安全的常数映射
    safe_constants = {
        'pi': math.pi,
        'e': math.e,
        'tau': math.tau,
    }

    try:
        # 清理和验证表达式
        expression = expression.strip()
        if not expression:
            raise ValueError("表达式不能为空")

        # 检查潜在的安全风险
        dangerous_keywords = ['import', 'exec', 'eval', 'open', 'file', '__']
        for keyword in dangerous_keywords:
            if keyword in expression.lower():
                raise ValueError(f"表达式包含不安全的关键字: {keyword}")

        # 解析表达式
        try:
            node = ast.parse(expression, mode='eval')
        except SyntaxError as e:
            raise ValueError(f"表达式语法错误: {str(e)}")

        # 验证AST节点是否安全
        def check_safety(node):
            if isinstance(node, ast.Expression):
                return check_safety(node.body)
            elif isinstance(node, ast.BinOp):
                return check_safety(node.left) and check_safety(node.right)
            elif isinstance(node, ast.UnaryOp):
                return check_safety(node.operand)
            elif isinstance(node, ast.Constant):
                return isinstance(node.value, (int, float))
            elif isinstance(node, ast.Name):
                return node.id in safe_functions or node.id in safe_constants
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                    if func_name not in safe_functions:
                        return False
                    # 检查所有参数是否安全
                    return all(check_safety(arg) for arg in node.args)
                return False
            elif isinstance(node, ast.Attribute):
                # 允许 math.xxx 格式的调用
                if isinstance(node.value, ast.Name) and node.value.id == 'math':
                    return True
                return False
            else:
                # 拒绝其他类型的节点
                return False

        if not check_safety(node):
            raise ValueError("表达式包含不安全的操作")

        # 构建安全的执行环境
        safe_dict = {}
        safe_dict.update(safe_functions)
        safe_dict.update(safe_constants)
        safe_dict.update({
            '__builtins__': {},
            '__import__': None,
        })

        # 计算表达式
        result = eval(compile(node, '<string>', 'eval'), safe_dict)

        # 生成计算步骤说明
        steps = [
            f"原始表达式: {expression}",
            f"解析AST节点: {ast.dump(node)}",
            f"执行计算: {expression}",
            f"计算结果: {result}"
        ]

        return MixedExpressionResult(
            operation="mixed_expression",
            expression=expression,
            result=float(result),
            steps=steps,
            timestamp=datetime.now().isoformat()
        )

    except Exception as e:
        raise ValueError(f"表达式计算失败: {str(e)}")


@mcp.tool()
def calculator_solve_linear_equation(equation: str, variable: str = "x") -> MixedExpressionResult:
    """解简单的一元线性方程。

    支持格式：ax + b = c 或类似形式

    Args:
        equation: 一元线性方程字符串，如 "2x + 3 = 7"
        variable: 变量名，默认为"x"

    Returns:
        MixedExpressionResult: 方程求解结果

    Raises:
        ValueError: 方程格式无效或无法求解时抛出
    """

    try:
        equation = equation.strip()
        if '=' not in equation:
            raise ValueError("方程必须包含等号 '='")

        left, right = equation.split('=', 1)
        left = left.strip()
        right = right.strip()

        # 解析左边和右边
        def parse_side(side):
            # 将变量替换为符号，然后计算常数项
            # 简化版本：处理 ax + b 或 a - bx 等格式

            # 移除所有空格
            side = side.replace(' ', '')

            # 查找变量项
            import re
            variable_pattern = f'([+-]?\\d*\\.?\\d*){re.escape(variable)}'
            matches = re.findall(variable_pattern, side)

            # 计算变量系数
            coeff_sum = 0
            for match in matches:
                if match == '' or match == '+':
                    coeff_sum += 1
                elif match == '-':
                    coeff_sum -= 1
                else:
                    coeff_sum += float(match)

            # 移除变量项，计算常数
            side_without_var = re.sub(variable_pattern, '', side)
            side_without_var = re.sub(f'[+-]{re.escape(variable)}', '', side_without_var)

            # 计算常数项
            if side_without_var == '':
                constant = 0
            elif side_without_var == '+':
                constant = 0
            elif side_without_var == '-':
                constant = 0
            else:
                try:
                    constant = eval(side_without_var, {'__builtins__': {}}, {})
                except:
                    constant = 0

            return coeff_sum, constant

        left_coeff, left_const = parse_side(left)
        right_coeff, right_const = parse_side(right)

        # 解方程：left_coeff * x + left_const = right_coeff * x + right_const
        # 移项：(left_coeff - right_coeff) * x = right_const - left_const
        total_coeff = left_coeff - right_coeff
        total_const = right_const - left_const

        if abs(total_coeff) < 1e-10:
            if abs(total_const) < 1e-10:
                result = float('inf')  # 无穷多解
                solution = "方程有无穷多解"
            else:
                result = float('nan')  # 无解
                solution = "方程无解"
        else:
            result = total_const / total_coeff
            solution = f"{variable} = {result}"

        steps = [
            f"原方程: {equation}",
            f"解析左边: {left_coeff} * {variable} + {left_const}",
            f"解析右边: {right_coeff} * {variable} + {right_const}",
            f"移项: ({left_coeff} - {right_coeff}) * {variable} = {right_const} - {left_const}",
            f"化简: {total_coeff} * {variable} = {total_const}",
            f"求解: {solution}"
        ]

        return MixedExpressionResult(
            operation="linear_equation",
            expression=equation,
            result=result,
            steps=steps,
            timestamp=datetime.now().isoformat()
        )

    except Exception as e:
        raise ValueError(f"方程求解失败: {str(e)}")


# ========== 统计工具 ==========

@mcp.tool()
def calculator_statistics(numbers: List[float], operation: str) -> StatisticsResult:
    """执行统计运算。

    支持的统计操作：mean(均值), median(中位数), mode(众数),
    stdev(标准差), variance(方差)。

    Args:
        numbers: 用于统计的数字列表
        operation: 统计操作类型

    Returns:
        StatisticsResult: 统计计算结果

    Raises:
        ValueError: 输入列表为空或操作类型无效时抛出
    """
    if not numbers:
        raise ValueError("Numbers list cannot be empty")

    if operation == "mean":
        result = statistics.mean(numbers)
    elif operation == "median":
        result = statistics.median(numbers)
    elif operation == "mode":
        result = statistics.mode(numbers)
    elif operation == "stdev":
        result = statistics.stdev(numbers) if len(numbers) > 1 else 0
    elif operation == "variance":
        result = statistics.variance(numbers) if len(numbers) > 1 else 0
    else:
        raise ValueError(f"Unknown operation: {operation}")

    return StatisticsResult(
        operation=f"statistics_{operation}",
        result=result,
        data=numbers,
        count=len(numbers)
    )


# ========== 批量计算工具 ==========

@mcp.tool()
def calculator_batch_calculations(
    operations: List[Dict[str, Any]] = Field(
        description="批量计算操作列表。每个操作包含：tool(工具名称：add/subtract/multiply/divide/power)、args(工具参数，如 {'numbers': [1, 2, 3]})"
    )
) -> List[CalculationResult]:
    """执行批量计算。

    Args:
        operations: 包含工具名称和参数的操作列表

    Returns:
        List[CalculationResult]: 所有计算结果列表

    Raises:
        ValueError: 操作列表为空或无效时抛出
    """
    if not operations:
        raise ValueError("At least one calculation is required")

    results = []

    for i, op in enumerate(operations):
        if not isinstance(op, dict):
            raise ValueError(f"Operation {i+1} must be a dictionary")

        tool_name = op.get("tool")
        args = op.get("args", {})

        if not tool_name:
            raise ValueError(f"Operation {i+1} missing 'tool' field")

        try:
            if tool_name == "add":
                numbers = args.get("numbers", [])
                if not numbers:
                    raise ValueError(f"Operation {i+1}: 'add' requires 'numbers' parameter")
                result = calculator_add(numbers)
            elif tool_name == "subtract":
                numbers = args.get("numbers", [])
                if not numbers:
                    raise ValueError(f"Operation {i+1}: 'subtract' requires 'numbers' parameter")
                result = calculator_subtract(numbers)
            elif tool_name == "multiply":
                numbers = args.get("numbers", [])
                if not numbers:
                    raise ValueError(f"Operation {i+1}: 'multiply' requires 'numbers' parameter")
                result = calculator_multiply(numbers)
            elif tool_name == "divide":
                numerator = args.get("numerator")
                denominator = args.get("denominator")
                if numerator is None or denominator is None:
                    raise ValueError(f"Operation {i+1}: 'divide' requires 'numerator' and 'denominator' parameters")
                result = calculator_divide(numerator, denominator)
            elif tool_name == "power":
                base = args.get("base")
                exponent = args.get("exponent")
                if base is None or exponent is None:
                    raise ValueError(f"Operation {i+1}: 'power' requires 'base' and 'exponent' parameters")
                result = calculator_power(base, exponent)
            else:
                raise ValueError(f"Operation {i+1}: Unknown tool '{tool_name}'")

            results.append(result)

        except Exception as e:
            error_result = CalculationResult(
                operation=f"batch_error_{tool_name}",
                result=float('nan'),
                numbers=args.get("numbers", []),
                timestamp=datetime.now().isoformat()
            )
            results.append(error_result)

    return results


# ========== 资源定义 ==========

@mcp.resource("calculator://constants")
def get_mathematical_constants() -> str:
    """获取常用数学常数。

    Returns:
        str: Markdown 格式的数学常数列表
    """
    constants = {
        "π (Pi)": "3.14159265359",
        "e (Euler's Number)": "2.71828182846",
        "φ (Golden Ratio)": "1.61803398875",
        "√2 (Square Root of 2)": "1.41421356237",
        "√3 (Square Root of 3)": "1.73205080757"
    }

    content = "# Mathematical Constants\n\n"
    for name, value in constants.items():
        content += f"- **{name}**: {value}\n"

    return content


@mcp.resource("calculator://formulas")
def get_common_formulas() -> str:
    """获取常用数学公式。

    Returns:
        str: Markdown 格式的数学公式列表
    """
    formulas = [
        "Area of Circle: A = πr²",
        "Area of Triangle: A = ½bh",
        "Quadratic Formula: x = (-b ± √(b²-4ac)) / 2a",
        "Pythagorean Theorem: a² + b² = c²",
        "Distance Formula: d = √[(x₂-x₁)² + (y₂-y₁)²]",
        "Slope Formula: m = (y₂-y₁) / (x₂-x₁)"
    ]

    content = "# Common Mathematical Formulas\n\n"
    for i, formula in enumerate(formulas, 1):
        content += f"{i}. {formula}\n"

    return content


# ========== 提示定义 ==========

@mcp.prompt()
def math_problem_solver(problem: str) -> str:
    """生成数学问题的结构化解题方法。

    Args:
        problem: 数学问题描述

    Returns:
        str: 包含结构化解题方法的提示文本
    """
    prompt_content = f"""You are a mathematical problem solver. Please help solve this problem:

**Problem:** {problem}

**Structured Approach:**
1. **Understand the Problem**
   - What are we trying to find?
   - What information is given?
   - Are there any constraints or assumptions?

2. **Identify the Method**
   - What mathematical concepts apply?
   - Which formulas or techniques are relevant?
   - Is there a preferred approach?

3. **Step-by-step Solution**
   - Show each calculation clearly
   - Explain the reasoning
   - Verify each step

4. **Final Answer**
   - State the result clearly
   - Check if it makes sense
   - Consider alternative approaches if applicable

Please provide a detailed, educational solution."""

    return prompt_content


@mcp.prompt()
def calculation_checker(calculation: str) -> str:
    """生成数学计算的验证和解释提示。

    Args:
        calculation: 待验证的数学计算表达式

    Returns:
        str: 包含计算验证和解释的提示文本
    """
    prompt_content = f"""Please review and explain this mathematical calculation:

**Calculation:** {calculation}

**Please provide:**
1. **Verification** - Is the calculation correct?
2. **Step-by-step breakdown** - Show how to arrive at the result
3. **Method explanation** - What mathematical principles are being used?
4. **Alternative approaches** - Are there other ways to solve this?
5. **Common pitfalls** - What mistakes should be avoided in similar calculations?

Provide an educational explanation that helps understand both the process and the underlying mathematics."""

    return prompt_content


def cli_main():
    """CLI entry point for the calculator MCP server."""
    print("Starting Calculator MCP Server with FastMCP...")
    mcp.run()


if __name__ == "__main__":
    cli_main()
