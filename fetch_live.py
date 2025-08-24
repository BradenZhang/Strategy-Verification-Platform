"""
实时从网上拉取指定股票/任意品种历史 K 线
返回 DataFrame（open/high/low/close/volume）
"""
import akshare as ak
import pandas as pd
from datetime import datetime, timedelta

def fetch_daily(symbol: str = "sh600519", days: int = 365) -> pd.DataFrame:
    """
    symbol:  sh600519 / sz000001 / usAAPL 等
    days:    往前多少天
    """
    end   = datetime.now().strftime("%Y%m%d")
    start = (datetime.now() - timedelta(days=days)).strftime("%Y%m%d")

    # A 股日线
    if symbol.startswith(("sh", "sz")):
        # 注意：akshare需要不带sh/sz前缀的股票代码
        code = symbol[2:]
        df = ak.stock_zh_a_hist(symbol=code, period="daily",
                                start_date=start, end_date=end, adjust="")
    # 美股日线
    elif symbol.startswith("us"):
        df = ak.stock_us_daily(symbol=symbol[2:], adjust="")
        df = df.loc[start:end]
    else:
        # 默认认为是A股代码，不带前缀
        df = ak.stock_zh_a_hist(symbol=symbol, period="daily",
                                start_date=start, end_date=end, adjust="")

    # 统一列名
    df.rename(columns={
        "日期": "date",
        "开盘": "open",
        "收盘": "close",
        "最高": "high",
        "最低": "low",
        "成交量": "volume"
    }, inplace=True)
    df["date"] = pd.to_datetime(df["date"])
    return df[["date", "open", "high", "low", "close", "volume"]]

if __name__ == "__main__":
    print(fetch_daily("sh600519", 30).head())