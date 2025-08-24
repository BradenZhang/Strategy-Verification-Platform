#!/usr/bin/env python3
"""
从网上抓 → 内存 DataFrame → 回放成 Bar
策略仅输出信号
"""
import pandas as pd
from datetime import datetime
from nautilus_trader.backtest.engine import BacktestEngine
from nautilus_trader.model.enums import AccountType, OmsType
from nautilus_trader.model.identifiers import Venue, InstrumentId, Symbol
from nautilus_trader.model.data import Bar, BarType
from nautilus_trader.model.objects import Price, Quantity, Money
from nautilus_trader.model.instruments import Equity
from nautilus_trader.model.currencies import CNY
from fetch_live import fetch_daily
from signal_only_strategy import SignalOnlyStrategy   # 同上一节的策略

# 1) 抓数据
df = fetch_daily("sh600519", 500)      # 最近 500 天
print("共抓到", len(df), "根 K 线")

# 2) 构造虚拟 instrument
symbol = Symbol("600519")
venue  = Venue("SSE")
instrument = Equity(
    instrument_id=InstrumentId(symbol, venue),
    raw_symbol=symbol,
    currency=CNY,
    price_precision=2,
    price_increment=Price.from_str("0.01"),
    lot_size=Quantity.from_int(1),
    isin="CNE000000519",
    ts_event=0,
    ts_init=0,
)

# 3) 构造 Bar 对象
bars = []
for _, r in df.iterrows():
    bar = Bar(
        bar_type=BarType.from_str(f"{instrument.id}-1-DAY-LAST-EXTERNAL"),
        open=Price(r["open"], precision=2),
        high=Price(r["high"], precision=2),
        low=Price(r["low"], precision=2),
        close=Price(r["close"], precision=2),
        volume=Quantity(r["volume"], precision=0),
        ts_event=pd.Timestamp(r["date"]).value,
        ts_init=pd.Timestamp(r["date"]).value,
    )
    bars.append(bar)

# 4) 回测引擎（无撮合，仅回放）
engine = BacktestEngine()
engine.add_venue(
    venue=venue,
    oms_type=OmsType.NETTING,
    account_type=AccountType.CASH,
    base_currency=CNY,
    starting_balances=[Money(1_000_000, CNY)],
)
engine.add_instrument(instrument)
engine.add_data(bars)

# 5) 添加策略
strategy = SignalOnlyStrategy()
engine.add_strategy(strategy)

# 6) 运行
engine.run()

# 7) 查看结果
print("最新 5 条信号：")
print(pd.DataFrame(strategy.signals).tail())