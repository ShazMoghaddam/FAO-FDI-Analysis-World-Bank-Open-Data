"""Draw every chart and write the findings report.

Run from the repository root after data/prepare.py:

    python findings/build.py

Charts go into charts/ as SVG files. The report is written to findings/README.md, and the key findings in the
main README are rewritten between their marker comments. Every number is worked out from the data. Nothing in
them is typed in by hand.
"""

from __future__ import annotations

import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "findings"))

import analysis as an  # noqa: E402
import charts  # noqa: E402

CHARTS = ROOT / "charts"
REPORT = ROOT / "findings" / "README.md"
README = ROOT / "README.md"


def bn(millions: float, decimals: int = 1) -> str:
    """12345.6 -> '$12.3bn'; -500 -> '-$0.5bn'."""
    sign = "-" if millions < 0 else ""
    return f"{sign}${abs(millions) / 1000:.{decimals}f}bn"


def facts(df) -> dict:
    """Every number the writing uses, in one place."""
    table = an.panel(df)
    total = table.sum(axis=1)
    groups = an.split_panel(df)
    fall = an.share_of_fall(df)
    figure = an.one_figure(df)
    conc = an.concentration(an.lifetime_totals(df))
    top = an.lifetime_totals(df)
    cont = an.by_continent(df)
    counts = an.countries_per_continent(df)
    share = an.outflow_share(df)
    errors = an.backtest_errors(an.backtest(total))
    panel_share = an.panel_share_of_reported(df)
    coverage = an.coverage(df)
    old = an.first_version()
    peak_year, low_year = int(total.idxmax()), int(total.loc[total.idxmax():].idxmin())
    return {
        "n_panel": table.shape[1], "start": bn(total.loc[an.PANEL_START]), "peak": bn(total.max()), "peak_year": peak_year,
        "low": bn(total.loc[low_year]), "low_year": low_year, "last": bn(total.loc[an.PANEL_END]),
        "peak_multiple": total.max() / total.loc[an.PANEL_START], "drop": 1 - total.loc[low_year] / total.max(),
        "panel_min": panel_share.min(), "panel_max": panel_share.max(),
        "indo_peak": bn(groups["Indonesia"].max()), "indo_fall": fall["Indonesia"],
        "two_fall": fall["Indonesia"] + fall["China"],
        "indo_2020": f"-${abs(groups.loc[2020, 'Indonesia']):.0f}m", "china_2010": bn(groups.loc[2010, "China"]),
        "china_2019": bn(groups.loc[2019, "China"]), "else_2015": bn(groups.loc[2015, "Everyone else"]),
        "else_2020": bn(groups.loc[2020, "Everyone else"]), "else_2021": bn(groups.loc[2021, "Everyone else"]),
        "de_value": bn(figure["value"]), "de_share": figure["share_of_year"],
        "de_other": f"${figure['other_years_net']:.0f}m", "de_other_n": figure["other_years_count"],
        "top_2": conc["top_2"], "top_3": conc["top_3"], "top_10": conc["top_10"], "bottom": conc["bottom_half"],
        "n_countries": conc["countries"], "half": conc["countries"] // 2, "china": bn(top["China"]), "indo": bn(top["Indonesia"]),
        "third": top.index[2], "third_value": bn(top.iloc[2]),
        "asia": cont["Asia"] / cont.sum(), "americas": cont["Americas"] / cont.sum(), "africa": cont["Africa"] / cont.sum(),
        "n_africa": counts["Africa"],
        "out_year": int(share.idxmax()), "out_max": share.max(), "out_avg": share.mean(), "out_low_year": int(share.idxmin()),
        "out_low": share.min(), "ever_neg": an.ever_negative(df),
        "err_naive": bn(errors["Last year"]), "err_trend": bn(errors["Linear trend"]),
        "n_all": df["iso3"].nunique(), "y0": int(df["year"].min()), "y1": int(df["year"].max()),
        "cov_2021": coverage[2021], "cov_2022": coverage[2022], "cov_2023": coverage[2023],
        "old_total": bn(old["old_total"], 0), "correct_total": bn(old["correct_total"], 0),
        "old_2015": bn(old["old_2015"]), "correct_2015": bn(old["correct_2015"]),
        "france_r2": f"{old['france_r2']:.2f}", "france_rows": old["france_rows"],
    }


