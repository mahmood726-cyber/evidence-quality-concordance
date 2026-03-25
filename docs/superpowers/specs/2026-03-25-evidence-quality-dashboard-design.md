# EvidenceQuality Dashboard Design Spec

**Date:** 2026-03-25
**Target:** `C:\EvidenceQuality\dashboard.html` (new single-file HTML app)
**Build step:** `C:\EvidenceQuality\build_unified.py` (existing, to be updated)
**Data sources:** 4 project outputs (FragilityAtlas, BiasForensics, PredictionGap, OutcomeReportingBias)

## Background

Four independent meta-research projects each assess a different dimension of evidence quality across Cochrane systematic reviews:

1. **Fragility Atlas** (403 reviews) — multiverse robustness analysis
2. **Bias Forensics** (307 reviews) — 8 publication bias detection methods
3. **Prediction Gap** (403 reviews) — PI/CI discordance analysis
4. **Outcome Reporting Bias** (403 reviews) — excess significance and ORB risk

Currently, a 152-line Python script (`build_unified.py`) merges these into a unified CSV, but strict inner-join yields only 10 reviews. No interactive visualization exists.

## Goal

Build a single-file HTML dashboard that presents unified evidence quality grades for all 403 Cochrane reviews, with completeness tiers for reviews missing one or more components.

## 1. Data Pipeline (build step)

### Updated `build_unified.py`

**Join strategy: LEFT JOIN from FragilityAtlas base**

1. Load FragilityAtlas (403 reviews) as the base — it has broadest coverage and the primary review_id index
2. Left-join BiasForensics (307) by `review_id`
3. Left-join PredictionGap (403) by `review_id`
4. Left-join ORB (403) by `review_id`
5. For each review, count non-null sources → `completeness` field (2, 3, or 4)
6. Compute quality score using available components with re-weighted scoring
7. Assign grade (A/B/C/D) or "Insufficient Data" if <2 components
8. Output `data/reviews.json` — JSON array embedded in the dashboard

### Source file paths

```
C:\FragilityAtlas\data\output\fragility_atlas_results.csv     (403 rows, 20 cols)
C:\BiasForensics\data\output\bias_forensics_results.csv       (307 rows, 29 cols)
C:\PredictionGap\data\output\prediction_gap_results.csv       (403 rows, 14 cols)
C:\OutcomeReportingBias\data\output\orb_results.csv           (403 rows, 11 cols)
```

### Fields extracted per source

**From FragilityAtlas:**
- `robustness_score` (0-100)
- `classification` (Robust/Moderate/Fragile/Unstable)
- `top_dimension` (which analyst decision drives most variance)
- `frac_significant` (fraction of specifications yielding significance)
- `frac_reversed` (fraction reversing direction)
- `analysis_name`, `k`, `review_doi`

**From BiasForensics:**
- `bias_class` (Clean/Suspected/Confirmed/Discordant)
- `n_detect` (count of 8 methods detecting bias)
- `egger_p`, `egger_sig`
- `tf_k0` (trim-fill imputed studies)
- `petpeese_theta`, `petpeese_method`

**From PredictionGap:**
- `discordance` (CONCORDANT_SIG/CONCORDANT_NS/FALSE_REASSURANCE/HIDDEN_SIGNAL)
- `pi_ci_ratio` (prediction interval / CI width ratio)
- `tau2`, `I2`
- `ci_lo`, `ci_hi`, `pi_lo`, `pi_hi`

**From ORB:**
- `orb_class` (Low_Risk/Moderate_Risk/High_Risk)
- `orb_score` (0-100)
- `excess_significance` (observed - expected)
- `outlier_ratio`

### Output JSON structure per review

```json
{
  "review_id": "CD000028",
  "analysis_name": "Cause of cardiovascular mortality",
  "k": 21,
  "review_doi": "...",
  "completeness": 4,
  "quality_score": 62.5,
  "quality_grade": "B",
  "fragility": {
    "robustness_score": 66.67,
    "classification": "Fragile",
    "top_dimension": "estimator",
    "frac_significant": 0.85,
    "frac_reversed": 0.02
  },
  "bias": {
    "bias_class": "Confirmed",
    "n_detect": 1,
    "egger_p": 0.03,
    "egger_sig": 1,
    "tf_k0": 3,
    "petpeese_theta": -0.18,
    "petpeese_method": "PEESE"
  },
  "prediction": {
    "discordance": "CONCORDANT_SIG",
    "pi_ci_ratio": 1.07,
    "tau2": 0.05,
    "I2": 42.3,
    "ci_lo": -0.45,
    "ci_hi": -0.14,
    "pi_lo": -0.72,
    "pi_hi": 0.13
  },
  "orb": {
    "orb_class": "Low_Risk",
    "orb_score": 10,
    "excess_significance": -0.57,
    "outlier_ratio": 0.05
  }
}
```

Missing components are `null` (e.g., `"bias": null` if review not in BiasForensics).

## 2. Scoring Logic

### Base weights

| Component | Weight | Score mapping |
|-----------|--------|---------------|
| Fragility | 35% | `robustness_score` directly (0-100) |
| Bias | 25% | Clean=100, Suspected=60, Confirmed=20, Discordant=40 |
| Prediction | 25% | CONCORDANT_SIG=100, CONCORDANT_NS=60, HIDDEN_SIGNAL=50, FALSE_REASSURANCE=20 |
| ORB | 15% | Low_Risk=100, Moderate_Risk=60, High_Risk=20 |

