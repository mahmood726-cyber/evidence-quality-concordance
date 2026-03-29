"""Build dashboard.html by embedding reviews.json and writing the full single-file app."""
import argparse
import json
import os
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_REVIEWS_JSON = PROJECT_ROOT / "data" / "reviews.json"
DEFAULT_DASHBOARD_HTML = PROJECT_ROOT / "dashboard.html"
DEFAULT_DASHBOARD_INDEX_HTML = PROJECT_ROOT / "dashboard" / "index.html"
DIMENSION_LABELS = ["Fragility", "Bias", "Prediction", "ORB"]


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Build EvidenceQuality dashboard HTML from reviews.json."
    )
    parser.add_argument(
        "--reviews-json",
        dest="reviews_json",
        help="Override input reviews JSON path.",
    )
    parser.add_argument(
        "--out",
        dest="out_html",
        help="Override output dashboard HTML path.",
    )
    parser.add_argument(
        "--index-out",
        dest="index_html",
        help="Optional mirrored output path for dashboard/index.html.",
    )
    return parser.parse_args(argv)


ARGS = parse_args() if __name__ == "__main__" else parse_args([])
reviews_path = Path(ARGS.reviews_json or os.environ.get("EVIDENCE_QUALITY_REVIEWS_JSON", DEFAULT_REVIEWS_JSON))
out_path = Path(ARGS.out_html or os.environ.get("EVIDENCE_QUALITY_DASHBOARD_HTML", DEFAULT_DASHBOARD_HTML))
default_index_out = out_path.parent / "dashboard" / "index.html" if out_path.name == "dashboard.html" else DEFAULT_DASHBOARD_INDEX_HTML
index_out_path = Path(
    ARGS.index_html
    or os.environ.get("EVIDENCE_QUALITY_DASHBOARD_INDEX_HTML", default_index_out)
)

# Load compact JSON
with open(reviews_path, encoding='utf-8') as f:
    data = json.load(f)

json_data = json.dumps(data, separators=(',', ':'))
review_count = len(data)
review_word = "review" if review_count == 1 else "reviews"
dimension_count = len(DIMENSION_LABELS)
dimension_list = ", ".join(DIMENSION_LABELS)
dashboard_subtitle = (
    f"{review_count} Cochrane {review_word} graded across "
    f"{dimension_count} dimensions: {dimension_list}"
)
embedded_data_summary = (
    f"{review_count} Cochrane {review_word}, {dimension_count} dimensions, nested JSON"
)

# Safety: verify no </script> in JSON
assert '</script>' not in json_data.lower(), "ERROR: JSON contains </script> — cannot embed safely"
print(f"JSON: {len(data)} reviews, {len(json_data)} bytes, no </script> found")

# ============================================================
# BUILD THE HTML
# ============================================================
html_parts = []

html_parts.append(r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Evidence Quality Dashboard</title>
<style>
/* ===== CSS CUSTOM PROPERTIES ===== */
:root {
  --bg: #f8f9fa;
  --bg-card: #ffffff;
  --bg-header: #1e3a5f;
  --text: #1f2937;
  --text-muted: #6b7280;
  --border: #e5e7eb;
  --accent: #2563eb;
  --accent-hover: #1d4ed8;
  --radius: 8px;
  --shadow: 0 1px 3px rgba(0,0,0,0.10), 0 1px 2px rgba(0,0,0,0.06);
  --shadow-md: 0 4px 6px rgba(0,0,0,0.07), 0 2px 4px rgba(0,0,0,0.05);
}

[data-theme="dark"] {
  --bg: #111827;
  --bg-card: #1f2937;
  --bg-header: #0f172a;
  --text: #f9fafb;
  --text-muted: #9ca3af;
  --border: #374151;
  --accent: #3b82f6;
  --accent-hover: #60a5fa;
  --shadow: 0 1px 3px rgba(0,0,0,0.40), 0 1px 2px rgba(0,0,0,0.30);
  --shadow-md: 0 4px 6px rgba(0,0,0,0.30), 0 2px 4px rgba(0,0,0,0.20);
}

/* ===== RESET ===== */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  background: var(--bg);
  color: var(--text);
  font-size: 14px;
  line-height: 1.5;
  transition: background 0.2s, color 0.2s;
}

/* ===== HEADER ===== */
.site-header {
  background: var(--bg-header);
  color: #fff;
  padding: 1.25rem 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.75rem;
}
.header-title h1 { font-size: 1.4rem; font-weight: 700; letter-spacing: -0.01em; }
.header-title p  { font-size: 0.85rem; opacity: 0.75; margin-top: 0.15rem; }

.btn-theme {
  background: rgba(255,255,255,0.12);
  color: #fff;
  border: 1px solid rgba(255,255,255,0.25);
  border-radius: var(--radius);
  padding: 0.4rem 0.85rem;
  font-size: 0.82rem;
  cursor: pointer;
  transition: background 0.15s;
  white-space: nowrap;
}
.btn-theme:hover { background: rgba(255,255,255,0.22); }

/* ===== LAYOUT ===== */
.main-container {
  max-width: 1300px;
  margin: 0 auto;
  padding: 1.5rem 1.5rem 3rem;
}

/* ===== CARD ===== */
.card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 1.25rem;
  margin-bottom: 1.25rem;
}
.card-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text);
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
}

