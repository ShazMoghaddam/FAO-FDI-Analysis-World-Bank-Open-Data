"""The analysis behind every finding. Plain functions, no charts and no files written.

All money is in millions of US dollars at constant 2015 prices unless a function says otherwise, so a dollar in
2005 and a dollar in 2021 can be compared.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parent.parent
TIDY = ROOT / "data" / "fdi_inflows.csv"
RAW = ROOT / "data" / "raw" / "FAO_FDI.csv"

VALUE = "fdi_usd_m_2015"
OUTLIER = ("DEU", 2012)  # One figure larger than any country's whole annual total; see one_figure()
PANEL_START, PANEL_END = 2005, 2021
BACKTEST_START = 2012


def load() -> pd.DataFrame:
    """The tidy table, keeping only rows with a value at 2015 prices."""
    return pd.read_csv(TIDY).dropna(subset=[VALUE]).reset_index(drop=True)


def without_outlier(df: pd.DataFrame) -> pd.DataFrame:
    return df[~((df["iso3"] == OUTLIER[0]) & (df["year"] == OUTLIER[1]))]


# Coverage ---------------------------------------------------------------------------------------

def coverage(df: pd.DataFrame) -> pd.Series:
    """How many countries reported each year."""
    return df.groupby("year")["iso3"].nunique()


def panel_countries(df: pd.DataFrame, start: int = PANEL_START, end: int = PANEL_END) -> list[str]:
    """Countries with a figure for every year from start to end. Comparing only these stops changes
    in who reports from looking like changes in investment."""
    years = df[df["year"].between(start, end)].groupby("iso3")["year"].nunique()
    return sorted(years[years == end - start + 1].index)


def panel(df: pd.DataFrame, start: int = PANEL_START, end: int = PANEL_END) -> pd.DataFrame:
    """One row per year, one column per country, for the comparable countries only."""
    rows = df[df["iso3"].isin(panel_countries(df, start, end)) & df["year"].between(start, end)]
    return rows.pivot(index="year", columns="country", values=VALUE).sort_index()


def panel_share_of_reported(df: pd.DataFrame) -> pd.Series:
    """The panel's share of all money reported each year, leaving out the outlier."""
    reported = without_outlier(df).groupby("year")[VALUE].sum()
    return (panel(df).sum(axis=1) / reported).dropna()


# Finding 1 and 4: the boom and the fall ----------------------------------------------------------

def split_panel(df: pd.DataFrame) -> pd.DataFrame:
    """The panel total split into Indonesia, China and everyone else."""
    table = panel(df)
    others = table.drop(columns=["Indonesia", "China"]).sum(axis=1)
    return pd.DataFrame({"Indonesia": table["Indonesia"], "China": table["China"], "Everyone else": others})


def share_of_fall(df: pd.DataFrame, start: int = 2015, end: int = 2020) -> pd.Series:
    """Each group's share of the fall in the panel total between two years."""
    table = split_panel(df)
    change = table.loc[end] - table.loc[start]
    return change / change.sum()


# Finding 2: the single figure --------------------------------------------------------------------

def one_figure(df: pd.DataFrame) -> dict:
    """How much one German figure distorts the totals."""
    iso, year = OUTLIER
    country = df[df["iso3"] == iso].set_index("year")[VALUE]
    return {
        "value": country[year],
        "share_of_year": country[year] / df.loc[df["year"] == year, VALUE].sum(),
        "other_years_net": country.drop(year).sum(),
        "other_years_count": len(country) - 1,
        "other_years_max": country.drop(year).max(),
    }


# Finding 3 and 5: who gets the money -------------------------------------------------------------

def lifetime_totals(df: pd.DataFrame) -> pd.Series:
    """Net inflows per country across every reported year, leaving out the outlier, largest first."""
    return without_outlier(df).groupby("country")[VALUE].sum().sort_values(ascending=False)


def concentration(totals: pd.Series) -> dict:
    """Shares of all money received. Countries that lost money overall count as zero, not as a negative share."""
    received = totals.clip(lower=0).sort_values(ascending=False)
    whole = received.sum()
    return {
        "top_2": received.head(2).sum() / whole,
        "top_3": received.head(3).sum() / whole,
        "top_10": received.head(10).sum() / whole,
        "bottom_half": received.tail(len(received) // 2).sum() / whole,
        "countries": len(received),
    }


def by_continent(df: pd.DataFrame) -> pd.Series:
    """Net inflows per continent across every reported year, leaving out the outlier."""
    return without_outlier(df).groupby("continent")[VALUE].sum().sort_values(ascending=False)


def countries_per_continent(df: pd.DataFrame) -> pd.Series:
    return df.groupby("continent")["iso3"].nunique()


# Finding 6: money going out -----------------------------------------------------------------------

def outflow_share(df: pd.DataFrame, end: int = PANEL_END) -> pd.Series:
    """Share of reporting countries with negative inflows each year, stopping before coverage thins out."""
    rows = df[df["year"] <= end]
    return rows.groupby("year")[VALUE].apply(lambda values: (values < 0).mean())


def ever_negative(df: pd.DataFrame) -> int:
    """How many countries recorded negative inflows in at least one year."""
    return int(df.groupby("iso3")[VALUE].min().lt(0).sum())


# Finding 7: can you forecast it? -----------------------------------------------------------------

def backtest(series: pd.Series, start: int = BACKTEST_START) -> pd.DataFrame:
    """Predict each year using only the years before it, the way a real forecast would have to.

    `Last year` simply repeats the previous value. `Linear trend` fits a straight line through the years so far.
    """
    rows = []
    for year in series.index[series.index >= start]:
        past = series[series.index < year]
        trend = LinearRegression().fit(past.index.to_numpy().reshape(-1, 1), past.to_numpy())
        rows.append(
            {
                "year": year,
                "Actual": series[year],
                "Last year": past.iloc[-1],
                "Linear trend": trend.predict([[year]])[0],
            }
        )
    return pd.DataFrame(rows).set_index("year")


def backtest_errors(table: pd.DataFrame) -> pd.Series:
    """Mean absolute error of each method, in the units of the series."""
    return table.drop(columns="Actual").sub(table["Actual"], axis=0).abs().mean()


# The correction to the first version of this project ---------------------------------------------

def first_version() -> dict:
    """What the original notebook's method produced, from the raw file, to show the size of the correction.

    It summed OBS_VALUE without filtering on UNIT_MEASURE, so most country-years were counted twice in two
    different price bases. Its one model used a random train/test split on those mixed rows for France.
    """
    raw = pd.read_csv(RAW)
    correct = raw[raw["UNIT_MEASURE"] == "USD_K_2015"]
    france = raw[raw["REF_AREA_LABEL"] == "France"]
    x_train, x_test, y_train, y_test = train_test_split(
        france[["TIME_PERIOD"]], france["OBS_VALUE"], test_size=0.2, random_state=42
    )
    model = LinearRegression().fit(x_train, y_train)
    return {
        "old_total": raw["OBS_VALUE"].sum(),
        "correct_total": correct["OBS_VALUE"].sum(),
        "old_2015": raw.loc[raw["TIME_PERIOD"] == 2015, "OBS_VALUE"].sum(),
        "correct_2015": correct.loc[correct["TIME_PERIOD"] == 2015, "OBS_VALUE"].sum(),
        "france_rows": len(france),
        "france_r2": r2_score(y_test, model.predict(x_test)),
    }
