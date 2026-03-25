# The Cochrane Quality Concordance: a multi-dimensional analysis of evidence reliability across 403 systematic reviews

**Mahmood Ahmad**

Royal Free Hospital, London, UK

Correspondence to: Mahmood Ahmad, Royal Free Hospital, London NW3 2QG, UK; mahmood.ahmad2@nhs.net

ORCID: 0009-0003-7781-4478

**Word count:** 3,420

---

## Abstract

**Objective:** To determine the extent to which six distinct dimensions of evidence quality in Cochrane systematic reviews are concordant or orthogonal, and to quantify the prevalence of multi-dimensional quality failures.

**Design:** Cross-sectional methodological study applying a multi-dimensional quality profiling framework to Cochrane reviews.

**Data sources:** 403 Cochrane systematic reviews of interventions, each assessed across six quality dimensions: fragility (multiverse robustness), publication bias (eight-method forensic concordance), prediction gap (prediction interval/confidence interval discordance), outcome reporting bias (excess significance and composite endpoint assessment), reproducibility (open-access coverage for computational verification), and study overlap (Jaccard-based non-independence).

**Results:** The six quality dimensions were largely orthogonal (mean absolute off-diagonal Spearman |rho| = 0.179). The strongest pairwise correlation was between publication bias and outcome reporting bias (rho = 0.468, p < 0.05); the weakest was between reproducibility and study overlap (rho = -0.006, p > 0.05). Of the 15 pairwise correlations, 11 reached statistical significance but all remained below 0.5, confirming that each dimension captures substantively different information. Composite quality grades assigned were: A (high quality) 44 reviews (10.9%), B (adequate) 279 (69.2%), C (concerning) 77 (19.1%), and D (seriously deficient) 3 (0.7%). The mean composite score was 68.5 (median 69.2) on a 0-100 scale. Cross-dimensional vulnerability was common: 30.5% (123/403) of reviews were simultaneously fragile and showed evidence of publication bias, while 10.4% (42/403) exhibited both false reassurance from narrow confidence intervals and high outcome reporting bias.

**Conclusions:** Quality dimensions in systematic reviews are substantially non-redundant. A review that passes one quality check may fail another entirely. Current approaches that assess evidence quality uni-dimensionally provide an incomplete and potentially misleading picture. Multi-dimensional quality profiling should be adopted to give decision-makers a realistic understanding of where the evidence is strong and where it is vulnerable.

---

## What this study adds

**What is already known on this topic**
- Systematic review quality is typically assessed using single tools (AMSTAR-2, GRADE, Risk of Bias) that produce a unitary rating
- Individual methodological threats (fragility, publication bias, reporting bias) have been studied in isolation
- It is unknown whether reviews that perform well on one quality dimension also perform well on others

**What this study adds**
- Six quality dimensions in 403 Cochrane reviews are largely orthogonal (mean |rho| = 0.179), meaning each captures different information
- Nearly one-third (30.5%) of reviews are simultaneously fragile and show publication bias -- a "double jeopardy" that single-dimension assessment would miss
- Only 10.9% of reviews achieve high-quality grades across all six dimensions simultaneously
- Multi-dimensional quality profiling reveals hidden vulnerabilities that unitary quality ratings obscure

---

## Introduction

Cochrane systematic reviews represent the most trusted source of synthesised clinical evidence and directly inform clinical guidelines, health technology assessments, and treatment decisions worldwide.[1,2] The methodological rigour of these reviews is conventionally assessed through tools such as AMSTAR-2,[3] the GRADE framework,[4] and the Cochrane Risk of Bias tool,[5] each of which produces a summary judgement along a single axis or a small number of correlated axes. An implicit assumption underlying current practice is that quality is substantially unitary: a well-conducted review is expected to perform well across multiple methodological criteria, and a single summary rating is therefore considered adequate for decision-making.

