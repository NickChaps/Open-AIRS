# Contract review example

This synthetic example produces two matched clause gaps and one indeterminate
result. That distinction matters: ambiguous audit language does not become a
silent finding or a silent pass.

```bash
PYTHONPATH=src python -m air_framework assess \
  --inventory examples/contract-review/inventory.json \
  --pack packs/contract-review-example/1.0.0/pack.json \
  --target contract-cloud-demo
```
