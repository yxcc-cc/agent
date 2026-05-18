import matplotlib
matplotlib.use('Agg')  # 非交互后端
import matplotlib.pyplot as plt
import pandas as pd
from typing import List

def generate_report(plan, data_frames: dict) -> str:
    """生成 Markdown 文本报告，并保存图表"""
    report_lines = []
    report_lines.append(f"# 分析报告\n")
    report_lines.append(f"## 问题：{getattr(plan, 'question', '用户问题')}\n")
    # 根据分析类型输出不同内容
    if plan.analysis_type == "trend":
        if 'main' in data_frames:
            df = data_frames['main']
            report_lines.append("## 趋势数据 (前10行)")
            report_lines.append(df.head(10).to_markdown(index=False))
            # 生成折线图
            plot_trend(df)
    elif plan.analysis_type in ("comparison", "attribution"):
        if 'curr' in data_frames and 'base' in data_frames:
            report_lines.append("### 基期 vs 当期 汇总")
            # 可以展示汇总值
        if 'attribution' in data_frames:
            attr_df = data_frames['attribution']
            report_lines.append("## 归因分析结果")
            report_lines.append(attr_df.to_markdown(index=False))
            plot_attribution(attr_df)

    report = "\n".join(report_lines)
    return report

def plot_trend(df_ts):
    """时间序列折线图"""
    if 'order_date' not in df_ts.columns:
        return
    plt.figure(figsize=(10, 4))
    # 假设有一列数值，自动选择
    num_cols = df_ts.select_dtypes(include='number').columns
    if len(num_cols) > 0:
        for col in num_cols[:2]:  # 最多两个指标
            plt.plot(df_ts['order_date'], df_ts[col], marker='o', label=col)
        plt.xticks(rotation=45)
        plt.legend()
        plt.tight_layout()
        plt.savefig("trend_chart.png")
        plt.close()

def plot_attribution(attr_df):
    """归因贡献度柱状图"""
    dim_col = attr_df.columns[0]
    plt.figure(figsize=(8, 5))
    colors = ['g' if x > 0 else 'r' for x in attr_df['变化量']]
    plt.bar(attr_df[dim_col], attr_df['变化量'], color=colors)
    plt.ylabel('变化量')
    plt.title(f'{dim_col} 维度的指标变化量')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("attribution_chart.png")
    plt.close()