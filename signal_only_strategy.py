"""
只输出买卖时机，不真正下单
"""
from nautilus_trader.trading.strategy import Strategy
from nautilus_trader.model.data import Bar, BarType
from nautilus_trader.model.identifiers import InstrumentId
from nautilus_trader.core.datetime import dt_to_unix_nanos
import pandas as pd
import datetime as dt

class SignalOnlyStrategy(Strategy):
    def __init__(self):
        super().__init__()
        # 例子：贵州茅台
        self.instrument_id = InstrumentId.from_str("600519.SSE")
        self.signals = []

    def on_start(self):
        # 订阅日线 K 线（也可换成 1m/5m）
        self.subscribe_bars(BarType.from_str(f"{self.instrument_id}-1-DAY-LAST-EXTERNAL"))

    def on_bar(self, bar: Bar):
        """
        示例：5 日 / 20 日均线交叉
        请在此处替换为你自己的 AI 模型或任何规则
        """
        bars = self.cache.bars(BarType.from_str(f"{self.instrument_id}-1-DAY-LAST-EXTERNAL"))[-20:]
        if len(bars) < 20:
            return

        ma5  = sum(b.close for b in bars[-5:])  / 5
        ma20 = sum(b.close for b in bars[-20:]) / 20

        if ma5 > ma20:
            action = "BUY"
        elif ma5 < ma20:
            action = "SELL"
        else:
            return

        # 记录信号
        self.signals.append({
            "ts"     : bar.ts_event,
            "dt"     : str(dt.datetime.utcfromtimestamp(bar.ts_event / 1e9)),
            "symbol" : str(self.instrument_id),
            "price"  : float(bar.close),
            "action" : action,
        })

    def on_stop(self):
        # 程序结束时保存 CSV
        df = pd.DataFrame(self.signals)
        df.to_csv("signals.csv", index=False)
        self.log.info("信号已保存到 signals.csv")
