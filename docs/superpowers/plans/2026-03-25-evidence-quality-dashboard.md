# EvidenceQuality Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a single-file HTML dashboard that grades 403 Cochrane reviews across 4 evidence quality dimensions (Fragility, Bias, Prediction, ORB) with completeness tiers, interactive sorting, and accordion detail panels.

**Architecture:** Two-phase build: (1) Python script merges 4 source CSVs via LEFT JOIN, computes quality scores with re-weighted scoring for missing components, outputs JSON. (2) Single-file HTML dashboard embeds the JSON and renders summary cards, grade distribution chart, component heatmap, sortable table, and accordion detail panels.

**Tech Stack:** Python 3.x (csv, json, pathlib), vanilla HTML/CSS/JS, SVG for charts.

**Spec:** `C:\EvidenceQuality\docs\superpowers\specs\2026-03-25-evidence-quality-dashboard-design.md`

---

## File Structure

| File | Responsibility |
|------|---------------|
| `C:\EvidenceQuality\build_unified.py` | Existing — rewrite to LEFT JOIN, nested JSON output, completeness tiers |
| `C:\EvidenceQuality\data\reviews.json` | Build artifact — 403 reviews as JSON array |
| `C:\EvidenceQuality\dashboard.html` | New — single-file HTML dashboard (~2,000 lines) |

---

### Task 1: Rewrite `build_unified.py` — LEFT JOIN with nested JSON output

**Files:**
- Modify: `C:\EvidenceQuality\build_unified.py`
- Output: `C:\EvidenceQuality\data\reviews.json`

**Context:** The existing script uses an inner-join and default fallbacks for missing data. We need a LEFT JOIN from FragilityAtlas (403 reviews), with BiasForensics as the only source of incompleteness (307/403). Missing components must be `null`, not filled with defaults. Scoring uses continuous values and re-weights for missing components.

- [ ] **Step 1: Rewrite `build_unified.py`**

