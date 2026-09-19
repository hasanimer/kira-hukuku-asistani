"""Read the bundled TBK snapshot by article; standard library only."""
import argparse
import hashlib
import json
import re
from pathlib import Path
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('article', type=int, nargs='?')
args = parser.parse_args()
root = Path(__file__).resolve().parents[1] / 'data' / 'mevzuat'
source = root / '6098-source.json'
data = json.loads(source.read_text(encoding='utf-8'))
chunks = data['chunks']
if [c['chunk']['index'] for c in chunks] != list(range(1, 8)) or any(
        c['chunk']['total'] != 7 for c in chunks):
    parser.error('Missing or unordered legislation chunks')
text = '\n\n'.join(c['markdown'] for c in chunks)
if len(text.encode('utf-8')) != chunks[0]['total_bytes']:
    parser.error('Total byte count mismatch')
manifest = json.loads((root.parent / 'manifest.json').read_text(encoding='utf-8'))
if hashlib.sha256(source.read_bytes()).hexdigest() != manifest['files']['mevzuat/6098-source.json']:
    parser.error('Legislation snapshot hash mismatch')
matches = list(re.finditer(r'(?m)^[ \t]*(?:#+\s*)?(?:\*\*)?MADDE\s+(\d+)\b', text))
if [int(m.group(1)) for m in matches] != list(range(1, 650)):
    parser.error('Article headings missing, duplicated or unordered')
result = {'retrieved_at_utc': data['retrieved_at_utc'],
          'source_url': chunks[0]['source_url'], 'article_count': len(matches),
          'snapshot_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
          'note': 'Stored retrieval snapshot; recheck effective law for the relevant date.'}
if args.article is not None:
    if not 1 <= args.article <= 649:
        parser.error('Article must be between 1 and 649')
    start = matches[args.article - 1].start()
    end = matches[args.article].start() if args.article < 649 else len(text)
    result['requested_article'] = args.article
    result['markdown'] = text[start:end]
    result['context_note'] = 'May include the next heading, temporary provisions or footnotes; distinguish them from the requested article.'
print(json.dumps(result, ensure_ascii=False, indent=2))