This assumption has not been empirically tested at scale. Individual methodological threats to systematic review validity -- statistical fragility,[6,7] publication bias,[8,9] prediction interval discordance,[10] outcome reporting bias,[11,12] limited reproducibility,[13] and primary study overlap[14,15] -- have each been studied in isolation. However, the critical question for users of evidence is not merely whether any single threat is present, but whether these threats are correlated (implying that a single quality check suffices) or orthogonal (implying that multiple independent checks are needed).

If the dimensions are largely independent, then a review that receives a favourable assessment on one dimension may harbour serious vulnerabilities on another -- a scenario we term "hidden quality discordance." The clinical consequence is that decision-makers relying on a single quality metric may be falsely reassured about the reliability of the evidence base.

This study addresses this gap by simultaneously measuring six quality dimensions across 403 Cochrane systematic reviews and characterising their pairwise concordance structure. Our primary hypothesis is that these dimensions are substantively non-redundant, implying that multi-dimensional quality profiling provides information that uni-dimensional assessment cannot.

## Methods

### Study design and review selection

We conducted a cross-sectional methodological study of Cochrane systematic reviews of interventions. Reviews were sampled from the Cochrane Database of Systematic Reviews to achieve broad clinical coverage. Inclusion criteria were: (a) review of a therapeutic intervention, (b) at least one meta-analysis with a binary or continuous primary outcome, (c) sufficient data reported to compute all six quality dimensions, and (d) published or last substantively updated within the preceding five years. Diagnostic test accuracy reviews, overviews of reviews, and protocols were excluded. A total of 403 reviews met all criteria.

### Quality dimensions

Each review was assessed on six dimensions, scored from 0 (worst) to 100 (best) and calibrated against established methodological standards.

**Dimension 1: Fragility (multiverse robustness).** We quantified the sensitivity of the primary meta-analytic result to analytic decisions using a multiverse framework.[6,16] For each review, we varied the effect measure (risk ratio, odds ratio, risk difference where applicable), the pooling model (fixed-effect, random-effects DerSimonian-Laird, REML, Paule-Mandel), the inclusion/exclusion of borderline studies, and the handling of zero cells. The fragility score reflects the proportion of plausible analytic specifications under which the qualitative conclusion (significant vs non-significant, direction of effect) remains unchanged. Reviews where the conclusion was robust across more than 90% of specifications scored above 80; those where fewer than 50% of specifications preserved the conclusion scored below 30.

**Dimension 2: Publication bias (eight-method forensic concordance).** Publication bias was assessed using a concordance approach across eight established methods: Egger's regression,[8] Begg's rank correlation,[17] the trim-and-fill method,[18] the p-curve,[19] the p-uniform method,[20] selection model approaches,[21] the excess significance test,[22] and visual funnel plot assessment. Each method returned a binary signal (bias detected/not detected), and the dimension score was derived from the proportion of methods that did not detect bias, weighted by each method's known sensitivity profile. A review scored 100 if no method detected bias and 0 if all eight methods detected bias.

**Dimension 3: Prediction gap (PI/CI discordance).** The prediction interval (PI) quantifies the range within which the true effect in a future study is expected to fall, incorporating between-study heterogeneity.[10,23] Where the 95% confidence interval excludes the null but the 95% prediction interval includes it, a "prediction gap" exists -- the summary effect is statistically significant but may not generalise. The dimension score was inversely proportional to the magnitude of discordance between PI and CI, with maximum penalty applied when the PI crossed the null while the CI did not.

**Dimension 4: Outcome reporting bias (ORB).** We assessed two components: the excess significance test,[22] which compares the observed proportion of statistically significant results with the expected proportion given the pooled effect size and individual study power, and a composite endpoint assessment that flags reviews where the primary outcome was a composite or surrogate that may inflate apparent treatment effects.[11,12] The dimension score combined both components.

**Dimension 5: Reproducibility (open-access coverage).** Computational reproducibility requires access to primary study data and reports.[13,24] We quantified the proportion of primary studies in each review that were available through open-access channels (PubMed Central, DOAJ-indexed journals, institutional repositories, or preprint servers). Reviews where all included studies were openly accessible scored 100; those where fewer than 30% were accessible scored below 30. This dimension does not assess whether anyone has attempted reproduction but rather whether the raw materials for reproduction are available.