```python
"""Build unified evidence quality dataset from 4 source projects.

LEFT JOIN from FragilityAtlas base (403 reviews).
Missing components are null, not defaulted.
Scoring re-weights available components.
Output: data/reviews.json
"""

import csv
import json
from pathlib import Path


def load_csv(path):
    """Load CSV into dict keyed by review_id. Returns {} if file missing."""
    data = {}
    p = Path(path)
    if not p.exists():
        print(f"  WARNING: {path} not found, skipping")
        return data
    with open(p, encoding='utf-8') as f:
        for row in csv.DictReader(f):
            data[row['review_id']] = row
    return data


def safe_float(val, default=None):
    """Parse float, return default if empty/invalid."""
    if val is None or val == '':
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def safe_int(val, default=None):
    """Parse int, return default if empty/invalid."""
    if val is None or val == '':
        return default
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return default


def compute_score(fragility, bias, prediction, orb):
    """Compute weighted quality score from available components.

    Base weights: Fragility 35%, Bias 25%, Prediction 25%, ORB 15%.
    Re-weights proportionally when a component is None.
    Returns (score, grade) or (None, 'Insufficient') if <2 components.
    """
    components = []
    weights = []

    if fragility is not None:
        components.append(fragility)
        weights.append(0.35)
    if bias is not None:
        components.append(bias)
        weights.append(0.25)
    if prediction is not None:
        components.append(prediction)
        weights.append(0.25)
    if orb is not None:
        components.append(orb)
        weights.append(0.15)

    if len(components) < 2:
        return None, 'Insufficient'

    total_w = sum(weights)
    score = sum(c * w / total_w for c, w in zip(components, weights))
    score = round(score, 1)

    if score >= 80:
        grade = 'A'
    elif score >= 60:
        grade = 'B'
    elif score >= 40:
        grade = 'C'
    else:
        grade = 'D'

    return score, grade


BIAS_MAP = {'Clean': 100, 'Suspected': 60, 'Confirmed': 20, 'Discordant': 40}
PRED_MAP = {'CONCORDANT_SIG': 100, 'CONCORDANT_NS': 60, 'FALSE_REASSURANCE': 20}


def main():
    print("Loading source datasets...")
    fragility = load_csv(r'C:\FragilityAtlas\data\output\fragility_atlas_results.csv')
    bias = load_csv(r'C:\BiasForensics\data\output\bias_forensics_results.csv')
    prediction = load_csv(r'C:\PredictionGap\data\output\prediction_gap_results.csv')
    orb = load_csv(r'C:\OutcomeReportingBias\data\output\orb_results.csv')

    print(f"  FragilityAtlas: {len(fragility)} reviews")
    print(f"  BiasForensics:  {len(bias)} reviews")
    print(f"  PredictionGap:  {len(prediction)} reviews")
    print(f"  ORB:            {len(orb)} reviews")

    # LEFT JOIN from FragilityAtlas base
    reviews = []
    for rid in sorted(fragility.keys()):
        fa = fragility[rid]
        bf = bias.get(rid)
        pg = prediction.get(rid)
        ob = orb.get(rid)

        # Count available sources
        completeness = 1  # FA always present
        if bf is not None:
            completeness += 1
        if pg is not None:
            completeness += 1
        if ob is not None:
            completeness += 1

        # Component scores (None if source missing)
        frag_score = safe_float(fa.get('robustness_score'))

        bias_score = None
        if bf is not None:
            bc = bf.get('bias_class', '')
            bias_score = BIAS_MAP.get(bc)

        pred_score = None
        if pg is not None:
            disc = pg.get('discordance', '')
            pred_score = PRED_MAP.get(disc)

        orb_raw = None
        orb_score_val = None
        if ob is not None:
            orb_raw = safe_float(ob.get('orb_score'))
            if orb_raw is not None:
                orb_score_val = round(100 - orb_raw, 1)

        quality_score, quality_grade = compute_score(
            frag_score, bias_score, pred_score, orb_score_val
        )

        # Build nested record
        record = {
            'review_id': rid,
            'analysis_name': fa.get('analysis_name', ''),
            'k': safe_int(fa.get('k')),
            'review_doi': fa.get('review_doi', ''),
            'completeness': completeness,
            'quality_score': quality_score,
            'quality_grade': quality_grade,
            'fragility': {
                'robustness_score': frag_score,
                'classification': fa.get('classification', ''),
                'top_dimension': fa.get('top_dimension', ''),
                'frac_significant': safe_float(fa.get('frac_significant')),
                'frac_reversed': safe_float(fa.get('frac_reversed')),
            },
            'bias': {
                'bias_class': bf.get('bias_class', ''),
                'n_detect': safe_int(bf.get('n_detect')),
                'egger_p': safe_float(bf.get('egger_p')),
                'egger_sig': safe_int(bf.get('egger_sig')),
                'tf_k0': safe_int(bf.get('tf_k0')),
                'petpeese_theta': safe_float(bf.get('petpeese_theta')),
                'petpeese_method': bf.get('petpeese_method', ''),
            } if bf is not None else None,
            'prediction': {
                'discordance': pg.get('discordance', ''),
                'pi_ci_ratio': safe_float(pg.get('pi_ci_ratio')),
                'tau2': safe_float(pg.get('tau2')),
                'I2': safe_float(pg.get('I2')),
                'ci_lo': safe_float(pg.get('ci_lo')),
                'ci_hi': safe_float(pg.get('ci_hi')),
                'pi_lo': safe_float(pg.get('pi_lo')),
                'pi_hi': safe_float(pg.get('pi_hi')),
            } if pg is not None else None,
            'orb': {
                'orb_class': ob.get('orb_class', ''),
                'orb_score': safe_float(ob.get('orb_score')),
                'excess_significance': safe_float(ob.get('excess_significance')),
                'outlier_ratio': safe_float(ob.get('outlier_ratio')),
            } if ob is not None else None,
        }
        reviews.append(record)

    # Output JSON
    out_path = Path(r'C:\EvidenceQuality\data\reviews.json')
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(reviews, f, indent=None)

    # Summary
    n = len(reviews)
    grades = {g: sum(1 for r in reviews if r['quality_grade'] == g) for g in ['A', 'B', 'C', 'D', 'Insufficient']}
    scored = [r['quality_score'] for r in reviews if r['quality_score'] is not None]
    comp4 = sum(1 for r in reviews if r['completeness'] == 4)
    comp3 = sum(1 for r in reviews if r['completeness'] == 3)

    print(f"\n{'='*50}")
    print("UNIFIED EVIDENCE QUALITY REPORT")
    print(f"{'='*50}")
    print(f"  {n} Cochrane reviews scored")
    print(f"  Completeness: {comp4} with 4/4, {comp3} with 3/4")
    if scored:
        print(f"  Mean quality: {sum(scored)/len(scored):.1f}/100")
        print(f"  Median quality: {sorted(scored)[len(scored)//2]:.1f}/100")
    print()
    for g in ['A', 'B', 'C', 'D']:
        c = grades.get(g, 0)
        print(f"  Grade {g}: {c:4d} ({c/n*100:5.1f}%)")
    print(f"\n  Output: {out_path}")
    print(f"  JSON size: {out_path.stat().st_size / 1024:.0f} KB")


if __name__ == '__main__':
    main()
```

