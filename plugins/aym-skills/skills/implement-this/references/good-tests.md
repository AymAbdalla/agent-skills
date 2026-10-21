# Good and weak tests

Read this when writing or reviewing a test. Examples use Python `unittest`; the rules apply to any language.

## A good test

- Calls the public interface the way a caller would.
- Names the behavior, not the mechanism: `test_total_includes_shipping_for_small_orders`, not `test_calls_shipping_helper`.
- Checks one behavior, with an expected value that comes from outside the code.
- Survives a refactor that keeps behavior the same.

```python
# Good: public function, expected value from the pricing requirement
def test_small_order_pays_flat_shipping(self):
    self.assertEqual(order_total([Item(price=20)]), 25)  # spec: +5 under 50
```

## Weak tests and their tells

**Tautological.** The expected value repeats the implementation's logic, so a wrong result would pass along with the right one.

```python
# Weak: recomputes the answer the way the code does
expected = sum(i.price for i in items) + (5 if sum(i.price for i in items) < 50 else 0)
self.assertEqual(order_total(items), expected)

# Better: a literal worked out from the requirement
self.assertEqual(order_total([Item(price=20), Item(price=10)]), 35)
```

**Coupled to internals.** The test reaches past the interface: it calls a private `_helper`, asserts how many times a collaborator was called, or reads a database row instead of using the read API. Tell: a refactor that keeps behavior breaks the test.

```python
# Weak: private helper
self.assertEqual(_normalise_tag("  Ash "), "ash")

# Better: the public behavior the helper serves
self.assertEqual(find_tags("  Ash , cedar"), ["ash", "cedar"])
```

**Insensitive.** The assertion cannot fail on the bug it claims to cover, for example only checking that a call did not raise. Tell: the test passes with the bug still present. Showing red before the fix catches this.

**Horizontal batch.** Many tests written up front for imagined behavior, then all the code. Tell: tests check shapes and names rather than results. Prefer one test, one change, repeat.

**Negative test with no named guard.** A test that feeds bad input and expects a rejection, without saying which check rejects it. Tell: an earlier layer (parsing, a type check, the framework) rejects the input first, so the guard the test claims to cover never runs. Name the guard the test trips and say why nothing before it catches the input.

## Never weaken a test to get green

Do not loosen or remove an assertion, widen a tolerance, add a skip or only marker, delete a case, mock the code under test, or lower a coverage threshold to make a run pass. If a test looks wrong, say why, tie the change to a requirement, and report it as a change to the test, not a fix to the code.

## Prove the test command first

Before writing a new test, run one existing test that should pass and see it pass. This proves the runner, paths and environment work, so a later red means the new test, not the setup.

## Red for the right reason

A failing run proves sensitivity only when the failure message matches the missing behavior: an `AssertionError` showing the wrong value, or the expected exception missing. A syntax error, typo or fixture crash means the test itself is broken, not red. Fix the test and rerun before changing production code. The one production change allowed before red is the stub below.

For a function or module that does not exist yet, an `ImportError` or `NameError` proves only that the name is missing. Add a stub that returns a placeholder, then run again so the failure comes from the assertion (`AssertionError: Lists differ: [] != ['axle', 'bolt']`). Pick a placeholder that differs from every expected value in the slice; a test that expects `[]` would pass against this stub and show no red.

```python
def low_stock(items, threshold=5):
    return []  # stub: lets the test reach its assertion
```

A stub that raises `NotImplementedError` shows the test reaches the call, but unittest reports it as an error, not an assertion failure.

## How much to test

Match the evidence to the request. A small bug fix usually needs one regression test plus the existing suite. A new feature needs a test per behavior in the acceptance criteria. Broad end-to-end suites belong to explicit requests or release checks. Say what remains untested instead of padding the suite.
