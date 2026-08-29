<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# Condition language

The v0.1 condition language is deliberately small enough to audit by eye.

## Boolean operators

```json
{"all": [CONDITION, CONDITION]}
{"any": [CONDITION, CONDITION]}
{"not": CONDITION}
{"literal": true}
```

Evaluation uses three values: true, false and unknown. `all` and `any` use the
usual Kleene-style behaviour: a decisive false wins in `all`, a decisive true
wins in `any`, and otherwise an unknown remains unknown.

## Facts

```json
{"fact": {"key": "decision.solely_automated", "operator": "eq", "value": true}}
```

Supported operators are `eq`, `neq`, `in`, `not_in`, `contains`,
`contains_any`, `contains_all`, `truthy`, `exists`, `gt`, `gte`, `lt` and
`lte`.

## Related objects

```json
{
  "related": {
    "path": ["implemented_by", "loads_skill"],
    "object_types": ["skill"],
    "quantifier": "any",
    "where": {"fact": {"key": "capability.cv_screening", "operator": "eq", "value": true}}
  }
}
```

Each path step follows an outgoing relation by default. An incoming step is an
object such as `{"relation": "operated_by", "direction": "incoming"}`.
Quantifiers are `any`, `all` and `none`.
