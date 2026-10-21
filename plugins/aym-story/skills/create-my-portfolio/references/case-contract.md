# Case contract

Use this contract to verify claims and to check a draft before you report it.

## Proof labels

Give each claim the lowest label its evidence supports. A label describes one claim. Name each label in plain words in the draft, for example "tested on the build machine with synthetic inputs, not with real users".

| Label | The evidence shows | It does not show |
| --- | --- | --- |
| `stated only` | A person or an article says it. No artifact supports it. | That it is true. |
| `implemented` | The code, file or document exists. Nobody ran it. | That it works. |
| `local simulation` | It ran on the build machine against synthetic data, stand-ins or a simulated service. | Behavior against the real system, a real device or real users. |
| `implementation tested` | The real implementation ran its tests or checks on the build machine, and they passed. | Behavior on a target device, in production or with customers. |
| `device checked` | It ran on the physical target, such as a phone, a production host or a game engine. | Public availability or customer use. |
| `public service` | People outside the project can reach it now, at a named address. | That anyone used it or benefited. |
| `customer outcome` | A real user or customer used it, and a record shows the result. | Results for other customers. |

When the run used any stand-in, fake service or synthetic data, use `local simulation`, even if the real implementation ran. A pass in one label never implies a higher label. A successful local simulation cannot support a production, public or customer claim. Words such as "production-ready", "users love", "saves hours" or "faster" need evidence at the matching label.

## Claim status

| Status | Use when | How the draft handles it |
| --- | --- | --- |
| `verified` | Primary evidence supports the claim as written. | State it directly and cite the source. |
| `qualified` | Evidence supports part of the claim, or a lower label. | Narrow the wording to what the evidence shows. |
| `gap` | No evidence found, or the source conflicts. | Leave it out of the results. Name it under Limits as unverified, or drop it. |

An article, a README claim or a project summary is a lead. Trace it to the underlying record before you mark it `verified`.

## Numbers and comparisons

- Copy each count and measurement exactly. Name its source next to it in the evidence table.
- Keep different measures apart: sessions and requests, tests and cases, tokens and money, estimates and observations.
- Report failures, errors and unavailable checks with the passes. Do not drop a retained failure to make a cleaner story.
- A comparison needs the same inputs, tools, model and grading rules on both sides. When a baseline also passed, write that no advantage was measured. One small sample supports only that sample.
- Do not compute an improvement figure that the source does not record.

## Attribution

- **The user's decisions**: approvals, rejections, scope choices, rules they set and direction changes. Cite the record, such as a ledger entry, an approval note or a commit message.
- **Assistant work**: drafting, implementation, running tests and evaluations, reviews. Name the tool or model when the record names it.
- When the record does not show who decided something, write "attribution not confirmed". First-person drafts must not present the assistant's work as the user's own hands-on work.

## Case identity

- One case has one case ID for its whole life: `<project>-<subject>`, lowercase kebab case, no date.
- Revise the existing draft for that ID. Record the revision date in `updated`.
- Keep the case ID in the draft frontmatter so a later revision can find it.

## Privacy and scope

Use only material the user has authorized. Keep employer data and internal source in their own environment. Keep raw transcripts, credentials, private keys, account numbers, customer details and home-directory paths out of the draft. A private repository is still an external destination.

## Check before you report

- The draft is at `portfolio/<case-id>/case.md` under `<outputs>/<owner>/<task>/` (the outputs folder named in the user's instructions, or `~/agent-outputs/`), or in the owning project's private area.
- Each cited path, commit or link resolves.
- Each result sentence matches a `verified` or `qualified` row in the evidence table.
- The evidence table uses only the labels and statuses defined in this contract.
- Each `gap` appears under Limits or nowhere.
- The overall proof label is the lowest label that the main result needs.
- The draft has exactly one visual, and it is editable or a real project image.
- Attribution separates the user's decisions from the assistant's work.
- No publication, site, deployment, scheduling or outreach step ran.
