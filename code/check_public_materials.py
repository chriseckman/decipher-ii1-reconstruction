"""Check literary source and fixed construction using only candidate files.

Does not decode the actual historical message, download or write key/output files.
"""
from pathlib import Path
import json
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ii1_verify as V

if not __debug__:
    raise SystemExit('Checks require assertions: run without -O, -OO or PYTHONOPTIMIZE.')


def main():
    root = Path(__file__).resolve().parent.parent
    expected = json.loads((root / 'aggregate_results.json').read_text(encoding='utf-8'))['hashes']
    source = V.normalize_source((root / 'inputs/source_transcription.txt').read_text(encoding='utf-8'))
    key = V.build_key(source)
    assert len(source) == 492 and len(key) == 984
    assert V.sha256(source) == expected['key_source_492']
    assert V.sha256(key) == expected['key_984']
    assert all(key[n - 1] == source[(n if n <= 492 else 985 - n) - 1] for n in range(1, 985))
    print(json.dumps({'public_source_key_check': 'PASS', 'source_letters': len(source), 'key_positions': len(key),
        'source_hash': V.sha256(source), 'key_hash': V.sha256(key), 'actual_message_check': 'NOT RUN: input withheld'}, indent=2))


if __name__ == '__main__':
    main()