def key_findings(f: dict, prefix: str = "") -> str:
    """The short version for the main README."""
    return f"""### Investment surged, then fell back

Across the {f['n_panel']} countries that reported every year, yearly inflows grew from a low of **{f['start']}** in 2005 to
**{f['peak']}** in {f['peak_year']}, then dropped {f['drop']:.0%} to {f['low']} in {f['low_year']}.

![Inflows across comparable countries, peaking in {f['peak_year']}]({prefix}charts/comparable-trend.svg)

### One country explains most of the fall

Indonesia alone accounts for **{f['indo_fall']:.0%}** of the fall from {f['peak_year']} to {f['low_year']}. Everyone outside
Indonesia and China was back at {f['else_2021']} by 2021, level with {f['else_2015']} in {f['peak_year']}.

![Indonesia, China and everyone else over time]({prefix}charts/who-drove-it.svg)

### Two countries took {f['top_2']:.0%} of the money

China and Indonesia received **{f['top_2']:.0%}** of all money across {f['n_countries']} countries. The bottom {f['half']}
countries shared **{f['bottom']:.1%}**.

![Share of money received by China, Indonesia and the rest]({prefix}charts/concentration.svg)

### One number looks like a global boom

A single figure, Germany in 2012, is **{f['de_value']}**, or {f['de_share']:.0%} of everything reported that year.
Germany's other {f['de_other_n']} years add up to {f['de_other']}.

![All reported inflows by year, with 2012 towering over the rest]({prefix}charts/one-figure.svg)"""


