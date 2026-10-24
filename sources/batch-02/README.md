# RMT Mimic Jules Batch 02 Sources

Private, curated CAD inputs for Jules review branches only. These files are not
production RMT assets and must not be copied into the runtime web bundle.

| Source | Intended site | Runtime inventory relation |
| --- | --- | --- |
| `ADMIRAL MARINA CLUB.dxf` | Admiral Marina Club | Not present in the current 152-floor runtime manifest. Identify only source-supported floor identities and report the discrepancy. |
| `TETUAN BIO TREE PHARMACEUTICAL.dxf` | Bio Tree | Reconcile against the five `BIO TREE` runtime candidates. |
| `UMB MIMIC.dxf` | UMB | Reconcile against the four `UMB-1` runtime candidates. |

Rules:

- CAD geometry is authoritative.
- Preserve walls, partitions, doors/openings, stairs, lifts/cores, major rooms,
  circulation, useful labels, and relative proportions.
- Remove only safe title blocks, dimensions, construction clutter, irrelevant
  hatching, and obsolete duplicate annotations.
- Never invent architecture, floor identities, labels, or device positions.
- Backgrounds contain architecture only. RMT runtime pins remain separate.
- Produce SVG, high-resolution PNG, metadata JSON, source/final comparison,
  review HTML, and deterministic QA evidence for each source-supported floor.
- Mark ambiguous identities or geometry `REVIEW_REQUIRED` and continue other
  independent floors.
- Do not modify approved UOB, Myamax, LTK, Hotel Bao Shu, or Avillion outputs.
