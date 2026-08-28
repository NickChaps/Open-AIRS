# Worked AI-governance example

All names and evidence are fictional. The graph demonstrates the distinction
between:

- a platform that exposes controls;
- a configured application that executes;
- a passive Agent Skill that contributes CV-screening instructions;
- a connector that makes outbound action possible;
- a concrete recruitment use that is the relevant legal composition.

Run:

```bash
PYTHONPATH=src python -m air_framework assess \
  --inventory examples/ai-governance/inventory.json \
  --pack packs/eu-ai-act/1.0.0/pack.json \
  --target use-recruiting-assistant
```

Then run the same target against `packs/eu-gdpr-ai/1.0.0/pack.json`. The two
packs answer different legal questions and may both match.
