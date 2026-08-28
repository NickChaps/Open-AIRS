# Security policy

## Reporting a vulnerability

Do not disclose vulnerabilities, malicious pack behaviour, prompt-injection paths or secret exposure in a public issue. Use the repository's private security-advisory channel once the remote repository is available.

Until a public security contact is published, do not send sensitive production data or credentials with a report. A minimal reproduction using synthetic data is preferred.

## Security boundary

Rule packs and Agent Skills are executable governance inputs. Treat third-party packages as untrusted until their origin, licence, requested tools and bundled scripts have been reviewed.

The reference engine does not grant connector permissions. Permissions remain the responsibility of the host runtime.
