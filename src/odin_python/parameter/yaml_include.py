from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class OdinIncludeError(Exception):
    pass


class OdinIncludeNotFoundError(OdinIncludeError):
    pass


class OdinIncludeCycleError(OdinIncludeError):
    pass


class OdinIncludeLoader(yaml.SafeLoader):
    """PyYAML SafeLoader that resolves `!include <path>` against the including file."""

    _odin_current_dir: Path
    _odin_include_stack: tuple[Path, ...]


def _build_loader(current_dir: Path, include_stack: tuple[Path, ...]):
    def loader_factory(stream):
        loader = OdinIncludeLoader(stream)
        loader._odin_current_dir = current_dir
        loader._odin_include_stack = include_stack
        return loader

    return loader_factory


def _construct_include(loader: OdinIncludeLoader, node: yaml.Node) -> Any:
    if not isinstance(node, yaml.ScalarNode):
        raise OdinIncludeError(
            f"!include expects a scalar path, got {type(node).__name__} "
            f"at {node.start_mark}"
        )

    raw = loader.construct_scalar(node)
    if not isinstance(raw, str) or not raw:
        raise OdinIncludeError(f"!include requires a non-empty path at {node.start_mark}")

    raw_path, fragment = (raw.split("#", 1) + [""])[:2]
    if not raw_path:
        raise OdinIncludeError(f"!include requires a path before '#' at {node.start_mark}")

    target = (loader._odin_current_dir / raw_path).resolve()
    parent_file = loader._odin_include_stack[-1] if loader._odin_include_stack else None

    if not target.is_file():
        parent_str = f" (from {parent_file})" if parent_file else ""
        raise OdinIncludeNotFoundError(
            f"!include cannot find '{raw_path}' resolved to '{target}'"
            f"{parent_str} at {node.start_mark}"
        )

    if target in loader._odin_include_stack:
        chain = " -> ".join(str(p) for p in loader._odin_include_stack + (target,))
        raise OdinIncludeCycleError(f"!include cycle detected: {chain}")

    value = _load_file(target, loader._odin_include_stack)
    if fragment:
        value = _resolve_fragment(value, fragment, target, node.start_mark)
    return value


def _resolve_fragment(value: Any, fragment: str, source: Path, mark: yaml.Mark) -> Any:
    keys = [k for k in fragment.split("/") if k != ""]
    walked: list[str] = []
    for key in keys:
        if not isinstance(value, dict):
            walked_str = "/".join(walked) or "<root>"
            raise OdinIncludeError(
                f"!include fragment '{fragment}' cannot descend into non-mapping "
                f"at '{walked_str}' in '{source}' at {mark}"
            )
        if key not in value:
            available = ", ".join(sorted(value.keys())) or "(empty)"
            raise OdinIncludeError(
                f"!include fragment '{fragment}' key '{key}' not found in '{source}'; "
                f"available: {available} (at {mark})"
            )
        value = value[key]
        walked.append(key)
    return value


OdinIncludeLoader.add_constructor("!include", _construct_include)


def _load_file(path: Path, include_stack: tuple[Path, ...]) -> Any:
    new_stack = include_stack + (path,)
    factory = _build_loader(path.parent, new_stack)
    with path.open("r", encoding="utf-8") as handle:
        return yaml.load(handle, Loader=factory)  # noqa: S506 — custom SafeLoader subclass


def load_yaml_with_includes(file_path: str | Path) -> Any:
    """Load a YAML file, expanding `!include <path>` tags relative to each file."""
    root = Path(file_path).resolve()
    if not root.is_file():
        raise OdinIncludeNotFoundError(f"YAML file not found: {root}")
    return _load_file(root, ())
