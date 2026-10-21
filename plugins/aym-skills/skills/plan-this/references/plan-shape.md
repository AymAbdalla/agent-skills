# Plan shape

Use this when writing a plan document. Scale it to the work: a two-slice change can fit on one screen. Leave a section out only when it has nothing to say, and say so in one line. Flow and Approval are always required.

## Section list

```markdown
# <Feature> plan

Status: proposed, awaiting approval. Source of agreement: <spec path or decision record>.

## Goal
<One paragraph: the agreed behavior and who it serves.>

## Slices
| # | Slice | Surfaces | Change | Acceptance check | Blocked by |
| --- | --- | --- | --- | --- | --- |

## Dependencies
| Dependency | Needed by | Exists now? | Provider | If missing |
| --- | --- | --- | --- | --- |

## Verification
| Requirement | Check | Runs now? |
| --- | --- | --- |

## Risks, open decisions and fog
- Open decision: <choice> (needs <who>)
- Risk: <what could go wrong> -> <how the plan limits it>
- Fog: <later unknown>; revisit when <trigger>

## Flow
<Mermaid block>

## Approval
<What approving this plan authorizes; what stays outside it.>
```

## Slice rules

- A slice ends with something a person or a check can observe: a command output, a page, a stored record, a passing test that exercises public behavior.
- A slice that only adds a table, a type or a helper with nothing calling it is a layer, not a slice. Fold it into the first slice that uses it.
- Put the riskiest unknown early when it can change the rest of the plan.
- Split slices when one would be too large to finish and check in one sitting; do not split to reach a number.
- Name real blockers only. Two slices that could run in parallel should not be chained.
- Wide mechanical migrations (rename across many files, format change) may use expand, migrate, contract batches. State that choice.

## Dependencies

Real dependencies are things outside the code being written: an external API or webhook, an account or credential, a dataset, a CLI or service that must be installed, a teammate's decision, another feature. Check the repository and environment for each one. When a dependency is missing, the plan says who can provide it and what the check does until then, for example a recorded sample payload, a local stub with the real contract, or a check marked "cannot run until provisioned". A stub check does not prove the real integration.

Never write secret values into the plan. Name the environment variable or secret store instead.

## Mermaid guidance

- Use `flowchart TD` or `flowchart LR` with one node per slice and edges for real blockers.
- Add a node for each external dependency that gates a slice, styled or labeled so it stands out.
- Keep labels short and plain. Avoid characters that break Mermaid parsing in labels: quotes, parentheses inside unquoted labels, and semicolons.
- The diagram is editable source in the plan file, not an image.

## After approval

The approved plan is the record. Implementation reads it; it does not get rewritten to match the build. If the build reveals a material change, note the proposed change and ask the user before treating it as approved.
