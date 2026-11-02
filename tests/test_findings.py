"""Checks that the data is sound and the findings hold up. Run from the repository root with `pytest`."""

import re
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "findings"), str(ROOT / "data")]

import analysis as an  # noqa: E402
import prepare  # noqa: E402


@pytest.fixture(scope="module")
def df() -> pd.DataFrame:
    return an.load()


@pytest.fixture(scope="module")
def raw() -> pd.DataFrame:
    return pd.read_csv(an.RAW)


def test_committed_table_matches_the_raw_file():
    committed = pd.read_csv(prepare.TIDY)
    pd.testing.assert_frame_equal(committed, prepare.prepare().reset_index(drop=True), check_dtype=False)


def test_one_row_per_country_and_year(df):
    assert not df.duplicated(["iso3", "year"]).any()


def test_price_bases_are_never_added_together(df, raw):
    """The bug in the first version: summing OBS_VALUE across both units."""
    real = raw.loc[raw["UNIT_MEASURE"] == "USD_K_2015", "OBS_VALUE"].sum()
    assert df[an.VALUE].sum() == pytest.approx(real, rel=1e-6)
    assert raw["OBS_VALUE"].sum() > 1.9 * real


def test_every_country_has_a_continent():
    assert pd.read_csv(prepare.TIDY)["continent"].notna().all()


def test_panel_is_balanced(df):
    table = an.panel(df)
    assert not table.isna().any().any()
    assert list(table.index) == list(range(an.PANEL_START, an.PANEL_END + 1))


def test_outlier_is_out_of_the_rankings_but_in_the_raw_totals(df):
    assert an.lifetime_totals(df)["Germany"] < 1000
    assert df.groupby("year")[an.VALUE].sum()[2012] > 20_000
    assert an.one_figure(df)["share_of_year"] > 0.5


def test_shares_of_the_fall_add_up(df):
    assert an.share_of_fall(df).sum() == pytest.approx(1)


def test_backtest_never_sees_the_future():
    series = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0, 6.0], index=range(2010, 2016))
    changed = series.copy()
    changed[2015] = 1000.0
    before, after = an.backtest(series, start=2013), an.backtest(changed, start=2013)
    columns = ["Last year", "Linear trend"]
    pd.testing.assert_frame_equal(before[columns], after[columns])
    assert before.loc[2013, "Last year"] == 3.0
    assert before.loc[2013, "Linear trend"] == pytest.approx(4.0)


def test_writing_has_no_broken_values():
    for path in (ROOT / "README.md", ROOT / "findings" / "README.md"):
        text = path.read_text(encoding="utf-8")
        assert "nan" not in re.findall(r"\bnan\b", text)
        assert "Filled in by" not in text


def test_every_chart_in_the_writing_exists():
    for path in (ROOT / "README.md", ROOT / "findings" / "README.md"):
        for link in re.findall(r"!\[[^\]]*\]\(([^)]+\.svg)\)", path.read_text(encoding="utf-8")):
            if not link.startswith("http"):
                assert (path.parent / link).resolve().exists(), link


def test_readme_alt_text_matches_the_data(df):
    """The tile descriptions in the README are written by hand, so check them."""
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    total = an.panel(df).sum(axis=1).loc[an.PANEL_END] / 1000
    assert f"ending at {total:.1f} billion dollars" in text
    assert f"received {an.concentration(an.lifetime_totals(df))['top_2']:.0%}".replace("%", " percent") in text
    assert f"for {df['iso3'].nunique()} countries" in text
