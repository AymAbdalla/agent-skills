# Interfaces and implementations

## MCP system

MCP connects an AI application's client to a server that exposes capabilities. Begin with the inspected configuration and version, not assumptions about current protocol support.

Trace the host/client role, server startup or endpoint, transport, advertised capabilities (tools, resources, prompts as present), selected input/schema, dispatch and available handler, response and errors. Identify authentication, data destinations, stored state and side effects from source; do not print secrets. Account for host permission policy separately from server validation.

An advertised schema explains the interface, not how the handler behaves. If only configuration and a tool listing are supplied, say **interface inspected; implementation unavailable**. Do not infer authentication enforcement, privacy, storage, argument validation, retries or safety from friendly names or descriptions. Also distinguish validation supplied by a library/framework from checks present in the handler; if the framework was not inspected, mark the dependency.

No live connection or operation is needed for source dissection. A fixture may supply explicit host/protocol behavior for analysis; identify it as fixture behavior, not a statement about every real MCP host. When explaining current protocol standards, consult the matching official version and cite it.

## Tool

Trace declared arguments to the implementation, outputs/errors, and any state or external effect. Find preconditions, who validates them, dependencies, permission boundaries, rerun behavior and cleanup. A function docstring can promise something its body does not enforce; compare both.

For an interface-only tool, describe only the visible contract and unknowns. For a script, inspect relevant code without running it. Parsing an input and checking permissions are separate steps. Error text is not proof the error can occur; show the condition in code or mark it as a documented expectation.

## Reuse

An instruction skill may teach or coordinate an operation; the tool still performs its machine work. A schema, handler or permission check usually belongs in code/configuration. A reusable user decision or evidence check may belong in instructions. Label a proposed implementation as ours, rather than attributing it to the studied target.
