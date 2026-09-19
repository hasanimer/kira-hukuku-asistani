"""Find fictional tenant scenarios and resolve their real, hash-checked sources."""
import argparse
import json
from pathlib import Path
import sys

from pool import normalize, read_rows, metadata

ROOT = Path(__file__).resolve().parents[1]


def load_catalog(root):
    catalog = json.loads((root / 'references/kiraci-senaryolari.json').read_text(encoding='utf-8'))
    if catalog.get('schema_version') != 1 or catalog.get('fictional') is not True:
        raise ValueError('Unsupported catalog or missing fiction label')
    seen = set()
    for row in catalog['scenarios']:
        if row['id'] in seen:
            raise ValueError('Duplicate scenario ID')
        seen.add(row['id'])
        for field in ('title', 'story', 'coverage'):
            if not isinstance(row.get(field), str) or not row[field].strip():
                raise ValueError(f'Missing scenario field: {field}')
        for field in ('keywords', 'modules', 'documents', 'decisive_questions',
                      'search_queries', 'decision_ids', 'counterfacts'):
            if not isinstance(row.get(field), list) or not row[field] or not all(
                    isinstance(item, str) and item.strip() for item in row[field]):
                raise ValueError(f'Invalid scenario field: {field}')
    return catalog['scenarios']


def resolve(rows, root):
    sources = {}
    for name in ('topic-rescan-assistant-adjusted.jsonl', 'bam-selected.jsonl'):
        for decision in read_rows(root / 'data' / name):
            key = str(decision['document_id'])
            if key in sources:
                raise ValueError(f'Duplicate source ID: {key}')
            sources[key] = decision
    result = []
    for row in rows:
        absent = set(row['decision_ids']) - sources.keys()
        if absent:
            raise ValueError(f'Missing source for {row["id"]}: {sorted(absent)}')
        result.append({**row, 'fictional': True,
                       'decisions': [metadata(sources[key]) for key in row['decision_ids']]})
    return result


def search(rows, query):
    # OR across words: a mixed dispute must not lose one issue to an AND filter.
    terms = set(normalize(query).split())
    if not terms:
        raise ValueError('Search query cannot be empty')
    found = []
    for row in rows:
        haystack = normalize(' '.join([row['title'], row['story'], *row['keywords']]))
        matches = sorted(term for term in terms if term in haystack)
        if matches:
            found.append({**row, 'matched_terms': matches})
    return sorted(found, key=lambda row: -len(row['matched_terms']))


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('list')
    show = commands.add_parser('show')
    show.add_argument('id')
    find = commands.add_parser('search')
    find.add_argument('query', nargs='+')
    args = parser.parse_args()
    rows = load_catalog(args.root)
    if args.command == 'show':
        rows = [row for row in rows if row['id'] == args.id.upper()]
        if not rows:
            raise ValueError(f'Unknown scenario: {args.id}')
    elif args.command == 'search':
        rows = search(rows, ' '.join(args.query))
    # Resolve before printing; broken citations must fail, not silently disappear.
    rows = resolve(rows, args.root)
    if args.command == 'list':
        rows = [{key: row[key] for key in ('id', 'title', 'fictional', 'modules', 'coverage')}
                for row in rows]
    print(json.dumps({
        'fictional': True,
        'matching': 'Lexical discovery only; order is not legal relevance or win probability.',
        'total': len(rows), 'scenarios': rows,
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, OSError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        sys.exit(2)