def report(f: dict) -> str:
    return f"""# Findings

Where foreign money goes when it invests in farming, forestry and fishing, across {f['n_all']} countries from {f['y0']} to
{f['y1']}. This page is written by [`build.py`](build.py), so every number comes straight from the data.

All figures are in US dollars at constant 2015 prices, so inflation doesn't flatter later years. A negative number
means more money left a country than arrived.

## 1. Investment surged, then fell back

Yearly inflows grew from a low of {f['start']} in 2005 to {f['peak']} in {f['peak_year']}, about {f['peak_multiple']:.1f} times as much. By
{f['low_year']} they had dropped {f['drop']:.0%} to {f['low']}, then recovered to {f['last']} in 2021.

![Inflows across comparable countries](../charts/comparable-trend.svg)

This chart follows only the {f['n_panel']} countries with a figure for every year from 2005 to 2021, because the number of
countries reporting changes each year. Those {f['n_panel']} countries hold between {f['panel_min']:.0%} and {f['panel_max']:.0%} of all
money reported in any of those years, leaving out the German figure in finding 3.

## 2. One country explains most of the fall

Indonesia went from {f['indo_peak']} in {f['peak_year']} to {f['indo_2020']} in {f['low_year']}. That single change is {f['indo_fall']:.0%} of the whole
fall, and with China it reaches {f['two_fall']:.0%}. China itself slid gradually, from {f['china_2010']} in 2010 to {f['china_2019']} in 2019.

Everyone else tells a calmer story: {f['else_2015']} in {f['peak_year']}, {f['else_2020']} in {f['low_year']}, and {f['else_2021']} in 2021. A headline
about a global retreat from agricultural investment would be wrong. This is mostly two countries.

![Indonesia, China and everyone else](../charts/who-drove-it.svg)

## 3. One number looks like a global boom

Add up every country and 2012 towers over everything else. That spike is one figure: Germany at {f['de_value']}, which is
{f['de_share']:.0%} of the year. Germany's other {f['de_other_n']} years come to {f['de_other']} combined.

![All reported inflows by year](../charts/one-figure.svg)

The data doesn't say what happened, so the figure stays in the raw file and this chart, and is left out of the
rankings and shares in findings 4 and 5. Germany isn't in the comparable group either, because it has gaps.

## 4. Two countries took {f['top_2']:.0%} of the money

China received {f['china']} and Indonesia {f['indo']}. The top 3, with {f['third']} at {f['third_value']}, took {f['top_3']:.0%}, and the top 10
took {f['top_10']:.0%}. The bottom {f['half']} of {f['n_countries']} countries shared {f['bottom']:.1%}.

![Top 10 countries](../charts/top-countries.svg)

![Who received the money](../charts/concentration.svg)

Shares here count only money received. A country that lost money overall counts as zero rather than a negative share.

## 5. Asia dominates, and Africa barely registers

Asia accounts for {f['asia']:.0%} of net inflows and the Americas {f['americas']:.0%}. Africa accounts for {f['africa']:.0%}, though only
{f['n_africa']} African countries appear in this data, so treat that as a partial picture.

![Net inflows by continent](../charts/continents.svg)

## 6. Money leaves as well as arrives

{f['ever_neg']} of {f['n_all']} countries recorded a net outflow in at least one year. On average {f['out_avg']:.0%} of reporting countries saw
one in any year, ranging from {f['out_low']:.0%} in {f['out_low_year']} to {f['out_max']:.0%} in {f['out_year']}, the first year of the pandemic.

![Share of countries with a net outflow](../charts/outflows.svg)

## 7. Past values alone don't forecast this

Predicting each year from 2012 to 2021 using only the years before it, a straight trend line missed by {f['err_trend']} on
average. Simply repeating last year's figure missed by {f['err_naive']}. The trend line kept predicting high figures long after
the money had turned, and neither method saw 2020 coming.

![Actual inflows against both forecasts](../charts/forecast.svg)

With ten test years this is a small sample, so read it as a warning rather than a verdict. Forecasting these flows
would need outside information such as commodity prices and policy changes, which this dataset doesn't include.

## What this data can't tell you

- **It isn't truly global.** {f['n_all']} countries appear, and many report only some years. Coverage falls from {f['cov_2021']} countries in
  2021 to {f['cov_2022']} in 2022 and {f['cov_2023']} in 2023, so the apparent drop in those final years is largely missing data. The
  trend stops at 2021 for that reason.
- **It shows what, not why.** Nothing here explains Indonesia's fall or Germany's spike, and the timing of the 2020 low
  doesn't prove the pandemic caused it.
- **It counts recorded flows.** These are figures countries report, and methods vary between them.

## How it was worked out

1. [`data/prepare.py`](../data/prepare.py) reshapes the raw World Bank file into one row per country and year.
2. [`analysis.py`](analysis.py) holds every calculation as a small, tested function.
3. [`charts.py`](charts.py) draws each chart with [bezel-charts](https://pypi.org/project/bezel-charts/).
4. [`notebooks/fdi_analysis.ipynb`](../notebooks/fdi_analysis.ipynb) walks through the same steps with the working shown.

## A correction to the first version

The first version of this project added up the raw value column without noticing the file holds most country-years
twice, once in current dollars and once at 2015 prices. That made the {f['y0']} to {f['y1']} total {f['old_total']} instead of
{f['correct_total']}, and 2015 alone {f['old_2015']} instead of {f['correct_2015']}. Its France model trained on those mixed rows, using a random
split that let it learn from the future, and scored an R² of {f['france_r2']}. Everything here replaces that work.
"""


def replace_block(text: str, name: str, body: str) -> str:
    pattern = re.compile(rf"(<!-- {name}:start -->\n).*?(\n<!-- {name}:end -->)", re.S)
    if not pattern.search(text):
        raise ValueError(f"Marker {name} not found")
    return pattern.sub(lambda m: m.group(1) + body + m.group(2), text)


def main() -> None:
    df = an.load()
    # bezel-charts gives each gradient a random id so charts can share a page. A fixed seed keeps the
    # files identical between runs, so a rebuild only shows up in git when something really changed.
    random.seed(2026)
    CHARTS.mkdir(exist_ok=True)
    for name, draw in charts.ALL.items():
        draw(df).save(CHARTS / f"{name}.svg")

    f = facts(df)
    REPORT.write_text(report(f), encoding="utf-8")
    README.write_text(replace_block(README.read_text(encoding="utf-8"), "key-findings", key_findings(f)), encoding="utf-8")
    print(f"Wrote {len(charts.ALL)} charts, {REPORT.relative_to(ROOT)} and the README findings")


if __name__ == "__main__":
    main()