- [ ] **Step 2: Run the build script**

```bash
cd /c/EvidenceQuality && python build_unified.py
```

Expected: 403 reviews scored, ~307 with 4/4, ~96 with 3/4. `data/reviews.json` created.

- [ ] **Step 3: Verify JSON output**

```bash
python -c "import json; d=json.load(open('data/reviews.json')); print(f'{len(d)} reviews'); print(f'Completeness 4: {sum(1 for r in d if r[\"completeness\"]==4)}'); print(f'Completeness 3: {sum(1 for r in d if r[\"completeness\"]==3)}'); print(f'Null bias: {sum(1 for r in d if r[\"bias\"] is None)}'); print(json.dumps(d[0], indent=2)[:500])"
```

Expected: 403 reviews, ~307 completeness 4, ~96 completeness 3 (all with `bias: null`). First record has nested structure.

- [ ] **Step 4: Commit**

```bash
cd /c/EvidenceQuality && git add build_unified.py data/reviews.json && git commit -m "feat: rewrite build pipeline — LEFT JOIN, nested JSON, completeness tiers"
```

---

### Task 2: Dashboard scaffold — HTML structure, CSS, dark mode, header

**Files:**
- Create: `C:\EvidenceQuality\dashboard.html`

**Context:** Create the HTML shell with all sections, CSS custom properties for theming, dark mode toggle, completeness filter, and the embedded JSON data. The JSON from Task 1 will be pasted into a `<script>` tag as `var REVIEWS = [...]`.

- [ ] **Step 1: Create dashboard.html with full HTML structure and CSS**

Create `C:\EvidenceQuality\dashboard.html` with:

1. CSS custom properties for light/dark theming (same pattern as RMST Meta, FragilityAtlas dashboards)
2. Header with title, subtitle, dark mode toggle
3. Completeness filter radio buttons: [All (403) | Complete 4/4 | Bias missing 3/4]
4. Text search input
5. Empty sections for: Summary Cards, Grade Distribution, Heatmap, Table, Footer
6. `<script>` block with `var REVIEWS = [];` placeholder (will be populated with actual data)
7. Utility functions: `escapeHtml()`, `applyFilters()` stub, dark mode toggle, localStorage with `eqd_` prefix

The CSS should include:
- `.stat-grid` with 4 stat boxes
- `.grade-a`, `.grade-b`, `.grade-c`, `.grade-d` color classes
- `.component-good`, `.component-moderate`, `.component-poor`, `.component-missing` status classes
- `.sortable-table` with hover rows
- `.accordion-panel` for expandable detail
- `.compare-table` for detail panel sub-cards
- Print styles hiding interactive elements
- `@media (max-width: 768px)` responsive breakpoints

