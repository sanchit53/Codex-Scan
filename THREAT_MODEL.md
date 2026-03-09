# Threat Model – Vulnerable Flask Lab

## 1. System Overview
This repository contains a deliberately vulnerable Flask application (`app.py`) that exposes multiple HTTP routes with insecure patterns to support security testing and training.

### In-scope components
- Flask web app process and route handlers in `app.py`.
- In-memory SQLite database connection and user table.
- Local file access to `uploads/` via `/read_file`.
- Host OS command execution path exposed through `/ping`.
- Deserialization path exposed through `/load_profile`.

## 2. Security Objectives
1. Preserve confidentiality of credentials, local files, and sensitive process/runtime data.
2. Preserve integrity of backend command execution, template rendering, and database queries.
3. Preserve availability of the web service and host resources.
4. Prevent remote code execution from untrusted user input.

## 3. Assets
- Hardcoded app secret key used by Flask session framework.
- Hardcoded demo credentials and debug credentials in code.
- User records in the SQLite table.
- Files reachable via the `uploads/` path join.
- Host command execution environment used by `subprocess.check_output(..., shell=True)`.
- Application process memory and Python runtime state.

## 4. Actors
- **Unauthenticated external attacker**: Can send crafted requests to all routes.
- **Curious internal tester/student**: Can discover and chain vulnerabilities intentionally left in the lab.
- **Service operator/developer**: Runs app with `debug=True`, potentially exposing traceback and debugger risks.

## 5. Entry Points and Trust Boundaries
### Entry points
- `GET/POST /login`
- `GET /user_lookup?id=...`
- `GET /ping?host=...`
- `GET /hello?name=...`
- `GET /read_file?file=...`
- `GET /load_profile?data=...`
- `GET /debug_login`

### Trust boundaries
1. **Internet/client boundary**: All query/form parameters are untrusted.
2. **App ↔ database boundary**: SQL text is assembled from user input.
3. **App ↔ shell boundary**: User input enters shell command context.
4. **App ↔ filesystem boundary**: User input controls file path segments.
5. **App ↔ template engine boundary**: User input is interpreted by Jinja template rendering.
6. **App ↔ Python object boundary**: User input is decoded and deserialized.

## 6. Threat Analysis (STRIDE-style)

| Route / Component | Threat type(s) | Attack scenario | Impact | Risk |
|---|---|---|---|---|
| `/login` hardcoded credentials | Spoofing, Information disclosure | Attacker uses known static credentials (`admin/password123`) from UI hint and source | Unauthorized access to admin message; poor auth posture | Medium |
| Flask `secret_key` hardcoded | Spoofing/Tampering | If sessions are used later, attacker can forge signed cookies using known key | Session forgery, privilege abuse | High |
| `/user_lookup` SQL interpolation | Tampering, Information disclosure | `id=1 OR 1=1` manipulates query due to f-string SQL composition | Data exposure/modification potential | High |
| `/ping` shell command build | Elevation of privilege, Tampering, DoS | `host=127.0.0.1; cat /etc/passwd` executes arbitrary shell commands | Full command execution on host, service compromise | Critical |
| `/hello` dynamic template rendering | Information disclosure, EoP | SSTI payload (e.g., Jinja expression traversal) executes template internals | Potential server-side code/data access | High |
| `/read_file` path traversal | Information disclosure | `file=../../app.py` (or sensitive paths) escapes `uploads/` | Arbitrary file read | High |
| `/load_profile` pickle.loads on input | Elevation of privilege | Crafted pickle gadget executes code at deserialize time | Remote code execution | Critical |
| `/debug_login` credential logging | Information disclosure, Repudiation | Sensitive credentials printed to logs/stdout | Secret leakage and poor audit hygiene | Medium |
| `debug=True` runtime setting | Information disclosure, EoP | Production exposure of interactive debugger/stack traces | Environment leakage and possible code execution | High |

## 7. Abuse Cases / Attack Chains
1. **RCE chain A**: Use `/hello` SSTI to inspect environment, then pivot to command execution primitives if reachable.
2. **RCE chain B**: Use `/load_profile` insecure deserialization to gain immediate code execution.
3. **Data theft chain**: Enumerate files via `/read_file`, extract source and secrets, then leverage `/ping` for further host compromise.
4. **Recon + exploit**: Read `app.py`, discover all vulnerable routes and hardcoded credentials, automate exploitation.

## 8. Recommended Mitigations (Prioritized)

### Critical priority
- Replace `pickle.loads` with a safe format (`json`) and strict schema validation.
- Remove shell invocation; use `subprocess.run([...], shell=False)` with allowlisted hostname/IP validation.
- Disable debug mode in non-local environments (`debug=False`, environment-based config).

### High priority
- Parameterize SQL queries (`SELECT ... WHERE id = ?`) with numeric validation.
- Remove `render_template_string` with user-controlled template text; render static templates with escaped variables.
- Enforce canonical path validation for file access and restrict to a fixed directory allowlist.
- Move secrets and credentials to environment variables or secret manager; rotate exposed values.

### Medium priority
- Remove hardcoded/demo credentials from production paths.
- Eliminate credential logging and sanitize sensitive log fields.
- Add centralized input validation and consistent error handling.

### Defense-in-depth
- Add authentication/authorization checks where business actions exist.
- Add rate limiting and request size limits.
- Add application security tests (SAST + DAST) in CI.
- Add runtime hardening (least-privilege container/user, seccomp/AppArmor where applicable).

## 9. Validation Plan
- Unit tests for input validation and safe wrappers (SQL/path/command constraints).
- Security regression tests for SQLi, command injection, SSTI, traversal, and unsafe deserialization.
- Run static analysis (Bandit/Semgrep) and dependency scanning in CI.
- Perform manual penetration tests against each route before release.

## 10. Residual Risk
Because this repository is a vulnerability lab, some insecure behavior may be intentionally preserved for educational objectives. If deployed anywhere outside a local training environment, all Critical and High findings should be remediated before exposure.
