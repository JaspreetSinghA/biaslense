# Lessons

## 2026-11-20 — Check where an ID column comes from before counting with it
- **Mistake:** Reported "22 matched Claude pairs" by counting overlaps in `rater_data_combined.csv`.
  That file's `prompt_id` was a row number (loader bug), so the count was meaningless. Real overlap: 16.
- **Rule:** Before computing overlaps or joins, confirm the key is a real identifier (sample a few values;
  for rater data they look like `COMP_DIRECT_01`, not `0, 1, 2`). Cross-check one count against raw files.
- **Rule:** Loaders must fail loudly when an identifier is missing. Never fall back to row order.