**This file will be ~400 lines (CSS ~180, HTML ~120, JS scaffold ~100).** The JS sections will be filled in subsequent tasks.

- [ ] **Step 2: Embed actual JSON data**

Read `C:\EvidenceQuality\data\reviews.json` and replace `var REVIEWS = [];` with `var REVIEWS = <actual JSON>;` in the dashboard. Use the build script output directly.

**IMPORTANT:** The JSON will be inside a `<script>` block. Verify it contains no literal `</script>` strings (it won't since it's pure data, but check).

- [ ] **Step 3: Verify — open in browser, confirm page loads, dark mode toggles, no console errors**

- [ ] **Step 4: Commit**

```bash
cd /c/EvidenceQuality && git add dashboard.html && git commit -m "feat: dashboard scaffold — HTML, CSS, dark mode, filters, embedded data"
```

---

### Task 3: Summary cards and `applyFilters()` logic

**Files:**
- Modify: `C:\EvidenceQuality\dashboard.html` — JS section

**Context:** Implement the core filtering function that drives all visualizations. When the completeness filter or text search changes, recompute the filtered dataset and update all sections. Start with the 4 summary stat boxes.

- [ ] **Step 1: Implement `applyFilters()` and `renderSummary()`**

```javascript
function applyFilters() {
  var filterVal = document.querySelector('input[name="completeness"]:checked').value;
  var searchVal = document.getElementById('searchInput').value.toLowerCase().trim();

  filtered = REVIEWS.filter(function(r) {
    // Completeness filter
    if (filterVal === '4' && r.completeness !== 4) return false;
    if (filterVal === '3' && r.completeness !== 3) return false;
    // Text search (AND with completeness)
    if (searchVal) {
      var rid = (r.review_id || '').toLowerCase();
      var name = (r.analysis_name || '').toLowerCase();
      if (rid.indexOf(searchVal) === -1 && name.indexOf(searchVal) === -1) return false;
    }
    return true;
  });

  renderSummary(filtered);
  renderGradeChart(filtered);
  renderHeatmap(filtered);
  renderTable(filtered);
}

function renderSummary(data) {
  var n = data.length;
  var scored = data.filter(function(r) { return r.quality_score !== null; });
  var meanScore = scored.length > 0
    ? (scored.reduce(function(s, r) { return s + r.quality_score; }, 0) / scored.length).toFixed(1)
    : '—';
  var nAB = data.filter(function(r) { return r.quality_grade === 'A' || r.quality_grade === 'B'; }).length;
  var pctAB = n > 0 ? (nAB / n * 100).toFixed(0) : '0';
  var n4 = data.filter(function(r) { return r.completeness === 4; }).length;
  var pct4 = n > 0 ? (n4 / n * 100).toFixed(0) : '0';

  document.getElementById('statTotal').textContent = n;
  document.getElementById('statMean').textContent = meanScore + '/100';
  document.getElementById('statAB').textContent = pctAB + '%';
  document.getElementById('statComplete').textContent = pct4 + '%';
}
```

Wire `applyFilters()` to the radio buttons (`onchange`) and search input (`oninput` with 200ms debounce). Call `applyFilters()` on page load.

- [ ] **Step 2: Stub out the other render functions**

```javascript
function renderGradeChart(data) { /* Task 4 */ }
function renderHeatmap(data) { /* Task 5 */ }
function renderTable(data) { /* Task 6 */ }
```

- [ ] **Step 3: Verify — open in browser, toggle filters, confirm stat boxes update**

With "All": Total=403, Mean=some value, %A+B=some%, %Complete=~76%.
Switch to "Complete 4/4": Total=307. Switch to "Bias missing": Total=96.
Type "CD000" in search: count drops to matching reviews.

- [ ] **Step 4: Commit**

```bash
cd /c/EvidenceQuality && git add dashboard.html && git commit -m "feat: summary cards + filter logic (completeness + text search)"
```

