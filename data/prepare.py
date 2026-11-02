"""Turn the raw World Bank download into the tidy table every other script reads.

Run from the repository root:

    python data/prepare.py

The raw file has 37 columns and holds each country and year twice, once in current US dollars and once at
constant 2015 prices. This keeps the fields that vary and puts the two price bases side by side, so they
can't be added together by accident.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "FAO_FDI.csv"
COUNTRIES = ROOT / "data" / "countries.csv"
TIDY = ROOT / "data" / "fdi_inflows.csv"

UNITS = {"USD": "fdi_usd_m_current", "USD_K_2015": "fdi_usd_m_2015"}


def prepare() -> pd.DataFrame:
    raw = pd.read_csv(RAW)
    unexpected = set(raw["UNIT_MEASURE"]) - set(UNITS)
    if unexpected:
        raise ValueError(f"Unknown units in the raw file: {sorted(unexpected)}")
    if raw["UNIT_MULT"].nunique() != 1 or raw["UNIT_MULT"].iloc[0] != 6:
        raise ValueError("Expected every value to be in millions")

    tidy = (
        raw.pivot(index=["REF_AREA", "REF_AREA_LABEL", "TIME_PERIOD"], columns="UNIT_MEASURE", values="OBS_VALUE")
        .rename(columns=UNITS)
        .reset_index()
        .rename(columns={"REF_AREA": "iso3", "REF_AREA_LABEL": "country", "TIME_PERIOD": "year"})
    )
    tidy.columns.name = None
    continents = pd.read_csv(COUNTRIES)[["iso3", "continent"]]
    tidy = tidy.merge(continents, on="iso3", how="left", validate="many_to_one")
    if tidy["continent"].isna().any():
        missing = sorted(tidy.loc[tidy["continent"].isna(), "iso3"].unique())
        raise ValueError(f"No continent for: {missing}")

    columns = ["iso3", "country", "continent", "year", "fdi_usd_m_current", "fdi_usd_m_2015"]
    return tidy[columns].sort_values(["country", "year"]).round(6).reset_index(drop=True)


if __name__ == "__main__":
    table = prepare()
    table.to_csv(TIDY, index=False)
    print(f"Wrote {len(table):,} rows to {TIDY.relative_to(ROOT)}")
