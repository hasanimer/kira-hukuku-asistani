"""Offline benchmark/catalog tools. Scores explicit human reviews, never legal truth."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(',', ':')).encode('utf-8')).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique(rows, label):
    require(isinstance(rows, list), f'{label}: expected list')
    ids = [r['id'] for r in rows]
    require(len(ids) == len(set(ids)), f'{label}: duplicate ID')
    return {r['id']: r for r in rows}


def load(root=ROOT):
    suite = read(root / 'evals/cases.json')
    catalog = read(root / 'references/karar-kartlari.json')
    require(suite['schema_version'] == catalog['schema_version'] == 1,
            'Unsupported schema')
    require(suite['fictional'] is True, 'Missing fiction label')
    cases = unique(suite['cases'], 'cases')
    cards = unique(catalog['cards'], 'cards')
    require(bool(cases) and bool(cards), 'Empty catalog')
    audit = unique(read(root / 'references/egitim-kaynak-kaydi.json')['records'], 'audit')
    for case in cases.values():
        require(case['fictional'] is True, 'Missing case fiction label')
        require(all(isinstance(case[k], str) and case[k].strip()
                    for k in ('id', 'prompt', 'module', 'reference')), 'Empty case field')
        ref = (root / case['reference']).resolve()
        require(ref.is_relative_to(root.resolve()) and ref.is_file(), 'Missing/unsafe reference')
        criteria = unique(case['criteria'], 'criteria')
        require(set(criteria) == {'analysis', 'questions', 'avoid'}, 'Incomplete rubric')
        for criterion in criteria.values():
            require(isinstance(criterion['description'], str) and criterion['description'].strip()
                    and type(criterion['critical']) is bool, 'Invalid criterion')
    for card in cards.values():
        require(card['source_id'] in audit, 'Unknown decision source')
        require(card['source'] == audit[card['source_id']], 'Source provenance mismatch')
        require(card['full_text_in_card'] is False, 'Card is not a full-text record')
        require(card['outcome'] in {'bozma', 'onama', 'uyusmazligin_giderilmesi',
                                   'karar_verilmesine_yer_olmadigi'}, 'Unknown disposition')
        for key in ('title', 'facts', 'evidence', 'issue', 'reasoning', 'result', 'limits',
                    'review_status', 'checked_on'):
            require(isinstance(card[key], str) and card[key].strip(), 'Empty card field: ' + key)
        require(isinstance(card['dissent'], list) and all(isinstance(x, str) and x.strip()
                for x in card['dissent']), 'Invalid dissent')
        require(card['scenario_ids'] and all(x in cases for x in card['scenario_ids']),
                'Unknown scenario link')
    return suite, catalog


def blind(suite):
    return {'suite_version': suite['version'], 'suite_hash': digest(suite),
            'fictional': True, 'cases': [
                {k: c[k] for k in ('id', 'prompt')} for c in suite['cases']]}


def template(suite, answers):
    cases = unique(suite['cases'], 'cases')
    rows = unique(answers['answers'], 'answers')
    require(rows and set(rows) <= set(cases), 'Empty or unknown answers')
    require(answers['suite_hash'] == digest(suite), 'Answers use a different suite')
    require(isinstance(answers.get('run'), str) and answers['run'].strip(), 'Missing run label')
    reviews = []
    for key, row in rows.items():
        require(isinstance(row['response'], str) and row['response'].strip(), 'Empty response')
        reviews.append({'id': key, 'response': row['response'],
                        'response_hash': digest(row['response']),
                        'checks': [{'id': c['id'], 'met': None, 'evidence': '', 'rationale': ''}
                                   for c in cases[key]['criteria']]})
    return {'suite_hash': digest(suite), 'run': answers['run'], 'reviewer': '',
            'reviewed_on': '', 'reviews': reviews}


def score(suite, review):
    cases = unique(suite['cases'], 'cases')
    require(review['suite_hash'] == digest(suite), 'Review uses a different suite')
    for field in ('run', 'reviewer', 'reviewed_on'):
        require(isinstance(review.get(field), str) and review[field].strip(), 'Missing ' + field)
    rows = unique(review['reviews'], 'reviews')
    require(rows and set(rows) <= set(cases), 'Empty or unknown reviews')
    details = []
    for key, row in rows.items():
        response = row['response']
        require(isinstance(response, str) and response.strip(), 'Empty response')
        require(row['response_hash'] == digest(response), 'Response changed after template')
        checks = unique(row['checks'], 'checks')
        criteria = unique(cases[key]['criteria'], 'criteria')
        require(set(checks) == set(criteria), 'Missing or unknown review criteria')
        for check in checks.values():
            require(type(check['met']) is bool, 'Unreviewed criterion')
            require(isinstance(check['rationale'], str) and check['rationale'].strip(),
                    'Missing review rationale')
            evidence = check['evidence']
            require(isinstance(evidence, str), 'Invalid evidence')
            require(not check['met'] or evidence.strip(), 'Passing review needs response evidence')
            require(not evidence or evidence in response, 'Evidence is not in response')
        critical_failures = [k for k, c in criteria.items() if c['critical'] and not checks[k]['met']]
        met = sum(c['met'] for c in checks.values())
        details.append({'id': key, 'module': cases[key]['module'], 'met': met,
                        'criteria': len(criteria), 'critical_failures': critical_failures,
                        'passed': met == len(criteria)})
    complete = len(rows) == len(cases)
    return {'assessment': 'human_review_not_automatic_legal_validation',
            'suite_hash': digest(suite), 'run': review['run'], 'reviewer': review['reviewer'],
            'reviewed_on': review['reviewed_on'], 'complete': complete,
            'reviewed': len(rows), 'total': len(cases),
            'missing': sorted(set(cases) - set(rows)),
            'met_ratio_reviewed': sum(r['met'] for r in details) / sum(r['criteria'] for r in details),
            'suite_passed': complete and all(r['passed'] for r in details), 'details': details}


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, help='Write UTF-8 JSON without shell encoding differences')
    sub = p.add_subparsers(dest='command', required=True)
    sub.add_parser('validate')
    sub.add_parser('export')
    show = sub.add_parser('case')
    show.add_argument('id')
    cards = sub.add_parser('cards')
    cards.add_argument('query', nargs='?', default='')
    for name in ('review-template', 'score'):
        child = sub.add_parser(name)
        child.add_argument('file', type=Path)
    args = p.parse_args()
    suite, catalog = load()
    if args.command == 'validate':
        result = {'structural_validation': 'pass', 'cases': len(suite['cases']),
                  'cards': len(catalog['cards']), 'suite_hash': digest(suite),
                  'legal_performance': 'not_measured'}
    elif args.command == 'export':
        result = blind(suite)
    elif args.command == 'case':
        found = [c for c in suite['cases'] if c['id'] == args.id.upper()]
        require(found, 'Unknown case ID')
        result = found[0]
    elif args.command == 'cards':
        q = args.query.casefold()
        result = [c for c in catalog['cards'] if q in json.dumps(c, ensure_ascii=False).casefold()]
    elif args.command == 'review-template':
        result = template(suite, read(args.file))
    else:
        result = score(suite, read(args.file))
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    if args.output:
        with args.output.open('x', encoding='utf-8') as handle:
            handle.write(rendered)
    else:
        print(rendered, end='')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        sys.exit(2)
