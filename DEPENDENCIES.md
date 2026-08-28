# Dependency policy

The reference engine has no third-party runtime dependency.

The source distribution uses one pinned build backend:

| Component | Version | Purpose | Provenance | Licence | Reviewed |
| --- | --- | --- | --- | --- | --- |
| Hatchling | 1.32.0 | Build Python wheel and source distribution | [PyPI](https://pypi.org/project/hatchling/1.32.0/) / PyPA | MIT | 2026-08-29 |

GitHub Actions are pinned to immutable commit hashes. Their tag and upstream
repository were checked before publication:

| Action | Release | Commit |
| --- | --- | --- |
| `actions/checkout` | 7.0.1 | `3d3c42e5aac5ba805825da76410c181273ba90b1` |
| `actions/setup-python` | 7.0.0 | `5fda3b95a4ea91299a34e894583c3862153e4b97` |

PyYAML may be used temporarily by maintainers to run the official Agent Skill
validator. It is not a framework dependency and is not installed by this
package.

Before adding a dependency, document why the standard library is insufficient,
verify the upstream project and licence, review its current security posture,
and pin or lock the selected version where practical.
