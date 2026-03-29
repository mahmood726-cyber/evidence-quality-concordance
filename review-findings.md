## REVIEW CLEAN — All P0 and P1 fixed
## Multi-Persona Review: dashboard.html
### Date: 2026-03-25
### Summary: 2 P0 [FIXED], 5 P1 [FIXED], 4 P2 remaining

#### P0 -- Critical
- **P0-1** [FIXED] [Security]: CSV formula injection — added csvSafe() prepending ' to =+@\t\r prefixes
- **P0-2** [FIXED] [Accessibility]: Grade C badge contrast — changed to #664d03 on #fff3cd (~8:1 ratio)

#### P1 -- Important
- **P1-1** [FIXED] [SWE]: quality_score || 0 — replaced with null-safe ternary
- **P1-2** [FIXED] [SWE]: exportPNG error handler — added img.onerror with Blob URL revocation
- **P1-3** [FIXED] [SWE/UX]: Table sorting — implemented getSortValue + sortTable with click handlers and indicators
- **P1-4** [FIXED] [UX]: Accordion focus management — td gets tabindex=-1 and focus after expand
- **P1-5** [FIXED] [Domain]: ORB score inversion — added "(lower = less bias risk)" hint

#### P2 -- Minor (not fixed)
- **P2-1** No skip-to-content link
- **P2-2** Theme toggle uses inline onclick
- **P2-3** Grade cutoffs unvalidated against GRADE
- **P2-4** Scoring weights undocumented in UI
