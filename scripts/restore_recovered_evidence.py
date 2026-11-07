#!/usr/bin/env python3
"""Verify archived handoff bytes and optionally restore separate evidence folders."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import tempfile
import zipfile


def verify(root, destination=None, assemble_to=None):
    with tempfile.TemporaryDirectory(prefix='ladefe-evidence-') as temp:
        return _verify(root, destination, assemble_to, Path(temp))


def _verify(root, destination, assemble_to, temp):
    manifest = json.loads((root / 'evidence/2026-11-06/manifest.json').read_text())
    transport_path = root / 'evidence/2026-11-06/archive_parts.json'
    transport = json.loads(transport_path.read_text())['archives'] if transport_path.exists() else {}
    count = 0
    resolved = []
    for entry in manifest['archives']:
        archive = root / entry['path']
        if not archive.exists() and entry['path'] in transport:
            archive = temp / Path(entry['path']).name
            with archive.open('wb') as out:
                for part in transport[entry['path']]:
                    part_path = PurePosixPath(part['path'])
                    if part_path.is_absolute() or '..' in part_path.parts:
                        raise ValueError(f'Unsafe part path: {part_path}')
                    data = (root / part_path).read_bytes()
                    if len(data) != part['size_bytes'] or hashlib.sha256(data).hexdigest() != part['sha256']:
                        raise ValueError(f'Part hash mismatch: {part_path}')
                    out.write(data)
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
        resolved.append(archive)
    # Verify everything before creating output. Destination must not already exist.
    for output in (destination, assemble_to):
        if output is not None and output.exists():
            raise FileExistsError(output)
    if destination is not None and assemble_to is not None and destination.resolve() == assemble_to.resolve():
        raise ValueError('Extraction and ZIP output directories must differ')
    if destination is not None:
        destination.mkdir(parents=True, exist_ok=False)
        for archive in resolved:
            with zipfile.ZipFile(archive) as z:
                z.extractall(destination / archive.stem)
    if assemble_to is not None:
        assemble_to.mkdir(parents=True, exist_ok=False)
        for archive in resolved:
            shutil.copyfile(archive, assemble_to / archive.name)
    return {'archives_verified': len(manifest['archives']), 'members_verified': count, 'result': 'PASS'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--extract-to', type=Path)
    parser.add_argument('--assemble-to', type=Path, help='Reconstruct the six original ZIP files in a new directory')
    args = parser.parse_args()
    print(json.dumps(verify(Path(__file__).resolve().parents[1], args.extract_to, args.assemble_to), indent=2))
