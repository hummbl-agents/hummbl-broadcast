"""Config defaults — TOML section scope + cross-platform paths.

Addresses §6 I3 (PowerShell Set-Location), I4 (TOML section-header confusion),
and the second-class bug that was missed: kill_switch sentinel_path hardcoded
to /tmp/... (Windows: C:\\tmp\\... which doesn't exist).
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from hummbl_broadcast.config import (
    AdapterConfig,
    Config,
    KillSwitchConfig,
    PublisherConfig,
)


def test_default_kill_switch_path_is_platform_correct():
    """The default sentinel_path must resolve to a directory that exists on this OS."""
    cfg = KillSwitchConfig()
    p = Path(cfg.sentinel_path)
    # Parent dir must exist (or be creatable)
    assert p.parent.exists() or p.parent.parent.exists()
    # And the path must point at the platform-correct temp dir, NOT /tmp/
    assert p.parent == Path(tempfile.gettempdir()), (
        f"default sentinel parent {p.parent} != platform tempdir {tempfile.gettempdir()}"
    )


def test_default_publisher_output_dir_is_platform_correct():
    cfg = PublisherConfig()
    p = Path(cfg.output_dir)
    assert p.parent == Path(tempfile.gettempdir())


def test_top_level_keys_after_section_header_land_on_root():
    """TOML doesn't reset section scope with comments — only with [section] headers.
    Top-level keys placed AFTER a [section] header would silently nest into that section.
    This test documents the GOTCHA so contributors don't reintroduce the bug from ee8d68f.
    """
    import tomllib

    bad_toml = b"""
[adapter]
name = "mock"

[publisher]
mode = "file"

# BUG: these would silently nest under [publisher], NOT land on root.
# Workaround: always put top-level keys BEFORE any [section] header.
brand_overlay_path = ""
prompts_path = "p.jsonl"
"""
    bad_data = tomllib.loads(bad_toml.decode())
    # Document the bug: yes, they DO nest. Test asserts the failure mode so
    # a future contributor is alerted when they see this pattern.
    assert "brand_overlay_path" in bad_data.get("publisher", {}), (
        "Expected: top-level keys after a [section] header nest into that section. "
        "If this fails, TOML semantics changed; update the fix in examples/*.toml."
    )

    good_toml = b"""
brand_overlay_path = ""
prompts_path = "p.jsonl"

[adapter]
name = "mock"

[publisher]
mode = "file"
"""
    good_data = tomllib.loads(good_toml.decode())
    # And the correct pattern puts them at root.
    assert good_data.get("brand_overlay_path") == ""
    assert good_data.get("prompts_path") == "p.jsonl"
    assert "brand_overlay_path" not in good_data.get("publisher", {})


def test_config_loads_with_all_top_level_keys():
    """Full Config() must accept every top-level key from the TOML schema."""
    cfg = Config()
    assert hasattr(cfg, "adapter")
    assert hasattr(cfg, "cost")
    assert hasattr(cfg, "buffer")
    assert hasattr(cfg, "publisher")
    assert hasattr(cfg, "kill_switch")
    assert hasattr(cfg, "brand_overlay_path")
    assert hasattr(cfg, "prompts_path")
    assert hasattr(cfg, "receipts_path")
    assert hasattr(cfg, "dry_run")


def test_load_example_configs():
    """Both shipped example configs must load without exception.
    Regression test for the TOML-null bug fixed in ee8d68f.
    """
    examples = Path(__file__).parent.parent / "examples"
    for name in ("config.mock.toml", "config.minimax.toml"):
        path = examples / name
        if not path.exists():
            pytest.skip(f"{path} not present")
        cfg = Config.from_file(path)
        # Must have populated the top-level keys correctly
        assert cfg.prompts_path.endswith(".jsonl")
        assert cfg.receipts_path.endswith(".jsonl")
        assert isinstance(cfg.dry_run, bool)
        # And the kill_switch section must exist
        assert isinstance(cfg.kill_switch.sentinel_path, str)
        assert cfg.kill_switch.sentinel_path  # not empty
