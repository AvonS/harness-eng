"""Move legacy per-feature lifecycle directories to phase-level state."""

import shutil
from pathlib import Path


def migrate_phase_layout(harness_root: Path, dry_run: bool = False) -> list[tuple[Path, Path]]:
    phases = harness_root / "phases"
    moves: list[tuple[Path, Path]] = []
    if not phases.is_dir():
        return moves
    plans = []
    for phase in sorted(phases.iterdir()):
        if not phase.is_dir() or phase.name in {"active", "archive"}:
            continue
        features = phase / "features"
        active = features / "active"
        completed = features / "done"
        if not completed.is_dir():
            completed = features / "archive"
        active_items = sorted(active.iterdir()) if active.is_dir() else []
        completed_items = sorted(completed.iterdir()) if completed.is_dir() else []
        state = "active" if active_items or not completed_items else "archive"
        destination = phases / state / phase.name
        if destination.exists():
            raise FileExistsError(f"phase migration collision: {destination}")
        names = [item.name for item in active_items + completed_items]
        if len(names) != len(set(names)):
            raise FileExistsError(f"duplicate legacy feature in phase: {phase.name}")
        plans.append((phase, destination, active_items + completed_items))

    for phase, destination, items in plans:
        if dry_run:
            moves.append((phase, destination)); continue
        (destination / "features").mkdir(parents=True)
        if (phase / "PHASE.md").is_file():
            shutil.move(str(phase / "PHASE.md"), str(destination / "PHASE.md"))
        for item in items:
            target = destination / "features" / item.name
            if target.exists():
                raise FileExistsError(f"feature migration collision: {target}")
            shutil.move(str(item), str(target))
        shutil.rmtree(phase)
        moves.append((phase, destination))
    return moves
