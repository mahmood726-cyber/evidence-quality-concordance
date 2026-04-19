# E156 Protocol — `evidence-quality-concordance`

This repository is the source code and dashboard backing an E156 micro-paper on the [E156 Student Board](https://mahmood726-cyber.github.io/e156/students.html).

---

## `[53]` The Cochrane Quality Concordance: Six Orthogonal Dimensions of Evidence Reliability

**Type:** methods  |  ESTIMAND: Mean absolute pairwise correlation  
**Data:** Pairwise70 dataset (403 Cochrane reviews, 6 quality dimensions)

### 156-word body

Are six dimensions of evidence quality in systematic reviews correlated or orthogonal when measured simultaneously across Cochrane meta-analyses? We profiled 403 Cochrane reviews from Pairwise70 across fragility, publication bias, prediction gap, outcome reporting bias, reproducibility, and study overlap. Spearman rank correlations and composite quality grades were computed across all fifteen pairwise dimension combinations, with significance assessed after Bonferroni correction. The median composite score was 69.2 (95% CI 67.5-70.9), with the strongest pairwise correlation being publication bias versus outcome reporting bias at rho equals 0.468, confirming non-redundancy. Only 43 reviews earned a top-tier quality grade, while 30.5% exhibited simultaneous fragility and publication bias, a double jeopardy pattern invisible to single-dimension assessment tools. Evidence quality in systematic reviews is multidimensional and largely orthogonal, meaning that passing one quality check provides little assurance about performance on others. Nonetheless, this framework is limited to six computationally derived dimensions and does not incorporate clinical domain expertise or individual patient-level outcome data.

### Submission metadata

```
Corresponding author: Mahmood Ahmad <mahmood.ahmad2@nhs.net>
ORCID: 0000-0001-9107-3704
Affiliation: Tahir Heart Institute, Rabwah, Pakistan

Links:
  Code:      https://github.com/mahmood726-cyber/evidence-quality-concordance
  Protocol:  https://github.com/mahmood726-cyber/evidence-quality-concordance/blob/main/E156-PROTOCOL.md
  Dashboard: https://mahmood726-cyber.github.io/evidencequality/

References (topic pack: fragility index):
  1. Walsh M, Srinathan SK, McAuley DF, et al. 2014. The statistical significance of randomized controlled trial results is frequently fragile: a case for a Fragility Index. J Clin Epidemiol. 67(6):622-628. doi:10.1016/j.jclinepi.2013.10.019
  2. Atal I, Porcher R, Boutron I, Ravaud P. 2019. The statistical significance of meta-analyses is frequently fragile: definition of a fragility index for meta-analyses. J Clin Epidemiol. 111:32-40. doi:10.1016/j.jclinepi.2019.03.012

Data availability: No patient-level data used. Analysis derived exclusively
  from publicly available aggregate records. All source identifiers are in
  the protocol document linked above.

Ethics: Not required. Study uses only publicly available aggregate data; no
  human participants; no patient-identifiable information; no individual-
  participant data. No institutional review board approval sought or required
  under standard research-ethics guidelines for secondary methodological
  research on published literature.

Funding: None.

Competing interests: MA serves on the editorial board of Synthēsis (the
  target journal); MA had no role in editorial decisions on this
  manuscript, which was handled by an independent editor of the journal.

Author contributions (CRediT):
  [STUDENT REWRITER, first author] — Writing – original draft, Writing –
    review & editing, Validation.
  [SUPERVISING FACULTY, last/senior author] — Supervision, Validation,
    Writing – review & editing.
  Mahmood Ahmad (middle author, NOT first or last) — Conceptualization,
    Methodology, Software, Data curation, Formal analysis, Resources.

AI disclosure: Computational tooling (including AI-assisted coding via
  Claude Code [Anthropic]) was used to develop analysis scripts and assist
  with data extraction. The final manuscript was human-written, reviewed,
  and approved by the author; the submitted text is not AI-generated. All
  quantitative claims were verified against source data; cross-validation
  was performed where applicable. The author retains full responsibility for
  the final content.

Preprint: Not preprinted.

Reporting checklist: PRISMA 2020 (methods-paper variant — reports on review corpus).

Target journal: ◆ Synthēsis (https://www.synthesis-medicine.org/index.php/journal)
  Section: Methods Note — submit the 156-word E156 body verbatim as the main text.
  The journal caps main text at ≤400 words; E156's 156-word, 7-sentence
  contract sits well inside that ceiling. Do NOT pad to 400 — the
  micro-paper length is the point of the format.

Manuscript license: CC-BY-4.0.
Code license: MIT.

SUBMITTED: [ ]
```


---

_Auto-generated from the workbook by `C:/E156/scripts/create_missing_protocols.py`. If something is wrong, edit `rewrite-workbook.txt` and re-run the script — it will overwrite this file via the GitHub API._