---

### Task 4: Grade distribution bar chart (SVG)

**Files:**
- Modify: `C:\EvidenceQuality\dashboard.html` — `renderGradeChart()`

**Context:** Horizontal bar chart showing count per grade (A/B/C/D). Each bar stacked by completeness tier (4/4 darker, 3/4 lighter). SVG rendered into `#gradeChartContainer`.

- [ ] **Step 1: Implement `renderGradeChart()`**

```javascript
function renderGradeChart(data) {
  var container = document.getElementById('gradeChartContainer');
  var grades = ['A', 'B', 'C', 'D'];
  var colors = { A: '#198754', B: '#2563eb', C: '#ffc107', D: '#dc3545' };
  var lightColors = { A: '#6ec98d', B: '#7da8f0', C: '#ffe066', D: '#f08080' };

  // Count per grade, split by completeness
  var counts = {};
  grades.forEach(function(g) {
    counts[g] = { c4: 0, c3: 0 };
  });
  data.forEach(function(r) {
    if (counts[r.quality_grade]) {
      if (r.completeness === 4) counts[r.quality_grade].c4++;
      else counts[r.quality_grade].c3++;
    }
  });

  var maxCount = Math.max.apply(null, grades.map(function(g) {
    return counts[g].c4 + counts[g].c3;
  }));
  if (maxCount === 0) maxCount = 1;

  var barH = 36, gap = 12, ml = 60, mr = 60, mt = 10, mb = 10;
  var chartW = 600;
  var barArea = chartW - ml - mr;
  var svgH = mt + grades.length * (barH + gap) + mb;

  var lines = [];
  lines.push('<svg width="' + chartW + '" height="' + svgH + '" role="img" aria-label="Grade distribution chart">');

  var isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  var textColor = isDark ? '#e5e7eb' : '#1f2937';

  grades.forEach(function(g, i) {
    var y = mt + i * (barH + gap);
    var total = counts[g].c4 + counts[g].c3;
    var w4 = counts[g].c4 / maxCount * barArea;
    var w3 = counts[g].c3 / maxCount * barArea;

    // 4/4 bar (darker)
    lines.push('<rect x="' + ml + '" y="' + y + '" width="' + w4 + '" height="' + barH + '" fill="' + colors[g] + '" rx="3"/>');
    // 3/4 bar (lighter, stacked after)
    if (w3 > 0) {
      lines.push('<rect x="' + (ml + w4) + '" y="' + y + '" width="' + w3 + '" height="' + barH + '" fill="' + lightColors[g] + '" rx="3"/>');
    }

    // Grade label
    lines.push('<text x="' + (ml - 10) + '" y="' + (y + barH / 2 + 5) + '" text-anchor="end" font-size="14" font-weight="700" fill="' + textColor + '">Grade ' + g + '</text>');
    // Count label
    lines.push('<text x="' + (ml + w4 + w3 + 8) + '" y="' + (y + barH / 2 + 5) + '" font-size="12" fill="' + textColor + '">' + total + ' (' + (data.length > 0 ? (total / data.length * 100).toFixed(0) : 0) + '%)</text>');
  });

  lines.push('</svg>');
  container.innerHTML = lines.join('');
}
```

- [ ] **Step 2: Verify — run analysis, see 4 horizontal bars with stacked completeness segments**

- [ ] **Step 3: Commit**

```bash
cd /c/EvidenceQuality && git add dashboard.html && git commit -m "feat: grade distribution bar chart (stacked by completeness)"
```

---

### Task 5: Component heatmap (SVG)

**Files:**
- Modify: `C:\EvidenceQuality\dashboard.html` — `renderHeatmap()`

**Context:** Purely visual SVG grid. 4 columns (Fragility, Bias, Prediction, ORB) x N rows sorted by quality_score descending. Each cell colored by component quality. No interactivity (too dense at ~1.5px per row).

- [ ] **Step 1: Implement `renderHeatmap()`**

