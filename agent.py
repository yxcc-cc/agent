from nl_parser import parse_to_query_plan, QueryPlan
from data_query import execute_query
from attribution import attribution_analysis
from report_generator import generate_report
import pandas as pd

class DataAgent:
    def __init__(self):
        pass

    def process(self, question: str):
        print(f"📥 收到问题：{question}")
        # 1. 解析查询计划
        plan = parse_to_query_plan(question)
        print(f"📋 查询计划：{plan.model_dump()}")

        # 2. 根据分析类型执行查询
        if plan.analysis_type == "trend":
            df = execute_query(plan.metrics, plan.dimensions, plan.filters)
            data_frames = {'main': df}
        elif plan.analysis_type in ("comparison", "attribution"):
            # 需要两个时段的对比，简化处理：在filters中要求两个时段的日期，这里假设问题为“上周vs本周”，
            # 实际项目中需要从plan.comparison_periods解析日期。这里用一个简化方法：让LLM生成具体日期范围。
            # 为了演示，我们可以硬编码两个查询，或修改parser让filters直接包含两个日期的分别查询。
            # 这里展示核心归因逻辑，先用整体趋势查询然后自行拆分。
            # 更好的做法：在plan中包含两个filter集合。此处为代码完整性，我们假设问题中给出了具体日期，通过两次查询。
            # 简化：取当前filter中的日期范围，然后划分为两半。不推荐，但为了演示。
            if plan.comparison_periods and len(plan.comparison_periods) == 2:
                # 假设parser已经将日期范围拆分放入两个filters，这里未实现，我们跳过直接模拟。
                print("归因分析需要明确两个时间段的过滤条件，请查看后续版本。")
                return
            else:
                # 临时模拟：使用全部数据，对比最近两个月
                # 从数据库获取整体维度数据，然后根据日期列手动拆分
                all_df = execute_query(plan.metrics, plan.dimensions, plan.filters)
                # 假设有order_date列，拆分为最近一个月和前一个月
                all_df['order_date'] = pd.to_datetime(all_df['order_date'])
                latest_date = all_df['order_date'].max()
                curr_df = all_df[all_df['order_date'] >= latest_date - pd.DateOffset(months=1)]
                base_df = all_df[(all_df['order_date'] >= latest_date - pd.DateOffset(months=2)) &
                                 (all_df['order_date'] < latest_date - pd.DateOffset(months=1))]
                if curr_df.empty or base_df.empty:
                    print("数据不足，无法对比")
                    return
                # 按维度聚合（如果dimensions不含日期，则直接按剩余维度聚合）
                agg_dim = [d for d in plan.dimensions if d != "日期"]
                if not agg_dim:
                    agg_dim = ['product_category']  # 默认按类别
                # 选择指标：取第一个非日期指标
                metric = "销售额" if "销售额" in plan.metrics else plan.metrics[0]
                curr_agg = curr_df.groupby(agg_dim).agg({metric: 'sum'}).reset_index()
                base_agg = base_df.groupby(agg_dim).agg({metric: 'sum'}).reset_index()
                attr_df = attribution_analysis(curr_agg, base_agg, agg_dim[0], metric)
                data_frames = {'curr': curr_agg, 'base': base_agg, 'attribution': attr_df}
        else:
            print("不支持的分析类型")
            return

        # 3. 生成报告
        plan.question = question  # 动态添加属性
        report = generate_report(plan, data_frames)
        print("\n" + report)
        print("图表已保存为 trend_chart.png / attribution_chart.png")

def main():
    from database import generate_data
    generate_data("ecommerce.db", num_records=3000)
    agent = DataAgent()
    print("====== 自动化数据报表与归因分析 Agent ======")
    print("示例问题：")
    print("1. 过去一周的销售额趋势如何？")
    print("2. 为什么上个月销售额下降了？（归因分析）")
    question = input("请输入你的数据分析问题：")
    agent.process(question)

if __name__ == "__main__":
    main()