# CP-A — source cleanup and storage decision

**Status:** inventory and authorized current-tree deduplication completed 2026-10-10. **Owner approved deferring LFS and retaining ordinary Git on 2026-10-10** with “$fab-ff approve both and continue,” referring to CP-A and CP-Spec. No Git history rewrite, LFS tracking change, remote push, hosting account or purchase has occurred.

## Evidence and completed cleanup

[Source inventory](source-inventory.md) documents exact SHA-256 matches before removal. Canonical retained evidence comprises 160 raw CSVs (296,535,120 bytes), 7 metadata CSVs, 30 original room renders (150,805,079 bytes) and 116 historical images (67,811,155 bytes). `data/source-inventory.json` and `data/MANIFEST.sha256` now use those retained paths; the historical migration map stays at `docs/reports/migration-inventory.json`. Project duplicate removal covered 30 root room renders, 116 old frontend images, two root PDFs, two `docs/thesis/` PDF copies and the untracked InDesign ZIP, all after checksum and Windows-original checks. The untracked thesis DOCX remains because an exact Windows original was not located. Raw signals and unique scientific evidence remain.

Local disk sizes measured 2026-10-10: `data/raw/` 284 MiB, `data/renders/raw/` 144 MiB, `artifacts/results/` 48 MiB, `frontend/public/` 9.2 MiB, and `.git/` 391 MiB (`du -sh`, rounded). Current-tree deletions do not remove historical Git objects. The 40+ MiB detailed signal export is a derived research product, not an original recording; its published static delivery is a separate hosting-size concern.

## Current limits and practical alternatives

- [GitHub LFS billing](https://docs.github.com/en/billing/concepts/product-billing/git-lfs) states GitHub Free includes 10 GiB LFS storage and 10 GiB download bandwidth per billing cycle; each changed file version stores its full size, and Actions downloads use the owner's bandwidth. A $0 budget blocks overage rather than billing it. [GitHub file limits](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-git-large-file-storage) give 2 GiB maximum per file on Free and say Git LFS cannot serve GitHub Pages assets.
- `git lfs version` did not execute successfully in this environment; adoption requires installing/fixing that tool and adding an explicit fetch/checkout contract to local, CI and hosting workflows. LFS now would not shrink the existing 391 MiB Git history because the owner rejected history rewrite.
- [Cloudflare Pages Free limits](https://developers.cloudflare.com/pages/platform/limits/) currently list 500 builds/month, 20,000 files and a 25 MiB limit per static asset. Split or redesign any static research export above that limit before selecting this host. [Render Free](https://render.com/docs/free) web services spin down after 15 idle minutes and can take about a minute to wake, with an ephemeral filesystem. Its [deployment guide](https://render.com/docs/your-first-deploy) includes static frontend and web-service patterns; keep research exports static so sleep affects only live Studio actions. Actual account quotas and production behavior were not checked.

## Proposed choice for owner

**Approved: defer Git LFS migration for this revision** while keeping canonical original files tracked normally. The present 10 GiB nominal allowance can hold the current source size, but LFS introduces a broken-tool dependency and new bandwidth/hosting behavior without reducing historical clone size. Current `.gitattributes` and CI retrieval remain ordinary Git, with no LFS fetch contract. Revisit LFS only if measured clone/install costs or remote size limits become a concrete problem; at that time, migrate selected large originals in a dedicated reviewable change, with a CI and hosting fetch check and no history rewrite. Keep the owner's explicit no-history-rewrite decision as final.

At release planning, choose a frontend host after testing actual static asset sizes and an API host with a visible wake/offline state. No domain purchase is authorized by this checkpoint.
