# Changelog

All notable changes to this project are listed here. Versions are dated by month, like `v2026.11`.

## v2026.11 · November 2026

A full rebuild, from a single notebook into a tested, reproducible analysis.

### Fixed

- The first version summed current-dollar and constant-2015 rows together, so every total was roughly double. All
  money now uses constant 2015 prices, and a test stops the two being combined again
- Comparing all reporting countries made changes in coverage look like changes in investment. The trend now follows
  only countries that reported every year from 2005 to 2021
- The France model trained on mixed units with a random split. It is replaced by a test that predicts each year from
  earlier years only

### Added

- A findings report with seven findings, every number worked out from the data
- Eight charts and three headline tiles, all drawn with [bezel-charts](https://pypi.org/project/bezel-charts/)
- Tidy data, a continent lookup and a record of sources in `data/`
- Tests, an automatic check on every pull request, Dependabot and a security policy
- Social preview image in `assets/social-preview.png`

### Changed

- New folder structure: `data/`, `findings/`, `notebooks/`, `charts/` and `tests/`
- README rewritten around the findings
- Notebook rewritten and moved to `notebooks/fdi_analysis.ipynb`

## January 2026

- First version: one notebook and the raw CSV
