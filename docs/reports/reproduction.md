# Isolated source-snapshot reproduction

Date: 2026-10-08. After the second review rework, `scripts/reproduce_isolated.py` copied the final intended source and preserved data into a temporary local Git repository, made temporary snapshot commit `bba8663c320c30c0c5d3fb1f7885ad972ff95485`, and cloned it into `/tmp/pa-repro-aj5mflxs/clean-clone`. The project working tree remained uncommitted; this temporary commit was neither made nor pushed in the project repository. The clone was clean before execution.

The snapshot excluded `.git`, generated `artifacts/`, Python/Node environments, compiled/build caches, staged browser research output and test reports. It retained original recordings, metadata, renders, legacy images, PDFs, source manifest, amended analysis specification and decision record, frozen locks, frontend derivatives and final implementation. The clone had to generate its own numerical products and model artifact.

The host command was:

```sh
LD_LIBRARY_PATH=/tmp/pa-browser-libs/root/usr/lib/x86_64-linux-gnu python3 scripts/reproduce_isolated.py
```

The temporary library path supplies Chromium system libraries absent from this host; it is not a numerical-pipeline input. Inside the clone, frozen setup and `make all` passed in **249.2 seconds**. Source verification found the preserved inventory intact. The pipeline audited and processed 160 recordings, generated a `not_better_than_baseline` fitted model from 14 eligible Experiment 3 trials, wrote seven validated research exports and generated API contracts. Ruff passed, **80 backend tests passed**, and **25 browser tests passed with one intentional live-API skip** because the clean-clone `make all` run does not start a separate API server. The production Vite build passed. The full transcript is [reproduction-run.log](reproduction-run.log).

The comparison script recursively matched **all 15 generated JSON products** between this working tree and the clone, requiring matching keys, order, identifiers, nulls and nonnumeric values, with `abs_tol=rel_tol=1e-8` for finite floats. Model metadata matched after excluding only Git-repository identity/status fields and the model-file hash field, which was checked separately. The fitted `model.joblib` bytes were identical in this same-host run, SHA-256 `aecbb36c64b51b9c5b77cb20bf555b4a88b0ecea9f899c8b2d8536956fba59c0`. These checks establish same-host, same-lock numerical reproduction of the final rework, not cross-platform bitwise identity or physiological validity.

The prior re-review independently passed **26/26 browser tests** in CI mode against a fresh production-dependency API process, including live prediction and optimization. The clean-clone browser run above passes the unchanged frontend against newly staged products with the API offline. After the metadata-validation source edit, focused API tests cover health, meta, prediction and optimization with malformed public metadata; fresh-process artifact loading and the full **80/80** backend suite pass. The source snapshot occupied about **1.2 GB** including Git objects, and the cloned tree after setup/products/build about **2.0 GB**. No paid service, login, deployment or legacy processed/model cache was required.

The first second-cycle reproduction attempt stopped before tests because `/tmp` lacked space while cloning the temporary snapshot. Only the two disposable workspaces created by this worker were removed; the older independently reviewed snapshot was left untouched. The successful run above is the final evidence.
