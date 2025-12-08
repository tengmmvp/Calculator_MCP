#!/usr/bin/env python3
"""
Calculator MCP Server

基于 FastMCP 框架构建的数学计算服务器，提供统一的数学计算接口。

支持的功能：
    - 基础算术运算（加减乘除、幂运算）
    - 数学函数计算（三角函数、对数、平方根等）
    - 统计分析（均值、中位数、标准差、方差）
    - 线性方程求解（一元一次方程）
    - 批量计算处理
    - 多种输出格式（Markdown、JSON）

模块常量：
    CHARACTER_LIMIT: 响应内容的最大字符数限制，防止超长输出
"""

# ========== 标准库导入 ==========
import ast
import re
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

# ========== 数学与统计库导入 ==========
import math
import statistics

# ========== 第三方库导入 ==========
from fastmcp import FastMCP
from pydantic import BaseModel, Field, ConfigDict, field_validator

# ========== MCP 服务器实例 ==========
mcp = FastMCP("calculator_mcp")

# ========== 模块级常量 ==========
CHARACTER_LIMIT = 25000  # 最大响应字符数，防止超长输出


# ========== 数据模型定义 ==========

class CalculationResult(BaseModel):
    """基础计算结果数据模型。
    
    用于封装单次基础数学计算的结果信息。
    
    Attributes:
        operation: 执行的操作类型标识
        result: 计算得到的数值结果
        numbers: 参与计算的原始数字列表
        timestamp: ISO 格式的计算时间戳
    """
    operation: str = Field(description="操作类型")
    result: float = Field(description="计算结果")
    numbers: List[float] = Field(description="参与计算的数字列表")
    timestamp: str = Field(description="计算时间戳")


class StatisticsResult(BaseModel):
    """统计计算结果数据模型。
    
    用于封装统计分析计算的结果信息。
    
    Attributes:
        operation: 统计操作类型（如 mean、median、stdev 等）
        result: 统计计算得到的数值结果
        data: 原始输入数据列表
        count: 参与统计的数据点总数
    """
    operation: str = Field(description="统计操作类型")
    result: float = Field(description="统计结果")
    data: List[float] = Field(description="输入数据")
    count: int = Field(description="数据点数量")


class ResponseFormat(str, Enum):
    """响应输出格式枚举类型。
    
    定义计算结果的输出格式选项。
    
    Attributes:
        MARKDOWN: 人类可读的 Markdown 格式
        JSON: 机器可读的 JSON 结构化格式
    """
    MARKDOWN = "markdown"
    JSON = "json"


class UnifiedCalculationResult(BaseModel):
    """统一计算结果数据模型。
    
    通用的计算结果封装模型，支持多种计算类型的结果表示。
    包含严格的数据验证规则和可选的扩展字段。
    
    Attributes:
        operation: 操作类型标识
        expression: 原始输入表达式字符串
        result: 计算结果，可以是单个数值、列表或字典
        timestamp: ISO 格式的计算时间戳
        steps: 可选的计算步骤说明列表
        data: 可选的输入数据列表（统计计算时使用）
        batch_results: 可选的批量计算结果列表
        error: 可选的错误信息字符串
        truncated: 响应是否因长度限制被截断
        truncation_message: 截断时的提示信息
    """
    model_config = ConfigDict(
        str_strip_whitespace=True,    # 自动去除字符串首尾空白
        validate_assignment=True,     # 启用赋值验证
        extra='forbid'                # 禁止额外字段
    )

    operation: str = Field(
        description="操作类型",
        min_length=1,
        max_length=50
    )
    expression: str = Field(
        description="原始表达式",
        min_length=1,
        max_length=1000
    )
    result: Union[float, List[float], Dict[str, Any]] = Field(
        description="计算结果"
    )
    timestamp: str = Field(
        description="计算时间戳"
    )
    steps: Optional[List[str]] = Field(
        default=None,
        description="计算步骤"
    )
    data: Optional[List[float]] = Field(
        default=None,
        description="输入数据（统计计算时）"
    )
    batch_results: Optional[List['UnifiedCalculationResult']] = Field(
        default=None,
        description="批量计算结果"
    )
    error: Optional[str] = Field(
        default=None,
        description="错误信息（如果有）",
        max_length=500
    )
    truncated: Optional[bool] = Field(
        default=False,
        description="响应是否被截断"
    )
    truncation_message: Optional[str] = Field(
        default=None,
        description="截断提示信息"
    )


