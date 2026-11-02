"""Every chart in the project, drawn with bezel-charts (https://pypi.org/project/bezel-charts/).

Each function takes the tidy table and returns a chart, which shows up in a notebook and saves as an SVG.
"""

from __future__ import annotations

import pandas as pd

import bezel_charts as bc

try:
    from . import analysis as an
except ImportError:
    import analysis as an

WIDE = {"theme": "light", "width": 760}
TILE = {"theme": "light", "width": 270}
MONEY_BN = {"prefix": "$", "suffix": "bn", "decimals": 1}
AXIS_BN = {"prefix": "$", "suffix": "bn", "decimals": 0}

# The library's default order puts pink next to green, which look alike with red-green colour blindness.
# These orders from the same palette stay distinct.
THREE = ["#6E70F0", "#D99A0E", "#E2508C"]
FOUR = ["#6E70F0", "#E2508C", "#D99A0E", "#16A884"]


def _bn(values: pd.Series | pd.DataFrame) -> pd.Series | pd.DataFrame:
    """Millions to billions, with years as text so they read as labels."""
    out = values / 1000
    out.index = out.index.astype(str)
    return out


def comparable_trend(df: pd.DataFrame):
    total = _bn(an.panel(df).sum(axis=1))
    return bc.line(
        total,
        heading=f"{len(an.panel_countries(df))} comparable countries, 2015 prices. Peak ${total.max():.1f}bn in {total.idxmax()}",
        stat="none", zero=True, height=250, straight=True, notes={"2020": f"Low ${total['2020']:.1f}bn"},
        **AXIS_BN, **WIDE,
    )


def one_figure(df: pd.DataFrame):
    totals = _bn(df.groupby("year")[an.VALUE].sum())
    share = an.one_figure(df)["share_of_year"]
    return bc.bars(
        totals,
        heading=f"All reported inflows by year, $bn at 2015 prices. Germany is {share:.0%} of 2012",
        stat="none", height=230, show_values=True, decimals=0, **WIDE,
    )


def top_countries(df: pd.DataFrame):
    return bc.bars(
        an.lifetime_totals(df).head(10) / 1000,
        heading="Top 10 by net inflows, 2000 to 2023, 2015 prices, without Germany 2012",
        horizontal=True, stat="none", show_values=True, **MONEY_BN, **WIDE,
    )


def concentration(df: pd.DataFrame):
    received = an.lifetime_totals(df).clip(lower=0)
    parts = {
        "China": received["China"],
        "Indonesia": received["Indonesia"],
        "Next 8 countries": received.iloc[2:10].sum(),
        f"The other {len(received) - 10} countries": received.iloc[10:].sum(),
    }
    return bc.donut(
        {name: round(value / 1000, 1) for name, value in parts.items()},
        heading="Who received the money, 2000 to 2023, 2015 prices",
        center_label="Received", color=FOUR, prefix="$", suffix="bn", decimals=0, theme="light", width=560,
    )


def who_drove_it(df: pd.DataFrame):
    return bc.line(
        _bn(an.split_panel(df)),
        heading="The same comparable countries, split into three groups, 2015 prices",
        stat="none", height=260, straight=True, color=THREE, **AXIS_BN, **WIDE,
    )


def continents(df: pd.DataFrame):
    money = an.by_continent(df) / 1000
    counts = an.countries_per_continent(df)
    money.index = [f"{name} ({counts[name]} countries)" for name in money.index]
    return bc.bars(
        money,
        heading="Net inflows by continent, 2000 to 2023, 2015 prices, without Germany 2012",
        horizontal=True, stat="none", show_values=True, **MONEY_BN, **WIDE,
    )


def outflows(df: pd.DataFrame):
    share = an.outflow_share(df) * 100
    share.index = share.index.astype(str)
    return bc.bars(
        share.round(1),
        heading="Share of reporting countries where more money left than arrived",
        stat="none", suffix="%", decimals=0, height=210, show_values=True, **WIDE,
    )


def forecast(df: pd.DataFrame):
    table = _bn(an.backtest(an.panel(df).sum(axis=1)))
    return bc.line(
        table[["Actual", "Last year", "Linear trend"]],
        heading="Each year predicted from earlier years only, comparable countries, 2015 prices",
        stat="none", zero=True, height=250, straight=True, color=THREE, **AXIS_BN, **WIDE,
    )


# Headline tiles ------------------------------------------------------------------------------------

def tile_total(df: pd.DataFrame):
    return bc.spark(
        _bn(an.panel(df).sum(axis=1)), heading=f"{len(an.panel_countries(df))} countries, 2021", delta="none",
        straight=True, height=86, **MONEY_BN, **TILE,
    )


def tile_indonesia(df: pd.DataFrame):
    return bc.spark(
        an.panel(df)["Indonesia"], heading="Indonesia, 2021", delta="none", straight=True, height=86,
        prefix="$", suffix="m", decimals=0, **TILE,
    )


def tile_top_two(df: pd.DataFrame):
    share = an.concentration(an.lifetime_totals(df))["top_2"] * 100
    return bc.gauge(round(share), label="China and Indonesia", heading="Share of all money", suffix="%", **TILE)


ALL = {
    "comparable-trend": comparable_trend,
    "one-figure": one_figure,
    "top-countries": top_countries,
    "concentration": concentration,
    "who-drove-it": who_drove_it,
    "continents": continents,
    "outflows": outflows,
    "forecast": forecast,
    "tile-total": tile_total,
    "tile-indonesia": tile_indonesia,
    "tile-top-two": tile_top_two,
}
