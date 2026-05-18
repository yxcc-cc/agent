import pandas as pd

def attribution_analysis(curr_df: pd.DataFrame, base_df: pd.DataFrame, 
                         dimension_col: str, metric_col: str) -> pd.DataFrame:
    """
    计算每个维度值对指标总变化的贡献度。
    curr_df: 当前期数据（按维度聚合）
    base_df: 基期数据（按维度聚合）
    dimension_col: 维度列名
    metric_col: 指标列名
    返回DataFrame包含：维度值、变化量、贡献度(%)
    """
    # 合并两个时段数据
    merged = pd.merge(base_df[[dimension_col, metric_col]], 
                      curr_df[[dimension_col, metric_col]], 
                      on=dimension_col, how='outer', suffixes=('_base', '_curr'))
    merged.fillna(0, inplace=True)
    merged['变化量'] = merged[f'{metric_col}_curr'] - merged[f'{metric_col}_base']
    total_change = merged['变化量'].sum()
    if total_change == 0:
        merged['贡献度'] = 0
    else:
        merged['贡献度'] = (merged['变化量'] / total_change * 100).round(1)
    merged = merged[[dimension_col, f'{metric_col}_base', f'{metric_col}_curr', '变化量', '贡献度']]
    merged.columns = [dimension_col, '基期值', '当期值', '变化量', '贡献度(%)']
    return merged.sort_values('贡献度(%)', ascending=False)