class CalculateInput(BaseModel):
    """计算工具输入参数验证模型。
    
    定义并验证 calculate 工具的输入参数，确保数据格式正确性。
    
    Attributes:
        expression: 数学表达式或方程字符串
        variable: 线性方程中的变量名（默认为 "x"）
        response_format: 输出格式选择（Markdown 或 JSON）
    """
    model_config = ConfigDict(
        str_strip_whitespace=True,    # 自动去除字符串首尾空白
        validate_assignment=True,     # 启用赋值验证
        extra='forbid'                # 禁止额外字段
    )

    expression: str = Field(
        ...,
        description="数学表达式或方程。支持基础运算（+、-、*、/、**）、数学函数（sin、cos、log等）、"
                    "统计计算（mean、stdev等）、线性方程（2x+3=7）和批量计算（用分号分隔）",
        min_length=1,
        max_length=1000,
        examples=[
            "2 + 3 * 4",
            "sin(pi/2)",
            "mean([1,2,3,4,5])",
            "2x + 3 = 7",
            "2+3; 4*5; 10/2"
        ]
    )
    variable: str = Field(
        default="x",
        description="线性方程中的变量名（仅在解方程时使用）",
        min_length=1,
        max_length=10,
        pattern=r'^[a-zA-Z_][a-zA-Z0-9_]*$'
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="输出格式：'markdown' 为人类可读格式，'json' 为机器可读格式"
    )

    @field_validator('expression')
    @classmethod
    def validate_expression(cls, v: str) -> str:
        """验证表达式字段的有效性。
        
        确保表达式不为空且不只包含空白字符。
        
        Args:
            v: 待验证的表达式字符串
            
        Returns:
            去除首尾空白后的表达式字符串
            
        Raises:
            ValueError: 当表达式为空或仅包含空白字符时抛出
        """
        if not v or not v.strip():
            raise ValueError("表达式不能为空")
        return v.strip()


# ========== 核心计算器类 ==========