### Re-weighting for missing components

When a component is `null`, redistribute its weight proportionally among available components.

Formula: `adjusted_weight[i] = base_weight[i] / sum(base_weights of available components)`

Example with ORB missing:
- Fragility: 35 / (35+25+25) = 41.2%
- Bias: 25 / 85 = 29.4%
- Prediction: 25 / 85 = 29.4%

### Grading thresholds

| Grade | Score range | Color |
|-------|------------|-------|
| A | >= 80 | Green (#198754) |
| B | >= 60 | Blue (#2563eb) |
| C | >= 40 | Amber (#ffc107) |
| D | < 40 | Red (#dc3545) |
| — | < 2 components | Grey — "Insufficient Data" |

## 3. Dashboard Layout

Single scrollable page, no tabs. Dark mode toggle in header.

### Header

- Title: "Evidence Quality Dashboard"
- Subtitle: "Unified assessment of N Cochrane reviews across 4 dimensions"
- Completeness filter: radio buttons [All | 4/4 sources | 3+ sources]

### Section 1 — Summary Cards (stat boxes)

4 boxes in a responsive grid:
1. **Total Reviews** — count matching current filter
2. **Mean Quality Score** — X.X / 100
3. **% Grade A+B** — proportion of reviews with good evidence
4. **% Complete (4/4)** — proportion with all 4 sources

All update dynamically when the completeness filter changes.

### Section 2 — Grade Distribution

Horizontal bar chart (SVG). 4 bars (A/B/C/D), colored by grade. Each bar stacked by completeness tier (4/4 darker, 3/4 lighter, 2/4 lightest). Shows both count and percentage.

### Section 3 — Component Heatmap

SVG grid: 4 columns (Fragility, Bias, Prediction, ORB) x N rows (sorted by quality score, highest at top).

Cell colors:
- **Green**: component score >= 80 (good)
- **Amber**: component score 40-79 (moderate)
- **Red**: component score < 40 (poor)
- **Grey**: component missing (null)

Hovering a cell shows a tooltip with the actual score and classification. Clicking a row scrolls to its detail in the table below.

Dimensions: ~800x600px. For 403 rows, each row is ~1.5px tall — shows the pattern, not individual values. This is a "data fingerprint" visualization.

### Section 4 — Sortable Table

| Column | Source | Sortable |
|--------|--------|----------|
| Review ID | base | Yes |
| Analysis | base | Yes |
| k | base | Yes |
| Score | computed | Yes (default sort, descending) |
| Grade | computed | Yes |
| Tier | computed | Yes |
| Fragility | FA classification | Yes |
| Bias | BF class | Yes |
| Prediction | PG discordance | Yes |
| ORB | ORB class | Yes |

- Grade badges colored by grade
- Component cells colored by status (green/amber/red/grey)
- Text filter on review ID / analysis name
- Click any row to expand detail panel (accordion)

### Section 5 — Expanded Detail Panel (accordion)

When a table row is clicked, an inline panel expands below it showing 4 cards:

**Fragility Card:**
- Robustness score gauge (0-100 with colored arc)
- Classification badge
- Top dimension driving variance
- Frac significant / frac reversed

**Bias Card:**
- Bias class badge
- "N/8 methods detected bias" progress indicator
- Egger's test: p=X.XX (sig/ns)
- Trim-fill: k0 imputed studies
- PET-PEESE: estimate via [method]

**Prediction Card:**
- Discordance type badge
- PI/CI ratio (with visual bar showing CI inside PI)
- tau², I²
- Actual CI and PI bounds displayed

**ORB Card:**
- ORB class badge
- ORB score (0-100)
- Excess significance: +/-X.XX
- Outlier ratio

Missing components shown as greyed-out card with "Data not available for this review".

### Footer

- "Evidence Quality Dashboard v1.0 — Browser-based, no data leaves your device."
- Dark mode toggle (if not in header)
- Export: [CSV] [PNG] buttons (filtered data export, summary chart screenshot)

## 4. Visual Design

Follow existing portfolio conventions:
- CSS custom properties for light/dark theming
- `--bg`, `--bg-card`, `--text`, `--accent`, `--border` variables
- Card-based layout with subtle shadows
- Print styles hiding interactive elements
- Responsive: mobile stacks columns, heatmap scrolls horizontally

## 5. Integration Map

| File | Purpose |
|------|---------|
| `C:\EvidenceQuality\build_unified.py` | Updated: LEFT JOIN, JSON output, completeness tiers |
| `C:\EvidenceQuality\data\reviews.json` | Build artifact: 403 reviews as JSON array |
| `C:\EvidenceQuality\dashboard.html` | New: single-file HTML dashboard (~1,800 lines) |

## 6. Out of Scope

- Cross-review correlation analysis
- Time trends / temporal filtering
- Subgroup filtering by medical condition
- PDF report export
- Live data refresh (build step is manual/one-time)
- Linking to original Cochrane reviews

## 7. Validation

- Review count matches source: 403 reviews from FragilityAtlas base
- Completeness tiers verified: 307 with 4/4 (all in BiasForensics), ~96 with 3/4
- Quality scores verified: manual check of 5 reviews against component scores
- Grade distribution plausible: majority B/C with tails at A and D
- Sort/filter: all columns sortable, filter updates summary cards
- Dark mode: all text/background combos pass WCAG AA (4.5:1)
- Export: CSV contains all visible filtered rows, PNG renders charts