```javascript
function renderHeatmap(data) {
  var container = document.getElementById('heatmapContainer');
  if (data.length === 0) { container.innerHTML = ''; return; }

  // Sort by quality_score descending
  var sorted = data.slice().sort(function(a, b) {
    return (b.quality_score || 0) - (a.quality_score || 0);
  });

  var cols = ['fragility', 'bias', 'prediction', 'orb'];
  var colLabels = ['Fragility', 'Bias', 'Prediction', 'ORB'];
  var ml = 80, mt = 30, colW = 120, gap = 4;
  var totalW = ml + cols.length * (colW + gap);
  var rowH = Math.max(1.5, Math.min(4, 600 / sorted.length));
  var totalH = mt + sorted.length * rowH + 10;

  var isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  var textColor = isDark ? '#e5e7eb' : '#1f2937';
  var goodColor = isDark ? '#22c55e' : '#198754';
  var modColor = isDark ? '#eab308' : '#d4a017';
  var poorColor = isDark ? '#ef4444' : '#dc3545';
  var missColor = isDark ? '#374151' : '#d1d5db';

  function componentScore(r, col) {
    if (col === 'fragility') return r.fragility ? r.fragility.robustness_score : null;
    if (col === 'bias') {
      if (!r.bias) return null;
      var m = { Clean: 100, Suspected: 60, Confirmed: 20, Discordant: 40 };
      return m[r.bias.bias_class] || null;
    }
    if (col === 'prediction') {
      if (!r.prediction) return null;
      var p = { CONCORDANT_SIG: 100, CONCORDANT_NS: 60, FALSE_REASSURANCE: 20 };
      return p[r.prediction.discordance] || null;
    }
    if (col === 'orb') {
      if (!r.orb || r.orb.orb_score === null) return null;
      return 100 - r.orb.orb_score;
    }
    return null;
  }

  function cellColor(score) {
    if (score === null) return missColor;
    if (score >= 80) return goodColor;
    if (score >= 40) return modColor;
    return poorColor;
  }

  var lines = [];
  lines.push('<svg width="' + totalW + '" height="' + totalH + '" role="img" aria-label="Component quality heatmap">');

  // Column headers
  cols.forEach(function(col, ci) {
    var x = ml + ci * (colW + gap) + colW / 2;
    lines.push('<text x="' + x + '" y="' + (mt - 8) + '" text-anchor="middle" font-size="11" font-weight="600" fill="' + textColor + '">' + colLabels[ci] + '</text>');
  });

  // Rows
  sorted.forEach(function(r, ri) {
    var y = mt + ri * rowH;
    cols.forEach(function(col, ci) {
      var x = ml + ci * (colW + gap);
      var score = componentScore(r, col);
      lines.push('<rect x="' + x + '" y="' + y + '" width="' + colW + '" height="' + rowH + '" fill="' + cellColor(score) + '"/>');
    });
  });

  // Legend
  var ly = totalH - 5;
  // (legend will be simple text below the heatmap)

  lines.push('</svg>');

  // Add legend below SVG
  container.innerHTML = lines.join('') +
    '<div class="heatmap-legend">' +
    '<span class="legend-item"><span class="legend-swatch" style="background:' + goodColor + '"></span> Good (&ge;80)</span>' +
    '<span class="legend-item"><span class="legend-swatch" style="background:' + modColor + '"></span> Moderate (40-79)</span>' +
    '<span class="legend-item"><span class="legend-swatch" style="background:' + poorColor + '"></span> Poor (&lt;40)</span>' +
    '<span class="legend-item"><span class="legend-swatch" style="background:' + missColor + '"></span> Missing</span>' +
    '</div>';
}
```

Add CSS for the legend:
```css
.heatmap-legend { display: flex; gap: 1rem; margin-top: 0.5rem; font-size: 0.8rem; }
.legend-item { display: flex; align-items: center; gap: 0.3rem; }
.legend-swatch { width: 14px; height: 14px; border-radius: 2px; display: inline-block; }
```

