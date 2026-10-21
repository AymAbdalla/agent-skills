# Behavior checklist for a simplification

Answer each question for the old code and the proposed code. A "no" or "unknown" means skip the change or flag it.

## Outputs and errors

- Same return value and type for normal inputs, including `None`, empty containers and zero?
- Same printed or logged text, including spacing, newlines and number formatting?
- Same exception type and the same message text? Callers and tests often match on messages.
- Same point of failure? A replacement that fails earlier or later can leave different partial state.

## Order and edge cases

- Same output order? Check sorting stability, ties, dictionary and set iteration, and reverse order.
- Same handling of empty input, one item, duplicates, negative numbers, very large values, mixed types and Unicode?
- Same rounding and integer or float result? For example, Python's `round` rounds half to even and `statistics.mean` raises `StatisticsError` on empty input, where a hand-written loop might return `0` or raise `ZeroDivisionError`.

## Callers and side effects

- Same public name, signature, default arguments and keyword names?
- Same side effects: files written, network calls, mutations of the input, caching, logging?
- Did you search for dynamic callers before deleting: string names, `getattr`, registries, exports, templates, configuration, other packages?

## Safety and settled choices

- Every validation, permission, escaping and secret-handling step still present?
- Accessibility attributes, labels and keyboard paths still present?
- No change to a choice the plan or spec settled on purpose?

## Confirming the answer

Prefer the project's own tests. If they do not cover the edge, run a short comparison: call the old and new code on the same inputs and print both results, including the error type and message for failing inputs. Run that comparison in scratch space, not in the repository. Report the inputs you tried, so the reader can see what the check covered.

## Debt note format

```text
Debt: <location> keeps <the more complex form>
Limit: <the real reason: caller compatibility, measured performance, safety check, settled plan choice>
Revisit when: <the event that removes the limit>
```

Record a debt note in the report. Write it into a project document only when the user asks.
