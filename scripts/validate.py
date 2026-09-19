"""Validate packaged source integrity and portable command behavior offline."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def run(script, *args, expected=0):
    result = subprocess.run(
        [sys.executable, str(ROOT / 'scripts' / script), *args],
        cwd=ROOT.parent, capture_output=True, encoding='utf-8')
    require(result.returncode == expected, f'{script}: {result.stderr}')
    return json.loads(result.stdout) if result.stdout else None


def main():
    manifest = json.loads((ROOT / 'data/manifest.json').read_text(encoding='utf-8'))
    for name, digest in manifest['files'].items():
        path = (ROOT / 'data' / name).resolve()
        require(path.is_relative_to(ROOT / 'data'), f'Invalid manifest path: {name}')
        require(hashlib.sha256(path.read_bytes()).hexdigest() == digest,
                f'File hash mismatch: {name}')
    data = json.loads((ROOT / 'data/mevzuat/6098-source.json').read_text(encoding='utf-8'))
    text = '\n\n'.join(c['markdown'] for c in data['chunks'])
    readable = (ROOT / 'data/mevzuat/6098-turk-borclar-kanunu.md').read_text(encoding='utf-8')
    require(readable == text + '\n', 'Readable law differs from source chunks')
    stats = run('pool.py', 'stats')
    require(stats['records'] == manifest['records'], 'Decision count mismatch')
    if 'collections' in manifest:
        for name, count in manifest['collections'].items():
            require(sum(bool(line.strip()) for line in (ROOT / 'data' / name).read_text(
                encoding='utf-8').splitlines()) == count, f'Collection count mismatch: {name}')
    bam_file = ROOT / 'data/bam-selected.jsonl'
    if bam_file.exists():
        for line in bam_file.read_text(encoding='utf-8').splitlines():
            bam = json.loads(line)
            fetched = run('pool.py', 'get', bam['document_id'])
            require(fetched['text'] == bam['text'] and fetched['source_url'] == bam['source_url'],
                    'BAM text or provenance lost')
            if bam.get('redactions'):
                require(fetched['redactions'] == bam['redactions'] and
                        fetched['source_text_sha256'] == bam['source_text_sha256'],
                        'Anonymization provenance lost')
                require(bam['source_text_sha256'] != bam['text_sha256'],
                        'Redacted text must have a distinct source hash')
                require(bam['text'].count('[KİŞİ ADI ANONİMLEŞTİRİLDİ]') ==
                        bam['redactions']['replacement_count'],
                        'Anonymization count mismatch')
            quoted = run('pool.py', 'quote', bam['document_id'], bam['text'][-100:])
            require(quoted['exact_match'], 'BAM final text quote failed')
        filtered = run('pool.py', 'search', 'kira', '--court-type', 'bam')
        require(filtered['total_matches'] == manifest['collections']['bam-selected.jsonl'],
                'BAM filter missed records')
        require(all(r['court_type'] == 'bam' for r in filtered['results']), 'BAM filter leaked')
    scenarios = run('scenarios.py', 'list')
    require(scenarios['fictional'] and scenarios['total'] > 0,
            'Scenario catalog unavailable or fiction label lost')
    deadline = run('deadlines.py', 'tbk345', '2026-09-01')
    require(deadline['raw_dates']['otuz_gun_once_esigi'] == '2026-08-02' and
            deadline['status'] == 'takvim_adayi_hukuki_kontrol_gerekli',
            'Deadline calendar or qualification lost')
    search = run('pool.py', 'search', 'eski kiracı', '--kind', 'esas_gerekcesi', '--limit', '1')
    require(search['total_matches'] > 0, 'Known search returned no matches')
    row = run('pool.py', 'get', search['results'][0]['document_id'])
    quote = row['text'][:80]
    match = run('pool.py', 'quote', row['document_id'], quote)
    require(match['exact_match'] and match['occurrences'][0]['start'] == 0,
            'Exact quote verification failed')
    absent = run('pool.py', 'quote', row['document_id'],
                 'NONEXISTENT-QUOTE-f06d52cb', expected=2)
    require(not absent['exact_match'], 'Absent quote was accepted')
    for number in (1, 59, 344, 345, 649):
        article = run('tbk.py', str(number))
        require(article['requested_article'] == number and article['markdown'],
                f'Article {number} unavailable')
    run('tbk.py', '650', expected=2)
    calc = run('hesap.py', 'tespit', '--baslangic', '01.07.2018', '--artis-sarti', '--hedef-donem', '01.07.2024', '--json')
    require(calc['bes_yil_dolum_tarihi'] == '30.06.2023' and calc['ilk_hak_nesafet_donemi']['kira_yili'] == 6,
            'hesap.py tespit calculation error')
    calc10 = run('hesap.py', 'tahliye-10yil', '--baslangic', '01.01.2015', '--json')
    require(calc10['toplam_yil'] == 12 and calc10['en_gec_ihtar_teblig_tarihi'] == '01.10.2026',
            'hesap.py tahliye-10yil calculation error')
    run('hesap.py', 'tespit', '--baslangic', 'invalid', '--hedef-donem', '01.07.2024', '--artis-sarti', expected=1)
    with tempfile.TemporaryDirectory(prefix='kira-integrity-') as directory:
        corrupt = dict(row, text=row['text'] + 'changed')
        path = Path(directory) / 'topic-rescan-assistant-adjusted.jsonl'
        path.write_text(json.dumps(corrupt), encoding='utf-8')
        run('pool.py', '--root', directory, 'stats', expected=1)
    for doc in [ROOT / 'README.md', ROOT / 'SKILL.md', *sorted((ROOT / 'references').glob('*.md'))]:
        for target in re.findall(r'\]\(([^)]+)\)', doc.read_text(encoding='utf-8')):
            if '://' not in target and not target.startswith('#'):
                require((doc.parent / target.split('#')[0]).exists(),
                        f'Broken link in {doc.name}: {target}')
    print(f'PASS: {stats["records"]} decisions, file/text hashes, law, links, CLI and rejection checks')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError) as exc:
        print(f'FAIL: {exc}', file=sys.stderr)
        sys.exit(1)
