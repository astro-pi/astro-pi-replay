from pathlib import Path
import os

from astro_pi_replay.resources.downloader import get_replay_dir


def collect_sequences() -> list[Path]:
    """
    Collects sequences in the {replay_dir}/VIS and {replay_dir}/IR
    directories.
    """
    replay_dir: Path = get_replay_dir()
    sequences: list[Path] = []
    for photography_type in os.listdir(replay_dir):
        sequences_root: Path = replay_dir / photography_type
        if not sequences_root.is_dir():
            continue  # skip files that are not directories
        sequence_id: str
        for sequence_id in os.listdir(sequences_root):
            # Upload the photos and videos separately
            sequence_base: Path = sequences_root / sequence_id
            sequences.append(sequence_base)
    return sequences
