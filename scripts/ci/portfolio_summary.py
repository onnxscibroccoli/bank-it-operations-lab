#!/usr/bin/env python3
"""Report portfolio job results, including failures. This is not an approval gate."""
import argparse
import json
import os
from pathlib import Path

import user_actions

REQUIRED = (
    'offline', 'backup-static', 'orgs-static', 'network-edge',
    'endpoint-pester', 'base-aws', 'postgres', 'terraform-static', 'package',
)


def evaluate(needs):
    if not isinstance(needs, dict):
        needs = {}
    results = {}
    for job in sorted(set(REQUIRED) | set(needs)):
        value = needs.get(job)
        results[job] = value.get('result', 'missing') if isinstance(value, dict) else 'missing'
    return results, all(result == 'success' for result in results.values())


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--summary', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args(argv)
    errors = []
    try:
        needs = json.loads(os.environ.get('NEEDS_JSON', '{}'))
    except (ValueError, TypeError):
        needs = {}
        errors.append('Invalid NEEDS_JSON')
    results, passed = evaluate(needs)
    try:
        tasks, items, problems = user_actions.load(user_actions.ROOT / 'coordination/tasks.json')
        errors.extend(problems)
        top = user_actions.render(tasks, items)[0] if not problems else 'USER ACTION REQUIRED: UNKNOWN — invalid task register'
    except (OSError, ValueError, TypeError, KeyError, AttributeError):
        top = 'USER ACTION REQUIRED: UNKNOWN — task register could not be read'
        errors.append('Task register could not be read')
    passed = passed and not errors
    report = {
        'schema': 'bank-lab/portfolio-run-summary/v1',
        'repository': os.environ.get('GITHUB_REPOSITORY', ''),
        'testedSha': os.environ.get('GITHUB_SHA', ''),
        'runId': os.environ.get('GITHUB_RUN_ID', ''),
        'runAttempt': os.environ.get('GITHUB_RUN_ATTEMPT', ''),
        'event': os.environ.get('GITHUB_EVENT_NAME', ''),
        'jobs': results, 'validationPassed': passed,
        'approvalEffective': False, 'userActions': top, 'errors': errors,
    }
    Path(args.out).write_text(json.dumps(report, indent=2) + '\n')
    esc = lambda value: user_actions.esc_md(str(value))
    lines = ['## Portfolio run: ' + ('PASS' if passed else 'FAIL'), '', esc(top), '',
             'Tested SHA: `' + esc(report['testedSha']) + '`',
             'Run: ' + esc(report['runId']) + ', attempt ' + esc(report['runAttempt']), '',
             '| Job | Result |', '|---|---|']
    lines += ['| ' + esc(job) + ' | ' + esc(result) + ' |' for job, result in results.items()]
    lines += ['', 'Draft lab validation only. This does not confer independent review, owner approval, or merge eligibility.']
    lines += ['', *[esc(error) for error in errors]]
    with open(args.summary, 'a') as output:
        output.write('\n'.join(lines) + '\n')
    print(top)
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