class UnifiedCalculator:
    """统一数学计算器核心类。
    
    提供统一的数学计算接口，支持多种计算类型的自动识别与处理。
    使用 AST 解析确保表达式计算的安全性，防止代码注入攻击。
    
    主要功能：
        - 表达式类型自动检测
        - 基础数学表达式求值
        - 线性方程求解
        - 统计计算
        - 批量计算处理
    
    Attributes:
        safe_functions: 安全的数学函数白名单字典
        safe_constants: 安全的数学常数白名单字典
    """

    def __init__(self):
        """初始化计算器实例。
        
        设置安全的函数和常数白名单，用于表达式求值时的安全检查。
        """
        # 安全函数白名单
        self.safe_functions = {
            # 基础数学函数
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'log': math.log,
            'log10': math.log10,
            'sqrt': math.sqrt,
            'abs': abs,
            'round': round,
            'pow': pow,

            # 统计函数
            'mean': statistics.mean,
            'median': statistics.median,
            'mode': statistics.mode,
            'stdev': statistics.stdev,
            'variance': statistics.variance,

            # 聚合函数
            'min': min,
            'max': max,
            'sum': sum,
            'len': len,
        }

        # 安全常数白名单
        self.safe_constants = {
            'pi': math.pi,
            'e': math.e,
            'tau': math.tau,
        }

    def detect_expression_type(self, expression: str) -> str:
        """自动检测表达式类型。
        
        根据表达式的语法特征判断其类型，用于后续选择合适的计算方法。
        
        检测优先级：
            1. 线性方程（包含等号和变量）
            2. 批量计算（包含分号）
            3. 统计计算（包含统计函数调用）
            4. 数学表达式（默认类型）
        
        Args:
            expression: 待检测的表达式字符串
            
        Returns:
            表达式类型标识，可能的值：
                - "linear_equation": 线性方程
                - "batch_calculation": 批量计算
                - "statistics": 统计计算
                - "expression": 数学表达式
        """
        expression = expression.strip()

        # 检查是否为线性方程（包含等号和变量）
        if '=' in expression and re.search(r'[a-zA-Z]\w*', expression):
            return "linear_equation"

        # 检查是否为批量计算（包含分号）
        if ';' in expression:
            return "batch_calculation"

        # 检查是否为统计函数
        stat_functions = ['mean(', 'median(', 'mode(', 'stdev(', 'variance(']
        if any(func in expression for func in stat_functions):
            return "statistics"

        # 默认为表达式计算
        return "expression"

    def evaluate_expression(self, expression: str) -> UnifiedCalculationResult:
        """求值数学表达式。
        
        使用 AST（抽象语法树）安全地解析和计算数学表达式，
        防止代码注入攻击。支持基础运算符和白名单内的数学函数。
        
        Args:
            expression: 数学表达式字符串
            
        Returns:
            包含计算结果的 UnifiedCalculationResult 对象
            
        Note:
            表达式中的统计函数会被自动重定向到 calculate_statistics 方法处理
        """
        # 检查是否包含统计函数
        stat_functions = ['mean', 'median', 'mode', 'stdev', 'variance']
        for func in stat_functions:
            if f"{func}(" in expression:
                return self.calculate_statistics(expression)

        # 使用 AST 解析安全地评估表达式
        try:
            node = ast.parse(expression, mode='eval')
            result = self._eval_node(node.body)

            return UnifiedCalculationResult(
                operation="expression",
                expression=expression,
                result=result,
                timestamp=datetime.now().isoformat(),
                steps=[
                    f"计算表达式: {expression}",
                    f"结果: {result}"
                ]
            )
        except Exception as e:
            return UnifiedCalculationResult(
                operation="error",
                expression=expression,
                result=float('nan'),
                timestamp=datetime.now().isoformat(),
                error=str(e)
            )

    def solve_linear_equation(self, equation: str, variable: str) -> UnifiedCalculationResult:
        """求解一元线性方程。
        
        解析并求解形如 ax + b = c 的一元线性方程。
        支持标准形式和各种变形，自动提取系数并求解。
        
        Args:
            equation: 线性方程字符串，必须包含一个等号
            variable: 方程中的未知变量名
            
        Returns:
            包含方程解的 UnifiedCalculationResult 对象，
            包括求解步骤的详细说明
            
        Note:
            方程必须是线性的（变量最高次数为1），否则可能产生错误结果
        """
        try:
            # 解析方程的左右两侧
            eq_parts = equation.split('=')
            if len(eq_parts) != 2:
                raise ValueError("方程必须包含一个等号")

            left_side = eq_parts[0].strip()
            right_side = eq_parts[1].strip()

            # 解析右侧的值
            right_value = self._evaluate_simple_expression(right_side)

            # 解析左侧的线性表达式（形式：ax + b）
            coeff = 0      # 变量的系数
            constant = 0   # 常数项

            # 移除空格以便解析
            left_side = left_side.replace(' ', '')

            # 使用正则表达式解析左侧表达式
            pattern = f'([+-]?\\d*\\.?\\d*)\\s*{re.escape(variable)}|([+-]\\d+\\.?\\d*)'
            matches = re.findall(pattern, left_side)

            # 提取系数和常数项
            for match in matches:
                coeff_match, const_match = match
                if coeff_match and coeff_match != '':
                    # 这是变量项
                    if coeff_match == '+' or coeff_match == '':
                        coeff += 1
                    elif coeff_match == '-':
                        coeff -= 1
                    else:
                        coeff += float(coeff_match)
                elif const_match:
                    # 这是常数项
                    constant += float(const_match)

            # 如果第一种方法未找到变量项，尝试备用解析
            if coeff == 0 and variable in left_side:
                parts = re.split(r'([+-])', left_side)
                for i in range(len(parts)):
                    part = parts[i]
                    if variable in part:
                        # 提取系数
                        coeff_str = part.replace(variable, '').replace('*', '')
                        if coeff_str == '' or coeff_str == '+':
                            coeff = 1
                        elif coeff_str == '-':
                            coeff = -1
                        else:
                            coeff = float(coeff_str)
                    elif part and part not in '+-' and i > 0 and parts[i-1] in '+-':
                        # 这是常数项
                        sign = -1 if parts[i-1] == '-' else 1
                        constant += sign * float(part)

            # 验证方程有效性
            if coeff == 0:
                raise ValueError(f"方程中必须包含变量 {variable} 或其系数为零")

            # 求解方程：ax + b = c => x = (c - b) / a
            solution = (right_value - constant) / coeff

            return UnifiedCalculationResult(
                operation="linear_equation",
                expression=equation,
                result=solution,
                timestamp=datetime.now().isoformat(),
                steps=[
                    f"原始方程: {equation}",
                    f"解析: {coeff}{variable} + {constant} = {right_value}",
                    f"移项: {coeff}{variable} = {right_value} - {constant}",
                    f"求解: {variable} = {solution}"
                ]
            )
        except Exception as e:
            return UnifiedCalculationResult(
                operation="error",
                expression=equation,
                result=float('nan'),
                timestamp=datetime.now().isoformat(),
                error=f"解方程失败: {str(e)}"
            )

    def calculate_statistics(self, expression: str) -> UnifiedCalculationResult:
        """执行统计计算。
        
        解析并计算统计函数调用，支持常用统计指标。
        输入格式为：function([data_list])
        
        Args:
            expression: 统计函数调用字符串，
                       格式示例：mean([1,2,3,4,5])
            
        Returns:
            包含统计结果的 UnifiedCalculationResult 对象
            
        Supported Functions:
            - mean: 算术平均值
            - median: 中位数
            - mode: 众数
            - stdev: 标准差（样本标准差）
            - variance: 方差（样本方差）
        """
        try:
            # 解析统计函数调用格式：function([data_list])
            match = re.match(r'(\w+)\(\[(.*?)\]\)', expression)
            if match:
                func_name = match.group(1)
                data_str = match.group(2)

                # 解析数据列表
                data = [float(x.strip()) for x in data_str.split(',') if x.strip()]

                # 执行对应的统计计算
                if func_name == 'mean':
                    result = statistics.mean(data)
                elif func_name == 'median':
                    result = statistics.median(data)
                elif func_name == 'mode':
                    result = statistics.mode(data)
                elif func_name == 'stdev':
                    result = statistics.stdev(data) if len(data) > 1 else 0
                elif func_name == 'variance':
                    result = statistics.variance(data) if len(data) > 1 else 0
                else:
                    raise ValueError(f"不支持的统计函数: {func_name}")

                return UnifiedCalculationResult(
                    operation="statistics",
                    expression=expression,
                    result=result,
                    timestamp=datetime.now().isoformat(),
                    data=data,
                    steps=[
                        f"统计函数: {func_name}",
                        f"数据: {data}",
                        f"结果: {result}"
                    ]
                )
            else:
                raise ValueError("统计函数格式不正确，应为: function([1,2,3])")
        except Exception as e:
            return UnifiedCalculationResult(
                operation="error",
                expression=expression,
                result=float('nan'),
                timestamp=datetime.now().isoformat(),
                error=f"统计计算失败: {str(e)}"
            )

    def process_batch(self, expressions: str) -> UnifiedCalculationResult:
        """处理批量计算请求。
        
        将多个表达式同时处理，表达式之间用分号分隔。
        每个表达式独立计算，支持混合不同类型的表达式。
        
        Args:
            expressions: 分号分隔的多个表达式字符串
            
        Returns:
            包含所有计算结果的 UnifiedCalculationResult 对象，
            result 字段为结果列表，batch_results 包含详细信息
        """
        try:
            # 分割表达式，移除空行
            expr_list = [expr.strip() for expr in expressions.split(';') if expr.strip()]

            batch_results = []
            # 递归处理每个表达式
            for expr in expr_list:
                expr_type = self.detect_expression_type(expr)
                if expr_type == "linear_equation":
                    result = self.solve_linear_equation(expr, "x")
                elif expr_type == "statistics":
                    result = self.calculate_statistics(expr)
                else:
                    result = self.evaluate_expression(expr)
                batch_results.append(result)

            # 提取所有成功计算的结果值
            results_values = [r.result for r in batch_results if r.operation != "error"]

            return UnifiedCalculationResult(
                operation="batch_calculation",
                expression=expressions,
                result=results_values,
                timestamp=datetime.now().isoformat(),
                batch_results=batch_results,
                steps=[
                    f"批量处理 {len(expr_list)} 个表达式",
                    *[f"  {i+1}. {r.expression} = {r.result}" for i, r in enumerate(batch_results)]
                ]
            )
        except Exception as e:
            return UnifiedCalculationResult(
                operation="error",
                expression=expressions,
                result=[],
                timestamp=datetime.now().isoformat(),
                error=f"批量计算失败: {str(e)}"
            )

    def _eval_node(self, node):
        """递归评估 AST 节点。
        
        安全地评估抽象语法树节点，仅支持白名单内的运算符和函数。
        用于防止恶意代码注入和不安全的表达式执行。
        
        Args:
            node: AST 节点对象
            
        Returns:
            节点的计算结果（float 类型）
            
        Raises:
            ValueError: 当遇到不支持的节点类型、运算符或函数时
            
        Supported Node Types:
            - Constant/Num: 数值常量
            - BinOp: 二元运算（+、-、*、/、**、//、%）
            - UnaryOp: 一元运算（+、-）
            - Call: 函数调用（仅白名单函数）
            - Name: 变量引用（仅白名单常数）
        """
        # 处理常量节点（Python 3.8+）
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return float(node.value)
            else:
                raise ValueError(f"不支持的常量类型: {type(node.value)}")
        
        # 兼容旧版本 Python（< 3.8）
        elif hasattr(ast, 'Num') and isinstance(node, ast.Num):
            return float(node.n)
        
        # 处理二元运算符
        elif isinstance(node, ast.BinOp):
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)

            if isinstance(node.op, ast.Add):
                return left + right
            elif isinstance(node.op, ast.Sub):
                return left - right
            elif isinstance(node.op, ast.Mult):
                return left * right
            elif isinstance(node.op, ast.Div):
                if right == 0:
                    raise ValueError("除数不能为零")
                return left / right
            elif isinstance(node.op, ast.Pow):
                return left ** right
            elif isinstance(node.op, ast.FloorDiv):
                if right == 0:
                    raise ValueError("除数不能为零")
                return left // right
            elif isinstance(node.op, ast.Mod):
                if right == 0:
                    raise ValueError("除数不能为零")
                return left % right
            else:
                raise ValueError(f"不支持的运算符: {type(node.op)}")
        
        # 处理一元运算符
        elif isinstance(node, ast.UnaryOp):
            operand = self._eval_node(node.operand)
            if isinstance(node.op, ast.UAdd):
                return +operand
            elif isinstance(node.op, ast.USub):
                return -operand
            else:
                raise ValueError(f"不支持的一元运算符: {type(node.op)}")
        
        # 处理函数调用
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
                if func_name in self.safe_functions:
                    args = [self._eval_node(arg) for arg in node.args]
                    return self.safe_functions[func_name](*args)
                else:
                    raise ValueError(f"不支持的函数: {func_name}")
            else:
                raise ValueError("不支持的函数调用形式")
        
        # 处理变量引用（仅允许白名单常数）
        elif isinstance(node, ast.Name):
            if node.id in self.safe_constants:
                return self.safe_constants[node.id]
            else:
                raise ValueError(f"不支持的变量或常数: {node.id}")
        
        # 不支持的节点类型
        else:
            raise ValueError(f"不支持的AST节点类型: {type(node)}")

    def _evaluate_simple_expression(self, expr: str) -> float:
        """评估简单的数学表达式。
        
        用于方程求解时计算等号右侧的简单表达式。
        支持基本运算和部分数学常数。
        
        Args:
            expr: 简单的数学表达式字符串
            
        Returns:
            表达式的计算结果（float 类型）
            
        Note:
            此方法使用受限的 eval，仅允许白名单内的名称和函数
        """
        try:
            # 处理空表达式
            if not expr or expr.strip() == '':
                return 0.0

            # 替换数学常数
            expr = expr.replace('pi', str(math.pi))
            expr = expr.replace('e', str(math.e))

            # 限制 eval 的命名空间，仅允许安全的函数和常数
            allowed_names = {
                'pi': math.pi,
                'e': math.e,
                'sqrt': math.sqrt,
                'abs': abs,
                'pow': pow,
            }

            # 执行受限的 eval
            result = eval(expr, {"__builtins__": {}}, allowed_names)
            return float(result)
        except:
            # 解析失败时尝试直接转换为数字
            try:
                return float(expr)
            except:
                return 0.0