- [ ] **Step 2: Verify — colored grid visible, sorted top-to-bottom (best at top), grey column for missing Bias on ~96 reviews**

- [ ] **Step 3: Commit**

```bash
cd /c/EvidenceQuality && git add dashboard.html && git commit -m "feat: component quality heatmap (data fingerprint)"
```

---

### Task 6: Sortable table with grade badges

**Files:**
- Modify: `C:\EvidenceQuality\dashboard.html` — `renderTable()`

**Context:** Sortable table with 10 columns. Click column headers to sort. Grade badges colored. Component cells show status text colored by quality. Default sort: quality_score descending.

- [ ] **Step 1: Implement `renderTable()` and sort logic**

The table renders into `#tableContainer`. Each row gets `data-idx` pointing to the filtered array index. Column headers get `onclick` handlers for sorting.

Key implementation details:
- Sort state: `var sortCol = 'quality_score'; var sortAsc = false;`
- `sortTable(col)` toggles direction if same col, else sort descending
- Grade badges: `<span class="grade-badge grade-X">X</span>`
- Component cells use `componentStatusHtml(r, col)` returning colored text
- Table rows are clickable (Task 7 adds the accordion)

- [ ] **Step 2: Verify — table shows 403 rows, sortable by clicking headers, grade badges colored**

- [ ] **Step 3: Commit**

```bash
cd /c/EvidenceQuality && git add dashboard.html && git commit -m "feat: sortable review table with grade badges"
```

---

### Task 7: Accordion detail panels

**Files:**
- Modify: `C:\EvidenceQuality\dashboard.html` — add `toggleDetail()` and detail rendering

**Context:** Clicking a table row (or pressing Enter/Space) expands an inline detail panel below it. The panel shows 4 component cards with full sub-metrics. Missing components shown as grey "Not available" cards.

- [ ] **Step 1: Implement accordion toggle and detail rendering**

```javascript
function toggleDetail(idx) {
  var existingPanel = document.getElementById('detail-' + idx);
  if (existingPanel) {
    existingPanel.remove();
    return;
  }
  // Close any other open panel
  var open = document.querySelectorAll('.detail-panel');
  open.forEach(function(p) { p.remove(); });

  var r = filtered[idx];
  var row = document.querySelector('[data-idx="' + idx + '"]');
  if (!row) return;

  var panel = document.createElement('tr');
  panel.id = 'detail-' + idx;
  panel.className = 'detail-panel';
  var td = document.createElement('td');
  td.colSpan = 10;
  td.innerHTML = renderDetailContent(r);
  panel.appendChild(td);
  row.after(panel);
}
```

`renderDetailContent(r)` returns HTML with:
- Header: `review_id — review_doi` (text, not linked)
- 4-card grid (`.detail-grid` with `grid-template-columns: repeat(auto-fit, minmax(250px, 1fr))`)
- Each card: title, key metrics as labeled values
- Null components: grey card with "Data not available for this review"

Detail for each component card:

**Fragility:** Robustness score (bold), classification badge, top dimension, frac_significant, frac_reversed
**Bias:** Bias class badge, "N/8 methods detected bias", Egger p-value (sig/ns), Trim-fill k0, PET-PEESE estimate
**Prediction:** Discordance badge, PI/CI ratio, tau², I², CI and PI bounds
**ORB:** ORB class badge, ORB score, excess significance, outlier ratio

- [ ] **Step 2: Wire keyboard accessibility**

Add to table row rendering: `tabindex="0" role="button" aria-expanded="false"`
Add keydown handler: Enter or Space triggers `toggleDetail(idx)` and toggles `aria-expanded`.

- [ ] **Step 3: Verify — click a row, panel expands with 4 cards. Click again, collapses. Click different row, old closes, new opens. Enter/Space work.**

- [ ] **Step 4: Commit**

```bash
cd /c/EvidenceQuality && git add dashboard.html && git commit -m "feat: accordion detail panels with 4 component cards"
```

