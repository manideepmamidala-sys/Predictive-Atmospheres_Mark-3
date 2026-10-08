# Model selection

Use Codex for all workflow roles:

| Role | Model | Reasoning effort |
| --- | --- | --- |
| Operator / orchestration | gpt-6-astra | max |
| Intake / planning / architecture | gpt-6-astra | high |
| Implementation / debugging | gpt-6-sol | high |
| Independent review | gpt-6-astra | xhigh |
| Documentation / hydrate | gpt-6-sol | high |
| Ship | gpt-6-luna | medium |
| PR feedback handling | gpt-6-sol | high |

Favor thorough reasoning; control cost primarily through model selection.
Do not use Terra or GPT-5.6 variants. Other providers, including Gemini,
require an explicit user override.

Delegate when supported and worthwhile. Use a fresh agent for independent
review. Explicitly set the model and reasoning effort through the active
tool’s supported options, verify actual dispatch settings, and report
the selected model and effort.

Escalate when workers are stuck or findings remain unresolved. Do not
silently change routing. Honor explicit user model and effort overrides.

This policy supersedes conflicting workflow or skill defaults, including
earlier “Astra for planning only” or “Luna always xhigh” policies.

If a requested model, effort, or routing mechanism is unavailable, report
the limitation instead of silently substituting. Instructions alone
cannot change the main session’s model or an already-running worker.
