#!/usr/bin/env python3
"""Run a frozen evaluator test under macOS Seatbelt, or refuse execution.

The test and manifest must live outside the worker fixture. The sandbox gives
Python read access to its system runtime, the fixture and the evaluator folder;
it permits writes only to artifacts/ inside a fresh output directory. The host
keeps its policy and receipt outside that writable area. It denies unspecified
operations, including network and child process creation. This is an optional
macOS evaluator, not a worker launcher.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def literal(path):
    # Seatbelt strings accept JSON's quote and backslash escapes for these paths.
    return json.dumps(str(path))


def profile(fixture, tests, artifacts, python):
    runtime = Path(python).parents[2] / "Library/Frameworks/Python3.framework"
    if not runtime.is_dir():
        raise ValueError("unsupported Python runtime; use Apple's Xcode Python")
    reads = ["/System", "/usr/lib", runtime, fixture, tests]
    ancestors = sorted({str(p) for location in [fixture, tests, artifacts, Path(python), runtime]
                        for p in Path(location).parents})
    return '\n'.join([
        '(version 1)', '(deny default)',
        # dyld opens the root directory while starting Apple's interpreter.
        # Grant this literal directory only, not its descendants.
        '(allow file-read-data (literal "/") (literal ' + literal(python) + '))',
        '(allow file-read* ' + ' '.join('(subpath ' + literal(p) + ')' for p in reads) + ')',
        '(allow file-read-metadata ' + ' '.join('(literal ' + literal(p) + ')' for p in ancestors) + ')',
        '(allow file-read* (literal "/dev/null") (literal "/dev/random") (literal "/dev/urandom") (literal "/private/etc/localtime"))',
        '(allow file-read* file-write* (subpath ' + literal(artifacts) + '))',
        '(allow process-exec (literal ' + literal(interpreter(python)) + '))',
    ]) + '\n'


def interpreter(python):
    # Apple's python3 shim uses posix_spawn. Invoke its interpreter directly so
    # the shim needs no child-process permission in the evaluator sandbox.
    return (Path(python).resolve(strict=True).parents[1] /
            'Resources/Python.app/Contents/MacOS/Python').resolve(strict=True)


def evaluate(fixture, manifest, output, timeout=30):
    fixture = Path(fixture).resolve(strict=True)
    manifest = Path(manifest).resolve(strict=True)
    if manifest.is_relative_to(fixture) or manifest.parent == fixture:
        raise ValueError("evaluator manifest must be outside worker fixture")
    frozen = json.loads(manifest.read_text())
    test = (manifest.parent / frozen['entrypoint']).resolve(strict=True)
    if not test.is_relative_to(manifest.parent) or test.is_relative_to(fixture):
        raise ValueError("test escapes evaluator folder")
    # Validate every evaluator input, not just the entrypoint, before execution.
    inputs = {}
    for rel, expected in frozen['files'].items():
        p = (manifest.parent / rel).resolve(strict=True)
        if not p.is_relative_to(manifest.parent) or sha(p) != expected:
            raise ValueError("frozen evaluator hash mismatch: " + rel)
        inputs[rel] = expected
    if frozen['entrypoint'] not in frozen['files']:
        raise ValueError("entrypoint is not frozen")
    sandbox = shutil.which('sandbox-exec')
    if not sandbox:
        raise ValueError("sandbox-exec unavailable; no unsandboxed fallback")
    python = subprocess.check_output(['/usr/bin/python3', '-I', '-c', 'import sys; print(sys.executable)'], text=True).strip()
    output = Path(output).resolve()
    if output.exists() or output.is_relative_to(fixture) or output.is_relative_to(manifest.parent):
        raise ValueError("output must be new and outside fixture and evaluator inputs")
    artifacts = output / 'artifacts'
    policy = profile(fixture, manifest.parent, artifacts, python)
    policy_digest = hashlib.sha256(policy.encode()).hexdigest()
    manifest_digest, test_digest = sha(manifest), sha(test)
    output.mkdir(parents=True)
    artifacts.mkdir()
    (artifacts / 'tmp').mkdir()
    policy_path = output / 'profile.sb'
    policy_path.write_text(policy)
    # Apply the in-memory policy; the evaluated code cannot select or rewrite
    # the policy file or host receipt. Only artifacts/ is writable.
    command = [sandbox, '-p', policy, str(interpreter(python)), '-I', '-B', str(test)]
    env = {'PATH': '/usr/bin:/bin', 'TMPDIR': str(artifacts / 'tmp'), 'EVAL_FIXTURE': str(fixture), 'EVAL_OUTPUT': str(artifacts)}
    try:
        result = subprocess.run(command, cwd=fixture, env=env, capture_output=True, text=True, timeout=timeout)
        record = {'status': 'pass' if result.returncode == 0 else 'fail', 'exit_code': result.returncode,
                  'stdout': result.stdout, 'stderr': result.stderr}
    except subprocess.TimeoutExpired:
        record = {'status': 'error', 'reason': 'evaluation timeout'}
    record.update(manifest_sha256=manifest_digest, test_sha256=test_digest,
                  profile_sha256=policy_digest, policy_unchanged=policy_path.read_bytes() == policy.encode(),
                  inputs_sha256=inputs,
                  inputs_unchanged=sha(manifest) == manifest_digest and all(
                      sha(manifest.parent / rel) == expected for rel, expected in inputs.items()),
                  command=command, sandbox='macOS Seatbelt default deny')
    if not record['policy_unchanged'] or not record['inputs_unchanged']:
        record.update(status='error', reason='host-owned policy or evaluator input changed')
    (output / 'receipt.json').write_text(json.dumps(record, indent=2) + '\n')
    return record


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fixture', required=True)
    parser.add_argument('--manifest', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    try:
        result = evaluate(args.fixture, args.manifest, args.output)
        print(json.dumps(result, indent=2))
        sys.exit(0 if result['status'] == 'pass' else 1)
    except (ValueError, OSError, KeyError) as exc:
        parser.exit(2, str(exc) + '\n')