# ========== MCP 工具定义 ==========

@mcp.tool(
    name="calculate",
    annotations={
        "title": "统一数学计算器",
        "readOnlyHint": True,         # 计算操作不修改系统状态
        "destructiveHint": False,     # 非破坏性操作
        "idempotentHint": True,       # 幂等操作，相同输入产生相同输出
        "openWorldHint": False        # 不与外部实体交互
    }
)
def calculate(
    expression: str,
    variable: str = "x",
    response_format: ResponseFormat = ResponseFormat.MARKDOWN
) -> str:
    """
    统一的数学计算工具：
    
    支持多种类型的数学运算，自动识别表达式类型并执行相应计算。
    
    核心功能：
        - 基础算术运算：支持 +、-、*、/、**、//、% 运算符
        - 数学函数：三角函数、对数、平方根等常用数学函数
        - 统计计算：均值、中位数、标准差、方差等统计指标
        - 线性方程求解：一元一次方程的自动求解
        - 批量计算：多个表达式的并行处理
    
    支持的运算符：
        +    加法
        -    减法
        *    乘法
        /    除法
        **   幂运算
        //   整除
        %    取模
    
    支持的函数：
        sin, cos, tan      三角函数
        log, log10         对数函数
        sqrt               平方根
        abs                绝对值
        round              四舍五入
        min, max, sum      聚合函数
        mean, median       统计函数
        mode, stdev        统计函数
        variance           方差
    
    支持的常数：
        pi      圆周率 (π)
        e       欧拉数
        tau     2π
    
    Args:
        expression: 数学表达式、方程或批量计算字符串。
            支持的格式：
                - 基础运算: "2 + 3 * 4", "(10 + 5) / 3", "2**3"
                - 数学函数: "sin(pi/2)", "log(100)", "sqrt(16) + abs(-5)"
                - 统计计算: "mean([1,2,3,4,5])", "stdev([1,2,3,4,5])"
                - 线性方程: "2x + 3 = 7", "3*y - 5 = 10"
                - 批量计算: "2+3; 4*5; 10/2", "sin(pi/2); cos(0); 2**3"
        
        variable: 线性方程中的变量名，默认为 "x"。
            仅在求解方程时使用，必须是有效的 Python 标识符。
        
        response_format: 输出格式选择。
            - ResponseFormat.MARKDOWN: 人类可读的格式化文本（默认）
            - ResponseFormat.JSON: 机器可读的结构化数据
    
    Returns:
        根据选择的格式返回计算结果：
        
        Markdown 格式：
            包含标题、表达式、结果、计算步骤和时间戳的格式化文本。
            
        JSON 格式：
            包含完整计算信息的结构化 JSON 字符串。
    
    Examples:
        基础计算：
            >>> calculate("2 + 3 * 4")
            返回包含结果 14.0 的 Markdown 格式文本
        
        方程求解：
            >>> calculate("2x + 3 = 7")
            返回包含 x = 2.0 求解过程的 Markdown 格式文本
        
        统计计算：
            >>> calculate("mean([1,2,3,4,5])")
            返回包含平均值 3.0 的 Markdown 格式文本
        
        批量计算：
            >>> calculate("2+3; 4*5; 10/2")
            返回包含批量结果 [5.0, 20.0, 5.0] 的 Markdown 格式文本
        
        JSON 输出：
            >>> calculate("sin(pi/2)", response_format=ResponseFormat.JSON)
            返回 JSON 格式的计算结果
    
    Note:
        - 幂运算使用 ** 运算符，不支持 ^
        - 统计函数的数据使用方括号：mean([1,2,3])
        - 批量计算使用分号分隔多个表达式
        - 方程必须包含等号，且变量默认为 x
        - 超长响应会被自动截断，截断阈值为 CHARACTER_LIMIT
    """
    # 验证输入参数
    try:
        validated_input = CalculateInput(
            expression=expression,
            variable=variable,
            response_format=response_format
        )
    except Exception as e:
        error_msg = f"输入验证失败: {str(e)}"
        if response_format == ResponseFormat.JSON:
            import json
            error_result = {
                "operation": "error",
                "expression": expression,
                "result": float('nan'),
                "timestamp": datetime.now().isoformat(),
                "error": error_msg
            }
            return json.dumps(error_result, indent=2, ensure_ascii=False)
        else:
            return f"❌ **错误**: {error_msg}"

    # 创建计算器实例并检测表达式类型
    calculator = UnifiedCalculator()
    expression_type = calculator.detect_expression_type(validated_input.expression)

    # 根据表达式类型执行相应计算
    try:
        if expression_type == "linear_equation":
            result = calculator.solve_linear_equation(
                validated_input.expression,
                validated_input.variable
            )
        elif expression_type == "batch_calculation":
            result = calculator.process_batch(validated_input.expression)
        elif expression_type == "statistics":
            result = calculator.calculate_statistics(validated_input.expression)
        else:
            result = calculator.evaluate_expression(validated_input.expression)

        # 根据输出格式生成响应
        if validated_input.response_format == ResponseFormat.JSON:
            import json
            # 构建 JSON 结果字典
            result_dict = {
                "operation": result.operation,
                "expression": result.expression,
                "result": result.result,
                "timestamp": result.timestamp,
                "steps": result.steps,
                "error": result.error
            }
            if result.data is not None:
                result_dict["data"] = result.data
            if result.batch_results is not None:
                result_dict["batch_results"] = [
                    {
                        "operation": br.operation,
                        "expression": br.expression,
                        "result": br.result
                    } for br in result.batch_results
                ]

            json_str = json.dumps(result_dict, indent=2, ensure_ascii=False)

            # 检查字符数限制
            if len(json_str) > CHARACTER_LIMIT:
                # 截断结果列表
                if isinstance(result_dict["result"], list):
                    result_dict["result"] = result_dict["result"][:len(result_dict["result"])//2]
                result_dict["truncated"] = True
                result_dict["truncation_message"] = (
                    f"响应因超过 {CHARACTER_LIMIT} 字符限制而被截断。"
                    "对于批量计算，请考虑减少表达式数量。"
                )
                json_str = json.dumps(result_dict, indent=2, ensure_ascii=False)

            return json_str

        else:
            # Markdown 格式输出
            if result.error:
                return (
                    f"❌ **计算错误**\n\n"
                    f"**表达式**: `{result.expression}`\n"
                    f"**错误**: {result.error}"
                )

            # 构建 Markdown 格式的成功结果
            lines = [f"# 🧮 计算结果", ""]
            lines.append(f"**表达式**: `{result.expression}`")
            lines.append(f"**操作类型**: {result.operation}")

            # 根据操作类型显示不同的结果格式
            if result.operation == "batch_calculation" and isinstance(result.result, list):
                lines.append("")
                lines.append("## 批量计算结果")
                lines.append("")
                for i, val in enumerate(result.result, 1):
                    lines.append(f"{i}. `{result.batch_results[i-1].expression}` = **{val}**")
            elif result.operation == "linear_equation":
                lines.append("")
                lines.append(f"## 方程求解结果")
                lines.append("")
                lines.append(f"**{validated_input.variable}** = **{result.result}**")
            else:
                lines.append("")
                lines.append(f"## 结果")
                lines.append("")
                lines.append(f"### {result.result}")

            # 显示计算步骤
            if result.steps:
                lines.append("")
                lines.append("## 计算步骤")
                lines.append("")
                for step in result.steps:
                    lines.append(f"- {step}")

            # 显示时间戳
            lines.append("")
            lines.append(f"---")
            lines.append(f"*计算时间: {result.timestamp}*")

            markdown_str = "\n".join(lines)

            # 检查字符数限制
            if len(markdown_str) > CHARACTER_LIMIT:
                # 截断内容
                lines = lines[:len(lines)//2]
                lines.append("")
                lines.append("⚠️ *响应因长度限制被截断*")
                markdown_str = "\n".join(lines)

            return markdown_str

    except Exception as e:
        error_msg = f"计算失败: {str(e)}"
        if validated_input.response_format == ResponseFormat.JSON:
            import json
            error_result = {
                "operation": "error",
                "expression": validated_input.expression,
                "result": float('nan'),
                "timestamp": datetime.now().isoformat(),
                "error": error_msg
            }
            return json.dumps(error_result, indent=2, ensure_ascii=False)
        else:
            return f"❌ **错误**: {error_msg}"


# ========== MCP 资源定义 ==========

@mcp.resource("calculator://constants")
def get_mathematical_constants() -> str:
    """获取常用数学常数列表。
    
    提供常用数学常数及其精确值，以 Markdown 格式呈现。
    
    Returns:
        Markdown 格式的数学常数列表，包含常数名称和对应的数值
    
    Constants Included:
        - π (Pi): 圆周率
        - e (Euler's Number): 欧拉数
        - φ (Golden Ratio): 黄金分割比
        - √2: 2的平方根
        - √3: 3的平方根
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
    """获取常用数学公式列表。
    
    提供常用的数学公式，包括几何、代数等领域，以 Markdown 格式呈现。
    
    Returns:
        Markdown 格式的数学公式列表
    
    Formulas Included:
        - 圆的面积公式
        - 三角形面积公式
        - 一元二次方程求根公式
        - 勾股定理
        - 平面距离公式
        - 直线斜率公式
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


# ========== MCP 提示定义 ==========

@mcp.prompt()
def math_problem_solver(problem: str) -> str:
    """生成数学问题的结构化解题方法提示。
    
    为给定的数学问题提供系统化的解题指导框架，
    帮助用户理解问题、选择方法、执行求解并验证结果。
    
    Args:
        problem: 待解决的数学问题描述
    
    Returns:
        包含结构化解题步骤的提示文本，指导用户完成问题求解
    
    Prompt Structure:
        1. 理解问题（目标、已知信息、约束条件）
        2. 识别方法（适用概念、相关公式、推荐方法）
        3. 逐步求解（清晰计算、推理说明、步骤验证）
        4. 最终答案（结果陈述、合理性检查、备选方法）
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
    
    为给定的数学计算提供验证和教育性解释，
    帮助用户理解计算过程、原理和可能的替代方法。
    
    Args:
        calculation: 待验证的数学计算表达式
    
    Returns:
        包含计算验证和解释的提示文本
    
    Prompt Content:
        1. 验证计算正确性
        2. 逐步分解计算过程
        3. 解释使用的数学原理
        4. 提供替代解法
        5. 指出常见错误
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


# ========== 主程序入口 ==========

def cli_main():
    """命令行界面主入口函数。
    
    启动 Calculator MCP Server，初始化 FastMCP 服务并开始监听请求。
    此函数作为命令行工具的入口点使用。
    
    Note:
        调用 mcp.run() 会启动服务器并阻塞当前线程，
        直到收到终止信号或发生错误。
    """
    print("Starting Calculator MCP Server with FastMCP...")
    mcp.run()


if __name__ == "__main__":
    cli_main()