/* ===== BUTTONS ===== */
.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.45rem 1rem;
  border-radius: var(--radius);
  font-size: 0.82rem;
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: background 0.15s, opacity 0.15s;
}
.btn-primary { background: var(--accent); color: #fff; }
.btn-primary:hover { background: var(--accent-hover); }
.btn-secondary { background: var(--bg-card); color: var(--text); border: 1px solid var(--border); }
.btn-secondary:hover { background: var(--bg); }

/* ===== FILTER BAR ===== */
.filter-bar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem 1.5rem;
  margin-bottom: 1.25rem;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 0.85rem 1.1rem;
  box-shadow: var(--shadow);
}
.filter-group { display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; }
.filter-label {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--text-muted);
  white-space: nowrap;
}
.radio-group { display: flex; gap: 0.25rem; }
.radio-btn {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.3rem 0.7rem;
  border-radius: 6px;
  font-size: 0.8rem;
  cursor: pointer;
  border: 1px solid var(--border);
  background: var(--bg);
  color: var(--text);
  transition: background 0.12s, border-color 0.12s;
}
.radio-btn input[type="radio"] { accent-color: var(--accent); margin: 0; }
.radio-btn:has(input:checked) { background: var(--accent); color: #fff; border-color: var(--accent); }
.radio-btn:has(input:checked) input[type="radio"] { accent-color: #fff; }

.search-input {
  padding: 0.35rem 0.75rem;
  border: 1px solid var(--border);
  border-radius: 6px;
  background: var(--bg);
  color: var(--text);
  font-size: 0.82rem;
  width: 220px;
  outline: none;
  transition: border-color 0.15s;
}
.search-input:focus { border-color: var(--accent); }

/* ===== STAT GRID ===== */
.stat-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-bottom: 1.25rem;
}
.stat-box {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 1.1rem 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}
.stat-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.stat-value { font-size: 2rem; font-weight: 700; color: var(--text); line-height: 1.1; }
.stat-sub   { font-size: 0.75rem; color: var(--text-muted); }

/* ===== GRADE COLORS ===== */
.grade-a { color: #198754; }
.grade-b { color: #2563eb; }
.grade-c { color: #b45309; }
.grade-d { color: #dc3545; }

.grade-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 26px;
  height: 26px;
  border-radius: 50%;
  font-size: 0.78rem;
  font-weight: 700;
  color: #fff;
}
.grade-badge.grade-a { background: #198754; }
.grade-badge.grade-b { background: #2563eb; }
.grade-badge.grade-c { background: #d97706; }
.grade-badge.grade-d { background: #dc3545; }
.grade-badge.grade-i { background: #6b7280; }

/* ===== COMPONENT STATUS ===== */
.component-good     { color: #198754; font-weight: 600; }
.component-moderate { color: #b45309; font-weight: 600; }
.component-poor     { color: #dc3545; font-weight: 600; }
.component-missing  { color: var(--text-muted); font-style: italic; }

/* ===== TABLE ===== */
.table-wrapper { overflow-x: auto; -webkit-overflow-scrolling: touch; }

.sortable-table { width: 100%; border-collapse: collapse; font-size: 0.82rem; }
.sortable-table th {
  background: var(--bg);
  border: 1px solid var(--border);
  padding: 0.55rem 0.75rem;
  text-align: left;
  font-weight: 600;
  font-size: 0.78rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.03em;
  cursor: pointer;
  white-space: nowrap;
  user-select: none;
  position: sticky;
  top: 0;
  z-index: 1;
}
.sortable-table th:hover    { color: var(--text); background: var(--border); }
.sortable-table th.sort-asc::after  { content: " \25B2"; font-size: 0.65rem; }
.sortable-table th.sort-desc::after { content: " \25BC"; font-size: 0.65rem; }
.sortable-table td {
  border: 1px solid var(--border);
  padding: 0.45rem 0.75rem;
  color: var(--text);
  vertical-align: middle;
}
.sortable-table tbody tr { cursor: pointer; transition: background 0.1s; }
.sortable-table tbody tr:hover  { background: var(--bg); }
.sortable-table tbody tr:focus  { outline: 2px solid var(--accent); outline-offset: -2px; }

/* ===== ACCORDION DETAIL PANEL ===== */
.detail-panel td { background: var(--bg); padding: 1rem 1.25rem; }
.detail-panel-inner { padding: 0.5rem 0; }
.detail-header {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-muted);
  margin-bottom: 0.75rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--border);
}
.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 0.75rem;
}
.detail-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 0.85rem 1rem;
}
.detail-card-title {
  font-size: 0.78rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--text-muted);
  margin-bottom: 0.6rem;
}
.detail-card-missing {
  background: var(--bg);
  border: 1px dashed var(--border);
  border-radius: var(--radius);
  color: var(--text-muted);
  font-style: italic;
  font-size: 0.82rem;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 80px;
  padding: 1rem;
}

/* ===== COMPARE TABLE ===== */
.compare-table { width: 100%; font-size: 0.8rem; border-collapse: collapse; }
.compare-table td { padding: 0.2rem 0.4rem; border-bottom: 1px solid var(--border); }
.compare-table td:first-child { color: var(--text-muted); width: 55%; }
.compare-table td:last-child  { font-weight: 600; text-align: right; }
.compare-table tr:last-child td { border-bottom: none; }

/* ===== HEATMAP LEGEND ===== */
.heatmap-legend { display: flex; gap: 1.25rem; margin-top: 0.6rem; font-size: 0.78rem; flex-wrap: wrap; }
.legend-item    { display: flex; align-items: center; gap: 0.35rem; color: var(--text-muted); }
.legend-swatch  { width: 14px; height: 14px; border-radius: 2px; display: inline-block; flex-shrink: 0; }

/* ===== EXPORT ROW ===== */
.export-row { display: flex; gap: 0.75rem; align-items: center; flex-wrap: wrap; margin-top: 0.75rem; }

/* ===== FOOTER ===== */
.site-footer {
  background: var(--bg-card);
  border-top: 1px solid var(--border);
  color: var(--text-muted);
  text-align: center;
  padding: 1rem 2rem;
  font-size: 0.78rem;
}

/* ===== SCORE BAR ===== */
.score-cell { white-space: nowrap; }
.score-bar-bg {
  display: inline-block; width: 60px; height: 6px;
  background: var(--border); border-radius: 3px;
  vertical-align: middle; margin-left: 4px; overflow: hidden;
}
.score-bar-fill { height: 100%; border-radius: 3px; background: var(--accent); }

/* ===== RESPONSIVE ===== */
@media (max-width: 768px) {
  .site-header     { padding: 1rem; }
  .main-container  { padding: 1rem 0.75rem 2rem; }
  .stat-grid       { grid-template-columns: repeat(2, 1fr); gap: 0.75rem; }
  .filter-bar      { gap: 0.75rem 1rem; }
  .search-input    { width: 160px; }
  .sortable-table  { font-size: 0.75rem; }
  .sortable-table th, .sortable-table td { padding: 0.4rem 0.5rem; }
  .detail-grid     { grid-template-columns: 1fr; }
}
@media (max-width: 480px) {
  .stat-grid   { grid-template-columns: 1fr 1fr; }
  .stat-value  { font-size: 1.5rem; }
  .radio-group { flex-wrap: wrap; }
}

/* ===== PRINT ===== */
@media print {
  .site-header .btn-theme,
  .filter-bar,
  .export-row,
  .btn        { display: none !important; }
  body        { background: #fff; color: #000; }
  .card       { box-shadow: none; border-color: #ccc; }
  .site-footer{ border-top: 1px solid #ccc; }
}

/* SVG max-width */
#gradeChartContainer svg,
#heatmapContainer svg { max-width: 100%; height: auto; }
</style>
</head>
<body>

<!-- ===== HEADER ===== -->
<header class="site-header">
  <div class="header-title">
    <h1>Evidence Quality Dashboard</h1>
    <p>403 Cochrane reviews graded across 4 dimensions: Fragility, Bias, Prediction, ORB</p>
  </div>
  <button class="btn-theme" id="themeToggle" onclick="toggleTheme()" aria-label="Toggle dark mode">
    <span id="themeIcon">&#9790;</span> Dark Mode
  </button>
</header>

<!-- ===== MAIN CONTENT ===== -->
<main class="main-container">

  <!-- FILTER BAR -->
  <div class="filter-bar" role="search">
    <div class="filter-group">
      <span class="filter-label">Completeness:</span>
      <div class="radio-group" role="radiogroup" aria-label="Completeness filter">
        <label class="radio-btn">
          <input type="radio" name="completeness" value="all" checked onchange="applyFilters()">
          All (403)
        </label>
        <label class="radio-btn">
          <input type="radio" name="completeness" value="4" onchange="applyFilters()">
          Complete 4/4
        </label>
        <label class="radio-btn">
          <input type="radio" name="completeness" value="3" onchange="applyFilters()">
          Bias missing 3/4
        </label>
      </div>
    </div>
    <div class="filter-group">
      <span class="filter-label">Search:</span>
      <input
        type="search"
        id="searchInput"
        class="search-input"
        placeholder="Review ID or name..."
        aria-label="Search reviews"
        oninput="debounceSearch()"
      >
    </div>
  </div>

  <!-- SUMMARY CARDS -->
  <div class="stat-grid" id="summaryCards">
    <div class="stat-box">
      <div class="stat-label">Total Reviews</div>
      <div class="stat-value" id="statTotal">&mdash;</div>
      <div class="stat-sub">matching current filters</div>
    </div>
    <div class="stat-box">
      <div class="stat-label">Mean Quality Score</div>
      <div class="stat-value" id="statMean">&mdash;</div>
      <div class="stat-sub">weighted across components</div>
    </div>
    <div class="stat-box">
      <div class="stat-label">Grade A or B</div>
      <div class="stat-value" id="statAB">&mdash;</div>
      <div class="stat-sub">high-quality evidence</div>
    </div>
    <div class="stat-box">
      <div class="stat-label">Fully Complete</div>
      <div class="stat-value" id="statComplete">&mdash;</div>
      <div class="stat-sub">all 4 components scored</div>
    </div>
  </div>

  <!-- GRADE DISTRIBUTION CHART -->
  <div class="card">
    <div class="card-title">Grade Distribution</div>
    <div id="gradeChartContainer">
      <p style="color:var(--text-muted);font-size:0.85rem;">Loading chart...</p>
    </div>
    <div class="export-row">
      <button class="btn btn-secondary" onclick="exportCSV()" title="Download filtered reviews as CSV">
        &#8681; Export CSV
      </button>
      <button class="btn btn-secondary" onclick="exportPNG()" title="Download grade chart as PNG">
        &#8681; Export PNG
      </button>
      <span style="font-size:0.78rem;color:var(--text-muted);" id="exportCount"></span>
    </div>
  </div>

  <!-- COMPONENT HEATMAP -->
  <div class="card">
    <div class="card-title">Component Quality Heatmap</div>
    <div id="heatmapContainer">
      <p style="color:var(--text-muted);font-size:0.85rem;">Loading heatmap...</p>
    </div>
    <div class="heatmap-legend" id="heatmapLegend"></div>
  </div>

  <!-- TABLE -->
  <div class="card">
    <div class="card-title">
      Review Table
      <span id="tableCount" style="font-weight:400;color:var(--text-muted);font-size:0.82rem;"></span>
    </div>
    <div class="table-wrapper" id="tableContainer">
      <p style="color:var(--text-muted);font-size:0.85rem;">Loading table...</p>
    </div>
  </div>

</main>

<!-- FOOTER -->
<footer class="site-footer">
  Evidence Quality Dashboard v1.0 &mdash; Browser-based, no data leaves your device.
</footer>

<script>
/* ================================================================
   EMBEDDED DATA
   Source: C:\EvidenceQuality\data\reviews.json
   403 Cochrane reviews, 4 dimensions, nested JSON
================================================================ */
var REVIEWS = """)

# Insert the JSON data directly
html_parts.append(json_data)

html_parts.append(r""";

/* ================================================================
   UTILITY FUNCTIONS
================================================================ */
function escapeHtml(s) {
  if (s == null) return '';
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function fmt(val, decimals) {
  if (val == null || val === '') return '\u2014';
  var n = parseFloat(val);
  if (!isFinite(n)) return '\u2014';
  return decimals != null ? n.toFixed(decimals) : String(n);
}

/* ================================================================
   DARK MODE TOGGLE
================================================================ */
function toggleTheme() {
  var isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  var next = isDark ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', next);
  try { localStorage.setItem('eqd_theme', next); } catch(e) {}
  document.getElementById('themeIcon').textContent = next === 'dark' ? '\u2600' : '\u263E';
  if (filtered.length > 0) {
    renderGradeChart(filtered);
    renderHeatmap(filtered);
  }
}

(function initTheme() {
  var saved;
  try { saved = localStorage.getItem('eqd_theme'); } catch(e) {}
  if (saved === 'dark' || (!saved && window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    document.documentElement.setAttribute('data-theme', 'dark');
  }
  var isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  var icon = document.getElementById('themeIcon');
  if (icon) icon.textContent = isDark ? '\u2600' : '\u263E';
})();

/* ================================================================
   GLOBAL STATE
================================================================ */
var filtered = [];
var sortCol = 'quality_score';
var sortAsc = false;
var searchTimer = null;

/* ================================================================
   DEBOUNCED SEARCH
================================================================ */
function debounceSearch() {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(applyFilters, 200);
}

/* ================================================================
   APPLY FILTERS
   Reads completeness radio + text search.
   Rebuilds `filtered`, then calls all 4 render functions.
================================================================ */
function applyFilters() {
  var filterVal = document.querySelector('input[name="completeness"]:checked').value;
  var searchVal = document.getElementById('searchInput').value.toLowerCase().trim();

  filtered = REVIEWS.filter(function(r) {
    if (filterVal === '4' && r.completeness !== 4) return false;
    if (filterVal === '3' && r.completeness !== 3) return false;
    if (searchVal) {
      var rid  = (r.review_id || '').toLowerCase();
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

/* ================================================================
   RENDER SUMMARY CARDS
================================================================ */
function renderSummary(data) {
  var n = data.length;
  var scored = data.filter(function(r) { return r.quality_score !== null; });
  var meanScore = scored.length > 0
    ? (scored.reduce(function(s, r) { return s + r.quality_score; }, 0) / scored.length).toFixed(1)
    : '\u2014';
  var nAB  = data.filter(function(r) { return r.quality_grade === 'A' || r.quality_grade === 'B'; }).length;
  var pctAB = n > 0 ? (nAB / n * 100).toFixed(0) + '%' : '0%';
  var n4   = data.filter(function(r) { return r.completeness === 4; }).length;
  var pct4 = n > 0 ? (n4 / n * 100).toFixed(0) + '%' : '0%';

  document.getElementById('statTotal').textContent    = n;
  document.getElementById('statMean').textContent     = meanScore !== '\u2014' ? meanScore + '/100' : '\u2014';
  document.getElementById('statAB').textContent       = pctAB;
  document.getElementById('statComplete').textContent = pct4;

  var ec = document.getElementById('exportCount');
  if (ec) ec.textContent = n + ' reviews in current filter';
}

/* ================================================================
   RENDER GRADE CHART (SVG horizontal bars, stacked by completeness)
================================================================ */
function renderGradeChart(data) {
  var container = document.getElementById('gradeChartContainer');
  if (!container) return;
  if (data.length === 0) {
    container.innerHTML = '<p style="color:var(--text-muted);padding:1rem 0;">No data matches current filters.</p>';
    return;
  }

  var grades  = ['A', 'B', 'C', 'D'];
  var colors  = { A: '#198754', B: '#2563eb', C: '#d97706', D: '#dc3545' };
  var lColors = { A: '#6ec98d', B: '#7da8f0', C: '#fde68a', D: '#f08080' };

  var counts = {};
  grades.forEach(function(g) { counts[g] = { c4: 0, c3: 0 }; });
  data.forEach(function(r) {
    if (counts[r.quality_grade]) {
      if (r.completeness === 4) counts[r.quality_grade].c4++;
      else                       counts[r.quality_grade].c3++;
    }
  });

  var maxCount = Math.max.apply(null, grades.map(function(g) {
    return counts[g].c4 + counts[g].c3;
  }));
  if (maxCount === 0) maxCount = 1;

  var barH = 38, gap = 10, ml = 78, mr = 90, mt = 20, mb = 28;
  var chartW = 580;
  var barArea = chartW - ml - mr;
  var svgH = mt + grades.length * (barH + gap) - gap + mb;

  var isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  var textClr  = isDark ? '#e5e7eb' : '#1f2937';
  var mutedClr = isDark ? '#6b7280' : '#9ca3af';
  var emptyClr = isDark ? '#374151' : '#e5e7eb';

  var out = [];
  out.push('<svg width="' + chartW + '" height="' + svgH + '" viewBox="0 0 ' + chartW + ' ' + svgH + '" role="img" aria-label="Grade distribution bar chart" style="max-width:100%;height:auto;">');

  grades.forEach(function(g, i) {
    var y = mt + i * (barH + gap);
    var total = counts[g].c4 + counts[g].c3;
    var w4 = counts[g].c4 / maxCount * barArea;
    var w3 = counts[g].c3 / maxCount * barArea;
    var wUsed = w4 + w3;

    out.push('<text x="' + (ml - 8) + '" y="' + (y + barH / 2 + 5) + '" text-anchor="end" font-size="13" font-weight="700" fill="' + colors[g] + '">Grade ' + g + '</text>');

    if (wUsed < barArea) {
      var ex = (ml + wUsed).toFixed(1);
      var ew = (barArea - wUsed).toFixed(1);
      var ey = (y + barH * 0.35).toFixed(1);
      var eh = (barH * 0.3).toFixed(1);
      out.push('<rect x="' + ex + '" y="' + ey + '" width="' + ew + '" height="' + eh + '" fill="' + emptyClr + '" rx="2"/>');
    }
    if (w4 > 0) {
      out.push('<rect x="' + ml + '" y="' + y + '" width="' + w4.toFixed(1) + '" height="' + barH + '" fill="' + colors[g] + '" rx="3"/>');
    }
    if (w3 > 0) {
      out.push('<rect x="' + (ml + w4).toFixed(1) + '" y="' + y + '" width="' + w3.toFixed(1) + '" height="' + barH + '" fill="' + lColors[g] + '" rx="3"/>');
    }
    var pct = data.length > 0 ? (total / data.length * 100).toFixed(0) : 0;
    out.push('<text x="' + (ml + wUsed + 8).toFixed(1) + '" y="' + (y + barH / 2 + 5) + '" font-size="12" fill="' + textClr + '">' + total + ' <tspan fill="' + mutedClr + '">(' + pct + '%)</tspan></text>');
  });

  var ly = svgH - 12;
  out.push('<rect x="' + ml + '" y="' + ly + '" width="11" height="11" fill="#4b5563" rx="2"/>');
  out.push('<text x="' + (ml + 15) + '" y="' + (ly + 9) + '" font-size="10" fill="' + mutedClr + '">4/4 complete</text>');
  out.push('<rect x="' + (ml + 100) + '" y="' + ly + '" width="11" height="11" fill="#9ca3af" rx="2" opacity="0.7"/>');
  out.push('<text x="' + (ml + 115) + '" y="' + (ly + 9) + '" font-size="10" fill="' + mutedClr + '">3/4 (bias missing)</text>');

  out.push('</svg>');
  container.innerHTML = out.join('');
}

/* ================================================================
   RENDER HEATMAP
================================================================ */
function renderHeatmap(data) {
  var container = document.getElementById('heatmapContainer');
  var legend    = document.getElementById('heatmapLegend');
  if (!container) return;
  if (data.length === 0) {
    container.innerHTML = '';
    if (legend) legend.innerHTML = '';
    return;
  }

  var sorted = data.slice().sort(function(a, b) {
    return (b.quality_score || 0) - (a.quality_score || 0);
  });

  var cols      = ['fragility', 'bias', 'prediction', 'orb'];
  var colLabels = ['Fragility',  'Bias', 'Prediction', 'ORB'];
  var ml = 16, mt = 28, colW = 100, gap = 3;
  var totalW = ml + cols.length * (colW + gap) - gap;
  var rowH   = Math.max(1.5, Math.min(5, 600 / sorted.length));
  var totalH = mt + sorted.length * rowH + 4;

  var isDark    = document.documentElement.getAttribute('data-theme') === 'dark';
  var textClr   = isDark ? '#e5e7eb' : '#374151';
  var goodColor = isDark ? '#22c55e' : '#198754';
  var modColor  = isDark ? '#eab308' : '#d97706';
  var poorColor = isDark ? '#ef4444' : '#dc3545';
  var missColor = isDark ? '#374151' : '#d1d5db';

  function componentScore(r, col) {
    if (col === 'fragility') {
      return (r.fragility && r.fragility.robustness_score != null) ? r.fragility.robustness_score : null;
    }
    if (col === 'bias') {
      if (!r.bias) return null;
      var bm = { 'Clean': 100, 'Suspected': 60, 'Confirmed': 20, 'Discordant': 40 };
      var v = bm[r.bias.bias_class];
      return v != null ? v : null;
    }
    if (col === 'prediction') {
      if (!r.prediction) return null;
      var pm = { 'CONCORDANT_SIG': 100, 'CONCORDANT_NS': 60, 'FALSE_REASSURANCE': 20 };
      var pv = pm[r.prediction.discordance];
      return pv != null ? pv : null;
    }
    if (col === 'orb') {
      if (!r.orb || r.orb.orb_score == null) return null;
      return 100 - r.orb.orb_score;
    }
    return null;
  }

  function cellColor(score) {
    if (score === null) return missColor;
    if (score >= 80)   return goodColor;
    if (score >= 40)   return modColor;
    return poorColor;
  }

  var out = [];
  out.push('<svg width="' + totalW + '" height="' + Math.ceil(totalH) + '" viewBox="0 0 ' + totalW + ' ' + Math.ceil(totalH) + '" role="img" aria-label="Component quality heatmap" style="max-width:100%;height:auto;">');

  cols.forEach(function(col, ci) {
    var x = ml + ci * (colW + gap) + colW / 2;
    out.push('<text x="' + x.toFixed(1) + '" y="' + (mt - 6) + '" text-anchor="middle" font-size="11" font-weight="600" fill="' + textClr + '">' + colLabels[ci] + '</text>');
  });

  sorted.forEach(function(r, ri) {
    var y = mt + ri * rowH;
    cols.forEach(function(col, ci) {
      var x = ml + ci * (colW + gap);
      var score = componentScore(r, col);
      out.push('<rect x="' + x.toFixed(1) + '" y="' + y.toFixed(2) + '" width="' + colW + '" height="' + rowH.toFixed(2) + '" fill="' + cellColor(score) + '"/>');
    });
  });

  out.push('</svg>');
  container.innerHTML = out.join('');

  if (legend) {
    legend.innerHTML =
      '<span class="legend-item"><span class="legend-swatch" style="background:' + goodColor + '"></span> Good (&ge;80)</span>' +
      '<span class="legend-item"><span class="legend-swatch" style="background:' + modColor  + '"></span> Moderate (40&ndash;79)</span>' +
      '<span class="legend-item"><span class="legend-swatch" style="background:' + poorColor + '"></span> Poor (&lt;40)</span>' +
      '<span class="legend-item"><span class="legend-swatch" style="background:' + missColor + ';border:1px solid #9ca3af;"></span> Missing</span>';
  }
}

/* ================================================================
   RENDER TABLE (sortable stub, full sort in Task 6)
================================================================ */
function renderTable(data) {
  var container = document.getElementById('tableContainer');
  var countEl   = document.getElementById('tableCount');
  if (!container) return;
  if (countEl) countEl.textContent = '(' + data.length + ' reviews)';

  if (data.length === 0) {
    container.innerHTML = '<p style="color:var(--text-muted);padding:1rem 0;">No reviews match current filters.</p>';
    return;
  }

  var html = [];
  html.push('<table class="sortable-table"><thead><tr>');
  html.push('<th>Review ID</th>');
  html.push('<th>Name</th>');
  html.push('<th style="text-align:center;">k</th>');
  html.push('<th style="text-align:center;">Complete</th>');
  html.push('<th>Score</th>');
  html.push('<th>Grade</th>');
  html.push('</tr></thead><tbody>');

  data.forEach(function(r, idx) {
    var gl = (r.quality_grade || 'I').toLowerCase();
    var gc = 'grade-' + (gl === 'insufficient' ? 'i' : gl);
    html.push('<tr data-idx="' + idx + '" tabindex="0" role="button" aria-expanded="false" onclick="toggleDetail(' + idx + ')" onkeydown="handleRowKey(event,' + idx + ')">');
    html.push('<td>' + escapeHtml(r.review_id) + '</td>');
    html.push('<td style="max-width:260px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" title="' + escapeHtml(r.analysis_name) + '">' + escapeHtml(r.analysis_name) + '</td>');
    html.push('<td style="text-align:center;">' + (r.k != null ? r.k : '\u2014') + '</td>');
    html.push('<td style="text-align:center;">' + r.completeness + '/4</td>');
    html.push('<td class="score-cell">' + (r.quality_score != null ? r.quality_score.toFixed(1) : '\u2014') + (r.quality_score != null ? '<span class="score-bar-bg"><span class="score-bar-fill" style="width:' + r.quality_score + '%"></span></span>' : '') + '</td>');
    html.push('<td><span class="grade-badge ' + gc + '">' + escapeHtml(r.quality_grade || 'I') + '</span></td>');
    html.push('</tr>');
  });

  html.push('</tbody></table>');
  container.innerHTML = html.join('');
}

/* ================================================================
   ACCORDION DETAIL PANELS
================================================================ */
function toggleDetail(idx) {
  var existingPanel = document.getElementById('detail-' + idx);
  if (existingPanel) {
    existingPanel.remove();
    var row = document.querySelector('[data-idx="' + idx + '"]');
    if (row) row.setAttribute('aria-expanded', 'false');
    return;
  }
  var open = document.querySelectorAll('.detail-panel');
  open.forEach(function(p) { p.remove(); });
  document.querySelectorAll('[data-idx]').forEach(function(r) { r.setAttribute('aria-expanded', 'false'); });

  var r   = filtered[idx];
  var row = document.querySelector('[data-idx="' + idx + '"]');
  if (!row || !r) return;
  row.setAttribute('aria-expanded', 'true');

  var panel = document.createElement('tr');
  panel.id = 'detail-' + idx;
  panel.className = 'detail-panel';
  var td = document.createElement('td');
  td.colSpan = 6;
  td.innerHTML = renderDetailContent(r);
  panel.appendChild(td);
  row.after(panel);
}

function handleRowKey(e, idx) {
  if (e.key === 'Enter' || e.key === ' ') {
    e.preventDefault();
    toggleDetail(idx);
  }
}

function renderDetailContent(r) {
  var h = [];
  h.push('<div class="detail-panel-inner">');
  h.push('<div class="detail-header">' + escapeHtml(r.review_id) + (r.review_doi ? ' &mdash; doi:' + escapeHtml(r.review_doi) : '') + '</div>');
  h.push('<div class="detail-grid">');

  // Fragility
  h.push('<div class="detail-card"><div class="detail-card-title">Fragility</div>');
  if (r.fragility) {
    h.push('<table class="compare-table">');
    h.push('<tr><td>Robustness score</td><td><strong>' + fmt(r.fragility.robustness_score, 1) + '</strong></td></tr>');
    h.push('<tr><td>Classification</td><td>' + escapeHtml(r.fragility.classification) + '</td></tr>');
    h.push('<tr><td>Top dimension</td><td>' + escapeHtml(r.fragility.top_dimension) + '</td></tr>');
    h.push('<tr><td>Frac significant</td><td>' + fmt(r.fragility.frac_significant, 2) + '</td></tr>');
    h.push('<tr><td>Frac reversed</td><td>' + fmt(r.fragility.frac_reversed, 2) + '</td></tr>');
    h.push('</table>');
  } else {
    h.push('<div class="detail-card-missing">Data not available for this review</div>');
  }
  h.push('</div>');

  // Bias
  h.push('<div class="detail-card"><div class="detail-card-title">Bias</div>');
  if (r.bias) {
    h.push('<table class="compare-table">');
    h.push('<tr><td>Bias class</td><td>' + escapeHtml(r.bias.bias_class) + '</td></tr>');
    h.push('<tr><td>Methods detected</td><td>' + (r.bias.n_detect != null ? r.bias.n_detect + '/8' : '\u2014') + '</td></tr>');
    h.push('<tr><td>Egger p-value</td><td>' + fmt(r.bias.egger_p, 4) + (r.bias.egger_sig ? ' *' : '') + '</td></tr>');
    h.push('<tr><td>Trim-fill k0</td><td>' + fmt(r.bias.tf_k0, 0) + '</td></tr>');
    h.push('<tr><td>PET-PEESE (&theta;)</td><td>' + fmt(r.bias.petpeese_theta, 3) + ' (' + escapeHtml(r.bias.petpeese_method) + ')</td></tr>');
    h.push('</table>');
  } else {
    h.push('<div class="detail-card-missing">Data not available for this review</div>');
  }
  h.push('</div>');

  // Prediction
  h.push('<div class="detail-card"><div class="detail-card-title">Prediction</div>');
  if (r.prediction) {
    h.push('<table class="compare-table">');
    h.push('<tr><td>Discordance</td><td>' + escapeHtml(r.prediction.discordance) + '</td></tr>');
    h.push('<tr><td>PI/CI ratio</td><td>' + fmt(r.prediction.pi_ci_ratio, 2) + '</td></tr>');
    h.push('<tr><td>tau&sup2;</td><td>' + fmt(r.prediction.tau2, 3) + '</td></tr>');
    h.push('<tr><td>I&sup2;</td><td>' + fmt(r.prediction.I2, 1) + '%</td></tr>');
    h.push('<tr><td>95% CI</td><td>[' + fmt(r.prediction.ci_lo, 3) + ', ' + fmt(r.prediction.ci_hi, 3) + ']</td></tr>');
    h.push('<tr><td>95% PI</td><td>[' + fmt(r.prediction.pi_lo, 3) + ', ' + fmt(r.prediction.pi_hi, 3) + ']</td></tr>');
    h.push('</table>');
  } else {
    h.push('<div class="detail-card-missing">Data not available for this review</div>');
  }
  h.push('</div>');

  // ORB
  h.push('<div class="detail-card"><div class="detail-card-title">ORB</div>');
  if (r.orb) {
    h.push('<table class="compare-table">');
    h.push('<tr><td>ORB class</td><td>' + escapeHtml(r.orb.orb_class) + '</td></tr>');
    h.push('<tr><td>ORB score</td><td>' + fmt(r.orb.orb_score, 1) + '</td></tr>');
    h.push('<tr><td>Excess significance</td><td>' + fmt(r.orb.excess_significance, 2) + '</td></tr>');
    h.push('<tr><td>Outlier ratio</td><td>' + fmt(r.orb.outlier_ratio, 2) + '</td></tr>');
    h.push('</table>');
  } else {
    h.push('<div class="detail-card-missing">Data not available for this review</div>');
  }
  h.push('</div>');

  h.push('</div>'); // detail-grid
  h.push('</div>'); // detail-panel-inner
  return h.join('');
}

/* ================================================================
   EXPORT FUNCTIONS
================================================================ */
function exportCSV() {
  var headers = ['review_id','analysis_name','k','completeness','quality_score','quality_grade',
    'fragility_class','robustness_score','bias_class','n_detect',
    'discordance','pi_ci_ratio','orb_class','orb_score'];
  var rows = [headers.join(',')];
  filtered.forEach(function(r) {
    rows.push([
      r.review_id,
      '"' + (r.analysis_name || '').replace(/"/g, '""') + '"',
      r.k != null ? r.k : '',
      r.completeness,
      r.quality_score != null ? r.quality_score : '',
      r.quality_grade,
      r.fragility ? r.fragility.classification : '',
      r.fragility ? (r.fragility.robustness_score != null ? r.fragility.robustness_score : '') : '',
      r.bias ? r.bias.bias_class : '',
      r.bias ? (r.bias.n_detect != null ? r.bias.n_detect : '') : '',
      r.prediction ? r.prediction.discordance : '',
      r.prediction ? (r.prediction.pi_ci_ratio != null ? r.prediction.pi_ci_ratio : '') : '',
      r.orb ? r.orb.orb_class : '',
      r.orb ? (r.orb.orb_score != null ? r.orb.orb_score : '') : ''
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

function exportPNG() {
  var svg = document.querySelector('#gradeChartContainer svg');
  if (!svg) { alert('Chart not available.'); return; }
  var svgData = new XMLSerializer().serializeToString(svg);
  var canvas  = document.createElement('canvas');
  var bb = svg.getBoundingClientRect();
  canvas.width  = Math.max(bb.width  || 580, 580);
  canvas.height = Math.max(bb.height || 200, 200);
  var ctx = canvas.getContext('2d');
  var svgBlob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' });
  var url = URL.createObjectURL(svgBlob);
  var img = new Image();
  img.onload = function() {
    ctx.fillStyle = document.documentElement.getAttribute('data-theme') === 'dark' ? '#1f2937' : '#ffffff';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(img, 0, 0);
    URL.revokeObjectURL(url);
    var pngUrl = canvas.toDataURL('image/png');
    var a = document.createElement('a');
    a.href = pngUrl;
    a.download = 'evidence_quality_grade_chart.png';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };
  img.src = url;
}

/* ================================================================
   INITIALISE
================================================================ */
document.addEventListener('DOMContentLoaded', function() {
  applyFilters();
});
</script>
</body>
</html>""")

html = ''.join(html_parts)
html = html.replace(
    "403 Cochrane reviews graded across 4 dimensions: Fragility, Bias, Prediction, ORB",
    dashboard_subtitle,
)
html = html.replace(r"Source: C:\EvidenceQuality\data\reviews.json", f"Source: {reviews_path}")
html = html.replace(
    "403 Cochrane reviews, 4 dimensions, nested JSON",
    embedded_data_summary,
)

# ============================================================
# SAFETY CHECKS
# ============================================================
print("\n--- Safety checks ---")

# 1) DIV balance (HTML portion only, not script)
html_only = re.sub(r'<script[\s\S]*?</script\s*>', '', html, flags=re.IGNORECASE)
opens  = len(re.findall(r'<div[\s>]', html_only))
closes = len(re.findall(r'</div>', html_only))
print(f"DIV balance: opens={opens}, closes={closes}, balanced={opens == closes}")
assert opens == closes, f"IMBALANCED DIVS: opens={opens} closes={closes}"

# 2) No </script> inside script blocks
script_blocks = re.findall(r'<script(?:\s[^>]*)?>[\s\S]*?</script\s*>', html, flags=re.IGNORECASE)
for i, blk in enumerate(script_blocks):
    inner_start = blk.index('>') + 1
    inner_end   = blk.rfind('</')
    inner = blk[inner_start:inner_end]
    bad = re.findall(r'</script', inner, re.IGNORECASE)
    print(f"Script block {i}: {len(inner):,} chars, spurious </script>: {len(bad)}")
    assert not bad, f"SCRIPT BLOCK {i} contains </script> !"

# 3) File size sanity
print(f"\nTotal HTML: {len(html):,} bytes ({len(html)//1024} KB)")

# Write it
out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text(html, encoding='utf-8')
print(f"\nWritten: {out_path}")

if index_out_path != out_path:
    index_out_path.parent.mkdir(parents=True, exist_ok=True)
    index_out_path.write_text(html, encoding='utf-8')
    print(f"Mirrored: {index_out_path}")

print("SUCCESS")
