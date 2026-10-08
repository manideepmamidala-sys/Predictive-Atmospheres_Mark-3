# CI action resolution repair

Date: 2026-10-08. Both PR #4 `reproduce-and-test` jobs ([push run](https://github.com/manideepmamidala-sys/Predictive-Atmospheres_Mark-3/actions/runs/37800197329/job/113390027872), [pull request run](https://github.com/manideepmamidala-sys/Predictive-Atmospheres_Mark-3/actions/runs/37800226492/job/113390127639)) stopped during **Prepare all required actions**, before checkout or any project command. Each log says `Unable to resolve action astral-sh/setup-uv@v9, unable to find version v9`.

The [upstream `v9.0.0` tag](https://github.com/astral-sh/setup-uv/tree/v9.0.0) resolves to commit `c771a70e6277c0a99b617c7a806ffedaca235ff9`; the upstream `v9` Git ref returns HTTP 404. The [`v9.0.0` action manifest](https://github.com/astral-sh/setup-uv/blob/v9.0.0/action.yml) declares the existing `version` and `python-version` inputs and uses the Node 24 action runtime. CI now uses that immutable commit while retaining uv `0.5.9` and Python `3.11.11`.

Verification: `gh api repos/astral-sh/setup-uv/git/ref/tags/v9.0.0` returned the pinned commit; `gh api repos/astral-sh/setup-uv/git/ref/tags/v9` returned 404; both failed job logs had the same action-resolution error. The remaining workflow steps align with the frozen `make setup`, `make pipeline`, and `make lint test site` entry points and the documented Chromium installation. No later job step ran in the failed GitHub jobs. A new GitHub Actions result requires publishing this workflow change.

## Hosted verification

After publication at commit `2cc064edf37cfb1324f425b05f8aa9d1925b0001`, both replacement checks passed: [push run 37809242788](https://github.com/manideepmamidala-sys/Predictive-Atmospheres_Mark-3/actions/runs/37809242788) in 3m50s and [pull-request run 37809256892](https://github.com/manideepmamidala-sys/Predictive-Atmospheres_Mark-3/actions/runs/37809256892) in 3m6s. `gh pr checks 4` reported both `reproduce-and-test` checks as pass. These hosted runs completed source verification, research regeneration, lint/type/contract checks, backend/browser tests and the site build; the action-resolution failure is resolved.