**Dimension 6: Study overlap (Jaccard non-independence).** When systematic reviews share primary studies, their conclusions are not statistically independent.[14,15] We computed pairwise Jaccard similarity coefficients between each review and all other reviews in the sample addressing overlapping clinical questions. The dimension score was inversely proportional to the maximum Jaccard overlap observed, penalising reviews that shared a high proportion of their evidence base with other reviews on the same topic.

### Composite scoring and grading

Composite scores were computed as the unweighted mean of the six dimension scores (range 0-100). Reviews were graded as: A (composite score >= 80; high quality across all dimensions), B (60-79; adequate with localised concerns), C (40-59; concerning with multiple vulnerabilities), or D (< 40; seriously deficient).

### Statistical analysis

Pairwise associations between the six dimensions were quantified using Spearman rank correlation coefficients (rho), with significance assessed at the two-sided alpha = 0.05 level. The overall redundancy of the six-dimensional space was summarised by the mean absolute off-diagonal correlation (mean |rho|). Cross-dimensional vulnerability was assessed by computing the proportion of reviews flagged on multiple dimensions simultaneously. All analyses were conducted using reproducible computational pipelines with fixed random seeds.

## Results

### Overall quality distribution

Among 403 Cochrane reviews, 44 (10.9%) received a grade of A, 279 (69.2%) grade B, 77 (19.1%) grade C, and 3 (0.7%) grade D (Table 1). The mean composite score was 68.5 (SD 12.3; median 69.2; interquartile range 60.8-77.1). The distribution was unimodal and approximately normal, with a slight left skew driven by the small number of grade D reviews.

The majority of reviews (69.2%) fell into the B category, indicating adequate quality with localised vulnerabilities on one or two dimensions. Only approximately one in nine reviews (10.9%) achieved consistently high quality across all six dimensions, while one in five (19.1%) showed concerning multi-dimensional weakness.

### Concordance structure: the six dimensions are largely orthogonal

The Spearman correlation matrix (Table 2) revealed that the six quality dimensions were substantially non-redundant. The mean absolute off-diagonal correlation was 0.179, indicating that the dimensions share, on average, only approximately 3.2% of their variance (mean rho-squared approximately 0.032).

The strongest pairwise association was between publication bias and outcome reporting bias (rho = 0.468, p < 0.05). This moderate correlation is theoretically expected: mechanisms that suppress negative studies (publication bias) often co-occur with selective reporting of favourable outcomes within published studies (outcome reporting bias).[11] Nonetheless, the correlation was well below 0.7, confirming that these dimensions remain substantially non-redundant even where the theoretical overlap is greatest.

The weakest pairwise association was between reproducibility and study overlap (rho = -0.006, p > 0.05), indicating complete independence. Whether a review's primary studies are openly accessible bears no relation to whether those studies are shared with other reviews. Similarly, fragility showed near-zero correlation with both reproducibility (rho = -0.021) and study overlap (rho = 0.048), indicating that the statistical robustness of a meta-analytic result is unrelated to the openness or independence of its evidence base.

Of the 15 pairwise correlations, 11 reached statistical significance at the 0.05 level (Table 2). However, significance in a sample of 403 is expected for correlations as small as 0.10, and the key finding is the consistently small magnitude of the associations rather than their statistical significance. No pairwise correlation exceeded 0.5.

### Cross-dimensional vulnerability: the "double jeopardy" problem

Cross-tabulation of dimension-specific flags revealed substantial multi-dimensional vulnerability (Table 3). Among the 234 reviews flagged as fragile (fragility score below the threshold) and the 145 flagged for publication bias, 123 (30.5% of all reviews) were flagged on both dimensions simultaneously. This "double jeopardy" -- where a review's conclusion is both statistically fragile and potentially inflated by missing studies -- represents a particularly concerning pattern that would be invisible to any assessment examining either dimension alone.

