import sqlite3
import pandas as pd
from typing import List, Dict, Optional
from config import DB_PATH

def build_where_clause(filters: Dict[str, str]) -> str:
    conditions = []
    for key, value in filters.items():
        if "日期范围" in key:
            # 简单解析 "2024-01-01到2024-01-31"
            parts = value.replace("到", ",").replace(" ", "").split(",")
            if len(parts) == 2:
                start, end = parts[0], parts[1]
                conditions.append(f"order_date BETWEEN '{start}' AND '{end}'")
        elif "商品类别" in key:
            conditions.append(f"product_category = '{value}'")
        elif "地区" in key:
            conditions.append(f"region = '{value}'")
        # 可根据需要扩展更多过滤字段
    if conditions:
        return "WHERE " + " AND ".join(conditions)
    return ""

def build_sql(metrics: List[str], dimensions: List[str], filters: Dict[str, str]) -> str:
    select_parts = []
    group_by = []
    # 维度处理
    for dim in dimensions:
        if dim == "日期":
            col = "order_date"
        elif dim == "商品类别":
            col = "product_category"
        elif dim == "地区":
            col = "region"
        else:
            continue
        select_parts.append(col)
        group_by.append(col)

    # 指标处理
    for m in metrics:
        if "订单量" in m or "订单数" in m:
            select_parts.append("COUNT(*) AS 订单量")
        elif "销售额" in m:
            select_parts.append("SUM(total_amount) AS 销售额")
        elif "平均单价" in m:
            select_parts.append("AVG(unit_price) AS 平均单价")
        # 可扩展

    sql = f"SELECT {', '.join(select_parts)} FROM orders {build_where_clause(filters)}"
    if group_by:
        sql += f" GROUP BY {', '.join(group_by)}"
    sql += " ORDER BY order_date" if "日期" in dimensions else ""
    return sql

def execute_query(metrics: List[str], dimensions: List[str], filters: Dict[str, str]) -> pd.DataFrame:
    sql = build_sql(metrics, dimensions, filters)
    print(f"执行SQL: {sql}")
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(sql, conn)
    conn.close()
    return df

def get_comparison_data(plan) -> tuple:
    """如果是comparison/attribution，返回两个DataFrame (curr_period, base_period)"""
    periods = plan.comparison_periods
    if not periods or len(periods) != 2:
        return None, None
    # 简单处理：将时间段描述转为实际日期
    # 这里简化使用最近一周等，建议在plan中让LLM给出具体日期范围
    # 此处假设用户问题中明确时间段，parser会给出具体日期
    # 如果parser只给出文字，需要额外的日期解析逻辑，这里为演示简化为直接使用filters中的日期。
    # 在实际项目中，应要求LLM返回具体日期范围。
    return None, None  # 省略细节，本示例通过修改filters两次查询实现