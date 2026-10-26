# Extend or rebuild a studied target

Read this when the request asks to extend, rebuild, adapt or replace an existing mechanism. Start with the target-specific inspection guide. A name or interface listing alone cannot supply the missing implementation.

## Establish the original and the requested difference

Identify the exact source and owning repository, its inspected revision or file hashes, the input-to-result path and the behavior the user wants changed. Carry forward existing choices and approval. Ask about a missing choice only when it changes behavior or material consequences; continue source inspection while it remains open.

Use separate labels:

- **Original, source-inspected:** what the inspected files implement or instruct. Cite file and symbol or line. Do not call it a reproduced result.
- **Original, runtime-observed:** a result from an executed check, with its input, environment and receipt.
- **Proposed:** an addition, deletion or altered rule. Explain the need, tradeoff and intended check.
- **Implemented and checked:** an authorized source change and the actual checks run. Record failures, unavailable checks and remaining uncertainty.

## Choose the size of the change

Prefer an extension when the existing contract, components and data format still fit. Recommend a rebuild when retaining them would prevent the agreed behavior or require a broader change than replacement. Explain the reason from inspected evidence. Complexity or unfamiliarity alone does not justify a rewrite.

Write a keep/change/remove table. For each row, include its original source, the proposed treatment, the reason and an observable check. Preserve useful mechanics rather than copying an entire framework. Name dependencies, output and privacy rules, side effects, compatibility costs and failure behavior. Data migration, changed public interfaces and removed behavior need explicit decisions. Mark unresolved choices as unresolved; do not invent them to complete the table.

Show a small editable flow when it helps. Make before and after clear: a proposed after state does not prove an improvement. A comparison needs comparable conditions and checks.

## Carry an authorized implementation

A request to dissect or propose stops at a reviewable blueprint. For implementation, check the current authorization against the concrete scope and owning project's rules. Existing approval can suffice; material scope changes need clarification before dependent edits.

Resolve the maintained source repository or registered task worktree before editing. An installed plugin, cache or runtime snapshot is a distribution copy. Do not edit it as a substitute for owning source. If the source is unavailable, deliver the proposal and name the missing source; do not silently create a competing implementation.

Use the available implementation method for the target. Preserve unrelated changes, review the settled change independently when required (a fresh chat or the other tool; a helper the author starts gives only a helper review, and the author's own look is self-review), run checks against the intended behavior and recheck the original symptom where relevant. Installation, migration, network writes, publication and sending messages retain their own authorization requirements.

Finish with the original evidence, proposed change, executed changes, actual checks, gaps and the retained artifact. A before/after proposal is still a proposal until implementation and its checks exist.