Similarly, 42 reviews (10.4%) exhibited both false reassurance (narrow confidence intervals that masked a wide prediction interval, indicating limited generalisability) and high outcome reporting bias. In these reviews, the apparent precision of the summary effect may itself be an artefact of selective reporting.

The overall distribution of dimension-specific flags was: fragility 234/403 (58.1%), publication bias 145/403 (36.0%), false reassurance (prediction gap) 132/403 (32.8%), outcome reporting bias 65/403 (16.1%), with varying proportions for reproducibility and study overlap.

### Dimension-specific findings

The fragility dimension had the highest flag rate (58.1%), consistent with prior work showing that many meta-analytic conclusions are sensitive to the exclusion of a single study or a change in analytic model.[6,7] The prediction gap dimension was flagged in 32.8% of reviews, reinforcing the importance of routinely reporting prediction intervals alongside confidence intervals.[10,23]

Publication bias was detected in 36.0% of reviews by the eight-method concordance approach. The multi-method concordance requirement makes this a conservative estimate: a review was flagged only when multiple complementary methods agreed, reducing the false-positive rate inherent in any single test.

Outcome reporting bias (16.1%) was the least frequently flagged among the "bias" dimensions, though this likely reflects the difficulty of detecting selective reporting when the full set of planned outcomes is not always available for comparison.

## Discussion

### Principal findings

This study demonstrates that six dimensions of systematic review quality are largely orthogonal in 403 Cochrane reviews, with a mean absolute inter-dimension correlation of only 0.179. This finding has a direct and important implication: assessing evidence quality along a single dimension -- however well that dimension is measured -- provides an incomplete picture. A review that is robust to analytic perturbation (high fragility score) may nonetheless be compromised by publication bias, and a review with no detectable publication bias may produce a summary effect that does not generalise beyond the included studies (wide prediction interval). Only 10.9% of reviews achieved high quality across all six dimensions simultaneously, while 30.5% exhibited the "double jeopardy" of simultaneous fragility and publication bias.

### Comparison with existing quality frameworks

Existing quality assessment frameworks operate predominantly in a uni-dimensional or low-dimensional space. AMSTAR-2 evaluates the conduct of the review process itself (search strategy, study selection, data extraction) but does not directly assess the statistical properties of the result.[3] GRADE assesses certainty of evidence across five domains (risk of bias, inconsistency, indirectness, imprecision, publication bias), but these domains are combined into a single overall rating that collapses the multi-dimensional information.[4] The Cochrane Risk of Bias tool focuses on bias within individual studies rather than the synthesis-level properties we assess here.[5]

Our six dimensions complement rather than replace these frameworks. They assess the synthesised result -- the meta-analytic output that directly informs clinical decisions -- rather than the process of conducting the review. The low inter-dimension correlations suggest that adding these dimensions to existing quality assessments would provide genuinely new information.

### The strongest correlation: publication bias and outcome reporting bias

The moderate correlation between publication bias and outcome reporting bias (rho = 0.468) was the strongest observed and deserves interpretation. Publication bias operates at the study level (entire studies are missing from the evidence base), while outcome reporting bias operates within studies (unfavourable outcomes are selectively unreported or de-emphasised). That these two mechanisms are moderately correlated but far from identical suggests a shared upstream driver -- perhaps research environments where there is strong pressure to produce positive results -- that manifests through both pathways simultaneously but with sufficient independence that detecting one does not reliably predict the other.

This has practical implications for bias assessment. Current practice often treats detection of publication bias as a sufficient check for reporting-related threats. Our data suggest that a review showing no funnel plot asymmetry may still harbour substantial outcome reporting bias, and vice versa.

### The weakest correlations: reproducibility and overlap are independent threats

The near-zero correlations of reproducibility and study overlap with most other dimensions (and with each other; rho = -0.006) indicate that these represent genuinely distinct vulnerabilities. A review may be statistically robust, free of detectable bias, and generalisable -- yet still fail on reproducibility because its primary studies are behind paywalls, or on independence because its evidence base overlaps substantially with competing reviews.

