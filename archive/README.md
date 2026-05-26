# Archive

Historical and development artifacts preserved for reference. Nothing here is part of the active application.

| Folder | Contents |
|--------|----------|
| `docs/` | Deployment notes, fix summaries, and ops docs from early development |
| `scripts/` | One-off scripts, demos, and walkthrough files used during development |
| `nested/` | The prior `biaslense/biaslense/` nested directory structure, including draft app variants and duplicate source tree |

## Reversibility

All files were moved here via `git mv` in a single commit. To restore any file:

```bash
# Restore a single file
git mv archive/<path>/<file> <original-path>/<file>

# Undo the entire cleanup commit
git revert <commit-hash>
```
