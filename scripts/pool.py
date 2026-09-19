"""Read-only, hash-checked access to the rent determination corpus."""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import sys
import unicodedata


def normalize(text):
    text = text.replace('ı', 'i').replace('İ', 'i').casefold()
    return ''.join(c for c in unicodedata.normalize('NFKD', text)
                   if not unicodedata.combining(c))


def read_rows(path):
    seen = set()
    with path.open(encoding='utf-8-sig') as stream:
        for line_no, line in enumerate(stream, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            key = str(row['document_id'])
            if key in seen:
                raise ValueError(f'Duplicate document_id: {key} ({path}:{line_no})')
            seen.add(key)
            actual = hashlib.sha256(row['text'].encode('utf-8')).hexdigest()
            if actual != row['text_sha256']:
                raise ValueError(f'Text hash mismatch: {key} ({path}:{line_no})')
            yield row


def metadata(row):
    keys = ('document_id', 'court', 'esas_no', 'karar_no', 'karar_tarihi',
            'text_sha256', 'human_validated', 'review_level', 'value_assessment',
            'court_type', 'source_url', 'source_provider', 'research_notes',
            'source_text_sha256', 'redactions')
    return {key: row.get(key) for key in keys}


def emit(value):
    print(json.dumps(value, ensure_ascii=False, indent=2))


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path,
                        default=Path(__file__).resolve().parents[1] / 'data')
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('stats')
    search = sub.add_parser('search')
    search.add_argument('terms', nargs='+')
    search.add_argument('--limit', type=int, default=8)
    search.add_argument('--court-type', choices=['bam'])
    search.add_argument('--kind', choices=['esas_gerekcesi', 'usul_gerekcesi',
                                         'kisa_karar', 'sinirda'])
    get = sub.add_parser('get')
    get.add_argument('document_id')
    quote = sub.add_parser('quote')
    quote.add_argument('document_id')
    quote.add_argument('quotation')
    args = parser.parse_args()
    source = args.root / 'topic-rescan-assistant-adjusted.jsonl'
    rows = list(read_rows(source))
    sources = [source]
    bam = args.root / 'bam-selected.jsonl'
    if bam.exists():
        rows.extend(read_rows(bam))
        sources.append(bam)
    ids = [str(row['document_id']) for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate document_id across pools')
    prior = args.root / 'verified-topic-pool.jsonl'
    if prior.exists():
        labels = {(str(r['document_id']), r['text_sha256']): r.get('value_assessment')
                  for r in read_rows(prior)}
        for row in rows:
            row['value_assessment'] = labels.get(
                (str(row['document_id']), row['text_sha256']), row.get('value_assessment'))
    envelope = {'source_file': str(source.resolve()), 'records': len(rows),
                'source_file_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                'source_files': {str(p.resolve()): hashlib.sha256(p.read_bytes()).hexdigest()
                                 for p in sources}}
    if args.command == 'stats':
        dates = sorted(r['karar_tarihi'] for r in rows if r.get('karar_tarihi'))
        kinds = collections.Counter((r.get('value_assessment') or {}).get(
            'icerik_turu', {}).get('choice', 'unknown') for r in rows)
        emit({**envelope, 'date_min': dates[0] if dates else None,
              'date_max': dates[-1] if dates else None, 'kinds': dict(kinds),
              'human_validated_records': sum(r.get('human_validated') is True for r in rows)})
    elif args.command == 'search':
        if not 1 <= args.limit <= 100:
            parser.error('--limit must be between 1 and 100')
        terms = [normalize(t.strip()) for t in args.terms]
        if not all(terms):
            parser.error('Search terms cannot be empty')
        found = []
        for row in rows:
            if args.court_type and row.get('court_type') != args.court_type:
                continue
            kind = (row.get('value_assessment') or {}).get('icerik_turu', {}).get('choice')
            if args.kind and kind != args.kind:
                continue
            normalized = normalize(row['text'])
            if all(t in normalized for t in terms):
                score = sum(normalized.count(t) for t in terms)
                # Return an original-text paragraph rather than offsets into normalized text.
                paragraphs = row['text'].splitlines()
                relevant = sorted(enumerate(paragraphs), key=lambda p: (
                    -sum(t in normalize(p[1]) for t in terms), p[0]))
                snippet = relevant[0][1][:1400] if relevant else ''
                found.append((score, str(row['document_id']),
                              {**metadata(row), 'lexical_score': score, 'snippet': snippet}))
        found.sort(key=lambda item: (-item[0], item[1]))
        emit({**envelope, 'total_matches': len(found),
              'results': [r[2] for r in found[:args.limit]]})
    else:
        row = next((r for r in rows if str(r['document_id']) == args.document_id), None)
        if row is None:
            raise ValueError(f'Document not found in strict pool: {args.document_id}')
        if args.command == 'get':
            emit({**envelope, **metadata(row), 'text': row['text']})
        else:
            if not args.quotation.strip():
                parser.error('Quotation cannot be empty')
            positions = []
            offset = 0
            while True:
                start = row['text'].find(args.quotation, offset)
                if start < 0:
                    break
                end = start + len(args.quotation)
                positions.append({'start': start, 'end': end,
                                  'context': row['text'][max(0, start-200):end+200]})
                offset = start + 1
            emit({**envelope, **metadata(row), 'exact_match': bool(positions),
                  'quotation': args.quotation, 'occurrences': positions})
            if not positions:
                return 2
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f'Corpus error: {exc}', file=sys.stderr)
        sys.exit(1)