---

### Task 8: CSV + PNG export, footer, final polish

**Files:**
- Modify: `C:\EvidenceQuality\dashboard.html`

**Context:** Add export buttons (CSV of filtered data, PNG of grade chart), footer with version, and final polish (print styles, responsive).

- [ ] **Step 1: Implement CSV export**

```javascript
function exportCSV() {
  var headers = ['review_id', 'analysis_name', 'k', 'completeness',
    'quality_score', 'quality_grade',
    'fragility_class', 'robustness_score',
    'bias_class', 'n_detect',
    'discordance', 'pi_ci_ratio',
    'orb_class', 'orb_score'];
  var rows = [headers.join(',')];
  filtered.forEach(function(r) {
    rows.push([
      r.review_id, '"' + (r.analysis_name || '').replace(/"/g, '""') + '"',
      r.k, r.completeness, r.quality_score, r.quality_grade,
      r.fragility ? r.fragility.classification : '',
      r.fragility ? r.fragility.robustness_score : '',
      r.bias ? r.bias.bias_class : '',
      r.bias ? r.bias.n_detect : '',
      r.prediction ? r.prediction.discordance : '',
      r.prediction ? r.prediction.pi_ci_ratio : '',
      r.orb ? r.orb.orb_class : '',
      r.orb ? r.orb.orb_score : ''
    ].join(','));
  });
  var blob = new Blob([rows.join('\n')], { type: 'text/csv;charset=utf-8' });
  var url = URL.createObjectURL(blob);
  var a = document.createElement('a');
  a.href = url;
  a.download = 'evidence_quality_' + filtered.length + '_reviews.csv';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
```

- [ ] **Step 2: Implement PNG export of grade chart**

Reuse the same SVG-to-Canvas-to-PNG pattern from RMST Meta (Task 9 of that plan). Target: `#gradeChartContainer svg`.

- [ ] **Step 3: Add footer**

```html
<footer>Evidence Quality Dashboard v1.0 — Browser-based, no data leaves your device.</footer>
```

- [ ] **Step 4: Verify — CSV downloads with correct columns, PNG downloads grade chart, footer visible**

- [ ] **Step 5: Commit**

```bash
cd /c/EvidenceQuality && git add dashboard.html && git commit -m "feat: CSV + PNG export, footer, final polish"
```

---

### Task 9: Integration test

**Files:**
- Modify: none (testing only)

- [ ] **Step 1: Full test with "All" filter**

Open `dashboard.html` in browser:
1. Summary cards: Total=403, Mean score populated, %A+B populated, %Complete=~76%
2. Grade chart: 4 bars visible, stacked colors
3. Heatmap: 4 columns, ~403 rows, grey band visible for missing Bias
4. Table: 403 rows, sortable, grade badges colored
5. Click first row: detail panel expands with 4 cards
6. No console errors

- [ ] **Step 2: Test "Complete 4/4" filter**

Switch filter: Total=~307, heatmap has no grey cells, table updates

- [ ] **Step 3: Test "Bias missing 3/4" filter**

Switch filter: Total=~96, all Bias column cells grey in heatmap, bias card says "Not available" in detail

- [ ] **Step 4: Test text search**

Type "cardiovascular": table filters to matching reviews, summary cards update

- [ ] **Step 5: Test dark mode**

Toggle dark mode: all text readable, heatmap colors adapt, cards have dark backgrounds

- [ ] **Step 6: Test exports**

CSV: downloads file with correct row count. PNG: downloads grade chart image.

- [ ] **Step 7: Div balance check**

```javascript
var html = document.documentElement.outerHTML;
var opens = (html.match(/<div[\s>]/g) || []).length;
var closes = (html.match(/<\/div>/g) || []).length;
console.log('Balanced:', opens === closes, opens, closes);
```

- [ ] **Step 8: Commit**

```bash
cd /c/EvidenceQuality && git add -A && git commit -m "chore: integration test passed, v1.0 verified"
```
