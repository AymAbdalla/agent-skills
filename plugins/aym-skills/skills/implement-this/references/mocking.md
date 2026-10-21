# When to replace a dependency

Read this before mocking, stubbing or faking anything.

## Replace only system boundaries

Replace a dependency only where the code leaves your control:

- external services and paid APIs (payments, email, model providers)
- the clock and randomness, so results are repeatable
- the network
- databases and the filesystem when a real temporary instance is slow or unavailable; prefer a temporary real one when it is cheap

Keep your own modules, classes and helper functions real. Replacing them tests the mock, not the code, and couples the test to internal structure.

## Make boundaries easy to replace

When a boundary is hard to replace, suggest passing it in rather than creating it inside the function:

```python
# Hard to test: creates its own client from the environment
def send_receipt(order):
    client = MailClient(os.environ["MAIL_KEY"])
    client.send(order.email, render(order))

# Easy to test: the caller supplies the client
def send_receipt(order, client):
    client.send(order.email, render(order))
```

Prefer one small function per external operation (`get_user`, `create_order`) over one generic `request(path, options)`. A fake for a specific operation returns one known shape and needs no branching.

Changing a function signature for testability is a design change. If an approved plan did not cover it, ask before making it.

## Assert outcomes, not calls

Even at a boundary, prefer checking what the caller can observe: the returned value, the message content a fake received, the saved record read back through the public API. Assert on call counts or order only when that order is itself the requirement, such as "charge exactly once".

## Secrets in tests

Never put real credentials in tests or fixtures. Use obvious placeholders such as `test-key` and read real values only from the environment in integration runs the user approved.