These dimensions are particularly relevant for health technology assessment and guideline development, where decisions may depend on multiple reviews of overlapping evidence. If decision-makers are unaware that two "independent" reviews share 70% of their primary studies, they may double-count the evidence, leading to false confidence.[14,15]

### Implications for practice

We propose that systematic review quality be reported as a six-dimensional profile rather than a single grade. A radar chart (Figure 2) provides an intuitive visualisation: each axis represents one dimension, and the area of the resulting polygon reflects overall quality while its shape reveals the pattern of strengths and vulnerabilities. A review with a small, circular polygon is uniformly weak; one with a large, spiky polygon is strong on most dimensions but vulnerable on one or two.

For rapid screening, the composite grade (A through D) provides a useful summary, but the dimensional profile should always be available for users who need to understand where the evidence is most and least reliable. This is analogous to the move from a single "blood pressure is normal" statement to reporting systolic and diastolic values separately -- a loss of simplicity but a gain in clinical utility.

### Strengths and limitations

This study has several strengths. It is, to our knowledge, the first to simultaneously assess six quality dimensions across a large sample of Cochrane reviews and to characterise their concordance structure. The use of multiple methods per dimension (particularly the eight-method concordance approach for publication bias) reduces reliance on any single statistical test. The sample of 403 reviews provides adequate power to detect even small correlations.

Limitations should be acknowledged. First, the six dimensions are not exhaustive; other aspects of quality (such as the appropriateness of the clinical question, the completeness of the search, or the quality of individual study conduct) are not captured. Second, the reproducibility dimension assesses availability of open-access full text rather than actual computational reproduction, which would require substantially more resources. Third, the composite scoring uses equal weights for all six dimensions, which may not reflect the relative importance of each dimension for a given clinical decision. Fourth, while the sample is drawn from Cochrane reviews, results may not generalise to non-Cochrane systematic reviews, which typically have lower methodological standards.[2] Finally, some correlations, though statistically significant, are small in magnitude, and the clinical significance of the "double jeopardy" patterns requires further investigation through empirical studies linking multi-dimensional quality profiles to the accuracy of treatment effect estimates.

## Conclusions

Six dimensions of evidence quality in Cochrane systematic reviews are largely orthogonal, with a mean inter-dimension correlation of 0.179. This means that a review performing well on one dimension provides minimal assurance about its performance on others. Nearly one-third of reviews are simultaneously fragile and affected by publication bias -- a compound vulnerability invisible to any single quality check. Current uni-dimensional quality assessment should be supplemented with multi-dimensional profiling that makes the full pattern of strengths and vulnerabilities transparent to decision-makers.

---

## Tables

### Table 1. Distribution of composite quality grades across 403 Cochrane reviews

| Grade | Composite score range | n | % | Interpretation |
|-------|----------------------|---|---|----------------|
| A | >= 80 | 44 | 10.9 | High quality across all dimensions |
| B | 60-79 | 279 | 69.2 | Adequate with localised concerns |
| C | 40-59 | 77 | 19.1 | Concerning; multiple vulnerabilities |
| D | < 40 | 3 | 0.7 | Seriously deficient |
| **Total** | | **403** | **100.0** | |

Mean composite score: 68.5; median: 69.2.

### Table 2. Spearman rank correlation matrix for six quality dimensions (n = 403)

| | Fragility | Pub Bias | Pred Gap | ORB | Reproducibility | Overlap |
|---|---|---|---|---|---|---|
| **Fragility** | 1.000 | | | | | |
| **Pub Bias** | 0.303* | 1.000 | | | | |
| **Pred Gap** | 0.161* | 0.205* | 1.000 | | | |
| **ORB** | 0.191* | 0.468* | 0.376* | 1.000 | | |
| **Reproducibility** | -0.021 | 0.218* | 0.029 | 0.054 | 1.000 | |
| **Overlap** | 0.048 | 0.291* | 0.109* | 0.200* | -0.006 | 1.000 |

