# 自动化数据报表与归因分析 Agent

用中文提问，自动出报告。输入「**为什么本周销售额下降了？**」，Agent 会解析意图、查询数据、做归因分析，最后输出一份带图表的 Markdown 报告——全程不用写 SQL。

---

## 效果

```
你：为什么本周销售额下降了？

Agent：
  本周销售额 128,450，较上周 156,200 下降 17.8%
  按商品类别拆解贡献：
    电子产品    -21,300  (-13.6%)   ← 主因
    服装        -5,100   (-3.3%)
    家居        +  650  (+0.4%)
  结论：下降主要由电子产品类别导致，集中在华东地区。
  [附柱状图]
```

---

## 整体流程

```
用户提问（中文自然语言）
        ↓
  ① 意图解析：LLM 结构化输出 → QueryPlan
        ↓
  ② 语义映射：中文指标/维度 → 物理列 + 聚合函数
        ↓
  ③ 数据查询：参数化 SQL 查 SQLite
        ↓
  ④ 归因分析：基期/当期对比，按维度拆解贡献度
        ↓
  ⑤ 报告生成：Markdown + Matplotlib 图表
```

---

## 关键设计

### 1. JSON Mode + Pydantic 双重校验

大模型的输出不能直接信，所以做了两层约束：

```python
response = client.chat.completions.create(
    model=MODEL_NAME,
    messages=[{"role": "user", "content": prompt}],
    response_format={"type": "json_object"},   # 第一层：强制 JSON 模式
    temperature=0,                              # 降低随机性
)
result = json.loads(response.choices[0].message.content)
return QueryPlan(**result)                      # 第二层：Pydantic 字段/类型校验
```

`QueryPlan` 定义了 `metrics` / `dimensions` / `filters` / `analysis_type` / `comparison_periods` 五个字段，模型少给一个字段或类型不对，直接抛异常，不会带着脏数据往下走。

### 2. 语义映射层（防幻觉 + 防注入）

**模型不直接生成 SQL。** 这是这套设计的核心取舍：

```python
METRIC_MAP = {
    "销售额":  ("SUM",  "total_amount"),
    "订单量":  ("COUNT", "order_id"),
    "平均单价": ("AVG",  "unit_price"),
}

DIMENSION_MAP = {
    "日期":    "order_date",
    "商品类别": "product_category",
    "地区":    "region",
}
```

模型只输出 `["销售额"]`、`["商品类别"]` 这样的**白名单内的中文名词**，由代码映射成 `SUM(total_amount)`、`GROUP BY product_category`。

好处是双重的：

- **防幻觉**：模型编不出 `SUM(nonexistent_column)`
- **防注入**：中文名词已经在白名单里，不存在拼接任意 SQL 的可能

### 3. 贡献度分解归因算法

回答「为什么下降」靠的不是让模型编，而是真算：

```python
贡献度 = 该维度当期值 - 该维度基期值
贡献占比 = 贡献度 / 总体变化量
```

按贡献度降序排列，一眼看出是哪个类别、哪个地区拖下来的。再用 Matplotlib 按正负变化着色出图——涨的绿、跌的红。

### 4. 配置与降级

- API Key 走 `.env`，`.env.example` 给出模板，真实配置不入库
- 兼容 OpenAI 接口格式的任意服务（DeepSeek、通义、本地 Ollama 都能接，改 `BASE_URL` 即可）

---

## 项目结构

```
.
├── agent.py              # 主入口，串联完整流程
├── nl_parser.py          # 自然语言 → QueryPlan（LLM 结构化输出）
├── data_query.py         # QueryPlan → 参数化 SQL → DataFrame
├── attribution.py        # 贡献度分解归因算法
├── report_generator.py   # Markdown 报告 + Matplotlib 图表
├── database.py           # SQLite 连接与初始化
├── config.py             # 环境变量与模型配置
├── requirements.txt
└── .env.example
```

---

## 快速开始

```bash
git clone https://github.com/yxcc-cc/agent.git
cd agent

pip install -r requirements.txt

cp .env.example .env
# 编辑 .env，填入 API_KEY / BASE_URL / MODEL_NAME

python database.py    # 初始化示例数据库
python agent.py       # 开始提问
```

### `.env` 配置

```ini
API_KEY=your_api_key_here
BASE_URL=https://api.deepseek.com
MODEL_NAME=deepseek-chat
```

> 任何兼容 OpenAI Chat Completions 接口的服务都可以，改 `BASE_URL` 和 `MODEL_NAME` 即可。

---

## 技术栈

| 用途 | 技术 |
| --- | --- |
| 大模型调用 | OpenAI Python SDK（兼容任意 OpenAI 协议服务） |
| 结构化输出 | JSON Mode + Pydantic 数据模型校验 |
| 数据处理 | Pandas、SQLite |
| 可视化 | Matplotlib |
| 配置管理 | python-dotenv |
