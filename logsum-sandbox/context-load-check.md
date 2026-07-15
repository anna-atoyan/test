Summary of CLAUDE.md by section:

Project: Event Log Summarizer — tiny CLI that summarizes synthetic events.csv logs into human-readable reports.
Code conventions: Source code in src/, tests in tests/, data in data/.
Preferred tools: Python 3.11 standard library only; Ruff for linting; Pytest for testing.
Escalation gates: (1) Stop before adding external dependencies, (2) Use only synthetic test data, (3) Never overwrite spec.md after sign-off without explicit approval.