# Code Quality

<!-- Optional coding standards consumed during apply and review.
     Projects opt in by creating this file. All sections are independently optional.
     Delete or leave empty any section that doesn't apply to your project. -->

## Principles

<!-- Positive coding standards to follow during implementation. -->

- Readability and maintainability over cleverness
- Follow existing project patterns unless there's compelling reason to deviate
- Prefer composition over inheritance
- Preserve source evidence and distinguish source values, derived features, and predictions
- Fit learned transforms only inside training folds; serialize preprocessing with the model
- Represent unavailable measurements and unsupported claims explicitly with reason codes

## Anti-Patterns

<!-- Patterns to avoid. Flagged during review with file:line references on violation. -->

- God functions (>50 lines without clear reason)
- Duplicating existing utilities instead of reusing them
- Magic strings or numbers without named constants
- Placeholder numerical research claims or default physiological replacements
- Parallel room-feature, Neuro-Score, or API request schemas

## Test Strategy

<!-- How tests relate to implementation.
     Values: test-alongside (default) | test-after | tdd -->

test-alongside
