import json
from openai import OpenAI
from pydantic import BaseModel
from typing import List, Optional, Dict
from config import API_KEY, BASE_URL, MODEL_NAME

class QueryPlan(BaseModel):
    metrics: List[str]
    dimensions: List[str]
    filters: Dict[str, str]
    analysis_type: str
    comparison_periods: Optional[List[str]] = None

def parse_to_query_plan(question: str) -> QueryPlan:
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
    
    db_schema = """
数据库为SQLite，包含一张订单表 orders，字段如下：
- order_id: 订单ID
- order_date: 订单日期 (格式 YYYY-MM-DD)
- product_category: 商品类别 (电子产品、服装、家居、食品、运动户外)
- region: 地区 (华东、华南、华北、西南、西北)
- quantity: 购买数量
- unit_price: 单价
- total_amount: 销售额

可用指标：订单量 (COUNT)，销售额 (SUM total_amount)，平均单价 (AVG unit_price)
可分析类型：
- "trend": 时间趋势分析
- "comparison": 两个时段的对比
- "attribution": 归因分析，回答“为什么某个指标变化”，需要对比两个时段并给出维度贡献
"""
    prompt = f"""
你是一个数据分析专家。根据用户自然语言问题，结合数据库Schema，输出一个JSON格式的查询计划。
查询计划包含以下字段（均为必填）：
- metrics: 指标列表，如 ["订单量", "销售额"]
- dimensions: 维度列表，如 ["日期", "商品类别", "地区"]
- filters: 过滤条件字典，如 {{"日期范围": "2024-01-01到2024-01-31"}}，若无过滤则为空字典
- analysis_type: 分析类型，从 "trend", "comparison", "attribution" 中选择
- comparison_periods: 若为comparison或attribution，提供两个时段的描述，如 ["前一周", "本周"]，否则为null

数据库Schema: {db_schema}

用户问题: {question}

请只输出严格符合上述结构的JSON，不要添加任何解释。
"""
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0
    )
    result = json.loads(response.choices[0].message.content)
    return QueryPlan(**result)