\* p < 0.05 (two-sided). Mean absolute off-diagonal |rho| = 0.179. Pub Bias = publication bias; Pred Gap = prediction gap; ORB = outcome reporting bias; Overlap = study overlap.

### Table 3. Cross-dimensional vulnerability: reviews flagged on multiple dimensions simultaneously

| Dimension combination | Reviews flagged on both | % of all reviews (N = 403) |
|---|---|---|
| Fragile AND publication bias detected | 123 | 30.5 |
| False reassurance (prediction gap) AND high ORB | 42 | 10.4 |

Individual dimension flag counts: fragility 234 (58.1%); publication bias 145 (36.0%); false reassurance 132 (32.8%); outcome reporting bias 65 (16.1%).

---

## Figure legends

**Figure 1.** Heatmap of Spearman rank correlations among six quality dimensions in 403 Cochrane reviews. Cells are coloured on a diverging scale from blue (negative correlation) through white (zero) to red (positive correlation). The mean absolute off-diagonal correlation is 0.179, indicating that the dimensions are largely orthogonal. The strongest correlation (0.468) is between publication bias and outcome reporting bias; the weakest (-0.006) is between reproducibility and study overlap. Asterisks denote correlations significant at p < 0.05.

**Figure 2.** Radar charts showing mean dimension scores by composite quality grade (A through D). Each axis represents one of the six quality dimensions (fragility, publication bias, prediction gap, outcome reporting bias, reproducibility, study overlap), scaled 0-100. Grade A reviews (n = 44) show a large, roughly circular polygon indicating uniformly high quality. Grade B reviews (n = 279) show a moderately sized polygon with one or two indentations indicating localised vulnerabilities. Grade C reviews (n = 77) show a small, irregular polygon. Grade D reviews (n = 3) show a small, collapsed polygon with multiple dimensions near zero. The contrasting shapes illustrate that quality failures are dimension-specific rather than uniform.

**Figure 3.** Proportional Venn diagram of "double jeopardy" overlap between fragility and publication bias. The left circle represents the 234 reviews flagged as fragile (58.1%); the right circle represents the 145 reviews with detected publication bias (36.0%). The intersection contains 123 reviews (30.5%) that are both fragile and biased -- a compound vulnerability that neither dimension alone would fully capture. The remaining 147 reviews (36.5%) were not flagged on either dimension. Reviews in the intersection are at highest risk of producing conclusions that are simultaneously unstable and inflated.

---

## References

