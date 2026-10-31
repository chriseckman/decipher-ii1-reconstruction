"""Manifest checks use tiny synthetic trees, not private research material."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_manifest as M


def tree(root):
    data = b'invented release file\n'
    (root / 'README.md').write_bytes(data)
    info = {'self_hash_included': False, 'files': [
        {'path': 'README.md', 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}]}
    (root / 'MANIFEST.json').write_text(json.dumps(info), encoding='utf-8')
    return info


class TestManifest(unittest.TestCase):
    def test_complete_manifest_succeeds_and_tampering_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tree(root)
            self.assertEqual(M.check(root)['payload_files'], 1)
            (root / 'README.md').write_bytes(b'tampered\n')
            with self.assertRaisesRegex(ValueError, 'mismatch'):
                M.check(root)

    def test_hidden_and_ignored_local_files_are_still_rejected(self):
        for name in ('.private-note', 'numbers.txt', 'plaintext_literal_314.txt', '__pycache__/private-note.txt'):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                tree(root)
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b'invented')
                with self.assertRaisesRegex(ValueError, 'unlisted'):
                    M.check(root)

    def test_git_internal_and_only_cache_bytecode_are_exempt(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tree(root)
            (root / '.git').mkdir()
            (root / '.git/config').write_bytes(b'invented')
            cache = root / '__pycache__'
            cache.mkdir()
            (cache / 'module.cpython-310.pyc').write_bytes(b'invented')
            self.assertEqual(M.check(root)['ignored_python_bytecode_files'], 1)

    def test_path_traversal_and_portability_collisions_fail(self):
        for name in ('../escape', '/absolute', 'C:/absolute', 'a\\b', 'a//b', 'a/./b', '.git/config', 'MANIFEST.json'):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                info = tree(root)
                info['files'][0]['path'] = name
                (root / 'MANIFEST.json').write_text(json.dumps(info), encoding='utf-8')
                with self.assertRaisesRegex(ValueError, 'Unsafe'):
                    M.check(root)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            info = tree(root)
            info['files'].append(dict(info['files'][0], path='readme.MD'))
            (root / 'MANIFEST.json').write_text(json.dumps(info), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'case-colliding'):
                M.check(root)

    def test_manifest_validation_is_active_under_optimization(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tree(root)
            (root / 'README.md').write_bytes(b'altered')
            env = os.environ.copy()
            env['PYTHONOPTIMIZE'] = '1'
            result = subprocess.run([sys.executable, '-B', '-O', str(Path(M.__file__)), '--root', str(root)],
                                    capture_output=True, text=True, env=env)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('FAIL', result.stderr)
            self.assertNotIn('PASS', result.stdout)


if __name__ == '__main__':
    unittest.main()
