#!/usr/bin/env python3
"""Verify archived handoff bytes and optionally restore separate evidence folders."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import zipfile


def verify(root, destination=None):
    manifest = json.loads((root / 'evidence/2026-11-06/manifest.json').read_text())
    count = 0
    for entry in manifest['archives']:
        archive = root / entry['path']
        if archive.stat().st_size != entry['size_bytes']:
            raise ValueError(f'Size mismatch: {archive}')
        if hashlib.sha256(archive.read_bytes()).hexdigest() != entry['sha256']:
            raise ValueError(f'Archive hash mismatch: {archive}')
        with zipfile.ZipFile(archive) as z:
            actual = [i.filename for i in z.infolist() if not i.is_dir()]
            expected = [i['path'] for i in entry['files']]
            if len(set(actual)) != len(actual) or sorted(actual) != sorted(expected):
                raise ValueError(f'Member inventory mismatch: {archive}')
            for member in entry['files']:
                name = PurePosixPath(member['path'])
                if name.is_absolute() or '..' in name.parts:
                    raise ValueError(f'Unsafe archive member: {name}')
                data = z.read(member['path'])
                if len(data) != member['size_bytes'] or hashlib.sha256(data).hexdigest() != member['sha256']:
                    raise ValueError(f'Member hash mismatch: {archive}: {name}')
                count += 1
    # Verify everything before creating output. Destination must not already exist.
    if destination is not None:
        destination.mkdir(parents=True, exist_ok=False)
        for entry in manifest['archives']:
            archive = root / entry['path']
            with zipfile.ZipFile(archive) as z:
                z.extractall(destination / archive.stem)
    return {'archives_verified': len(manifest['archives']), 'members_verified': count, 'result': 'PASS'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--extract-to', type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(Path(__file__).resolve().parents[1], args.extract_to), indent=2))