1. Chandler J, Cumpston M, Li T, Page MJ, Welch VA, eds. *Cochrane Handbook for Systematic Reviews of Interventions*. Version 6.4. Cochrane, 2023.
2. Page MJ, Shamseer L, Altman DG, et al. Epidemiology and reporting characteristics of systematic reviews of biomedical research: a cross-sectional study. *PLoS Med* 2016;13:e1002028.
3. Shea BJ, Reeves BC, Wells G, et al. AMSTAR 2: a critical appraisal tool for systematic reviews that include randomised or non-randomised studies of healthcare interventions, or both. *BMJ* 2017;358:j4008.
4. Guyatt GH, Oxman AD, Vist GE, et al. GRADE: an emerging consensus on rating quality of evidence and strength of recommendations. *BMJ* 2008;336:924-6.
5. Sterne JAC, Savovic J, Page MJ, et al. RoB 2: a revised tool for assessing risk of bias in randomised trials. *BMJ* 2019;366:l4898.
6. Walsh M, Srinathan SK, McAuley DF, et al. The statistical significance of randomized controlled trial results is frequently fragile: a case for a Fragility Index. *J Clin Epidemiol* 2014;67:622-8.
7. Atal I, Porcher R, Boutron I, Ravaud P. The statistical significance of meta-analyses is frequently fragile: definition of a fragility index for meta-analyses. *J Clin Epidemiol* 2019;111:32-40.
8. Egger M, Davey Smith G, Schneider M, Minder C. Bias in meta-analysis detected by a simple, graphical test. *BMJ* 1997;315:629-34.
9. Sterne JAC, Sutton AJ, Ioannidis JPA, et al. Recommendations for examining and interpreting funnel plot asymmetry in meta-analyses of randomised controlled trials. *BMJ* 2011;343:d4002.
10. IntHout J, Ioannidis JPA, Rovers MM, Goeman JJ. Plea for routinely presenting prediction intervals in meta-analysis. *BMJ Open* 2016;6:e010247.
11. Dwan K, Gamble C, Williamson PR, Kirkham JJ; Reporting Bias Group. Systematic review of the empirical evidence of study publication bias and outcome reporting bias -- an updated review. *PLoS One* 2013;8:e66844.
12. Kirkham JJ, Dwan KM, Altman DG, et al. The impact of outcome reporting bias in randomised controlled trials on a cohort of systematic reviews. *BMJ* 2010;340:c365.
13. Hardwicke TE, Mathur MB, MacDonald K, et al. Data availability, reusability, and analytic reproducibility: evaluating the impact of a mandatory open data policy at the journal *Cognition*. *R Soc Open Sci* 2018;5:180448.
14. Pieper D, Antoine SL, Mathes T, Neugebauer EAM, Eikermann M. Systematic review finds overlapping reviews were not mentioned in every other overview. *J Clin Epidemiol* 2014;67:368-75.
15. Bougioukas KI, Liakos A, Tsapas A, Ntzani E, Haidich AB. Preferred reporting items for overviews of systematic reviews including harms checklist: PRIOR-harms. *BMC Med Res Methodol* 2018;18:73.
16. Steegen S, Tuerlinckx F, Gelman A, Vanpaemel W. Increasing transparency through a multiverse analysis. *Perspect Psychol Sci* 2016;11:702-12.
17. Begg CB, Mazumdar M. Operating characteristics of a rank correlation test for publication bias. *Biometrics* 1994;50:1088-101.
18. Duval S, Tweedie R. Trim and fill: a simple funnel-plot-based method of testing and adjusting for publication bias in meta-analysis. *Biometrics* 2000;56:455-63.
19. Simonsohn U, Nelson LD, Simmons JP. P-curve: a key to the file-drawer. *J Exp Psychol Gen* 2014;143:534-47.
20. van Aert RCM, Wicherts JM, van Assen MALM. Conducting meta-analyses based on p values: reservations and recommendations for applying p-uniform and p-curve. *Perspect Psychol Sci* 2016;11:713-29.
21. Vevea JL, Hedges LV. A general linear model for estimating effect size in the presence of publication bias. *Psychometrika* 1995;60:419-35.
22. Ioannidis JPA, Trikalinos TA. An exploratory test for an excess of significant findings. *Clin Trials* 2007;4:245-53.
23. Riley RD, Higgins JPT, Deeks JJ. Interpretation of random effects meta-analyses. *BMJ* 2011;342:d549.
24. Naudet F, Sakarovitch C, Janiaud P, et al. Data sharing and reanalysis of randomized controlled trials in leading biomedical journals with a full data sharing policy: survey of studies published in *The BMJ* and *PLOS Medicine*. *BMJ* 2018;360:k400.

---

## Declarations

**Funding:** None.

**Competing interests:** The author declares no competing interests.

**Ethical approval:** Not required (analysis of published data).

**Data sharing:** The dataset of quality scores for all 403 reviews and the analysis code will be deposited in a public repository upon acceptance.

**Transparency declaration:** The lead author affirms that the manuscript is an honest, accurate, and transparent account of the study being reported; that no important aspects of the study have been omitted; and that any discrepancies from the study as originally planned have been explained.

**Patient and public involvement:** No patients were involved in the design, conduct, or reporting of this research.

**Contributorship:** MA conceived the study, designed the quality profiling framework, conducted all analyses, and wrote the manuscript.

**Licence:** This manuscript is submitted under a CC BY 4.0 licence to permit unrestricted reuse with attribution.
