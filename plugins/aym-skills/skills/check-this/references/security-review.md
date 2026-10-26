# Security review

Every review, verify and slice check includes this pass. It looks for ways the change could leak a secret, let an outsider in, or be turned against its user. It is a read-and-run review of the change, not a penetration test.

## Scope it to the change

1. List what the change touches from the diff: code, configuration, workflows, dependencies, prompts and skill text, docs.
2. Docs or prose only, with no commands, links to run or settings: one line, "Security: docs-only change; checked for secrets and links, none found."
3. Anything else: work through the checklist below for the changed files and anything they call or that calls them. Go wider only when a finding points there.

## Checklist

For each item, look at the changed code, then decide: finding, or clear.

1. **Secrets.** API keys, tokens, passwords, private keys or connection strings in code, config, tests, logs, fixtures or docs. Search the diff for key-shaped strings and for names such as `key`, `token`, `secret`, `password`. A secret read from an environment variable or secret store is fine; a default value that is a real secret is not.
2. **Injection.** Text from outside (a user, a file, a web page, an API, a model reply) built into a shell command, SQL query, file path, URL, HTML page, regular expression or `eval`. Safe forms: argument lists instead of a shell string, parameterized queries, path checks that resolve and stay inside a known folder, escaping by the output's own library.
3. **Access.** Logins, sessions and permission checks: a route or action with no check, a check on the client only, an ID from the request used to read someone else's record, tokens that never expire.
4. **Outside input.** Size, type and range checks on anything read from outside; uploads; deserializing untrusted data (`pickle`, `yaml.load` without a safe loader).
5. **Dependencies.** New or changed packages: are they the real package (spelling), pinned, maintained, and free of known holes? Run the project's audit command when one exists (`npm audit`, `pip-audit`); otherwise say it was not run.
6. **Data exposure.** Personal or private data in logs, error messages, analytics, URLs, public files or exports; debug output left on.
7. **Settings and permissions.** Workflow permissions wider than needed (`permissions: write-all`), secrets passed to untrusted pull requests, CORS open to every site, files or tokens readable by everyone, a tool given more access than its job needs.
8. **AI and agent risks.** Instructions hidden in files, pages or tool output that an agent would read and obey; an agent allowed to run commands, send messages or spend without a person's yes; model output used as code or as a command without checks.

## Record

Give each finding a location (file:line), a severity, what an attacker or accident could do, the evidence, and a fix:

- **blocker:** a secret in the repository, or a hole an outsider can use now. Never "consider".
- **should fix:** a real weakness that needs one more condition to be used.
- **consider:** hardening.

When nothing is found, say "Security: no findings" and list the checklist items you covered and the commands you ran. Never write "not covered" or point to another reviewer for the basics; a deeper audit (a threat model of the whole system, attacking a running service) is a separate request, and the report says it was not part of this check.

A secret found in the history is a blocker even after it is deleted from the code: the fix is to revoke the secret and issue a new one, then clean the history if the repository is public. Never print the secret's value in the report; name the file, line and kind.

## Second opinions

These are optional and never replace the checklist:

- Claude Code: `/security-review` on the branch.
- Codex: `/review`, asked to focus on security.
- On a public GitHub repository: the repository's code scanning and secret scanning alerts (Security tab).

Quote any that ran and say which did not.
