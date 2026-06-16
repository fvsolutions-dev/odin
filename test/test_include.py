from pathlib import Path

import pytest

from odin_python.parameter.loader import ConfigurationReader
from odin_python.parameter.yaml_include import (
    OdinIncludeCycleError,
    OdinIncludeError,
    OdinIncludeNotFoundError,
    load_yaml_with_includes,
)


INCLUDE_DIR = Path(__file__).parent / "include_configs"


def test_main_config_with_includes_loads():
    main = INCLUDE_DIR / "main.yaml"
    model_context, _ = ConfigurationReader().load(main.as_posix(), "advanced")
    root = model_context.root_model
    names = {name for name in root.children}
    assert {"param_float", "device", "sensors"} <= names


def test_includes_are_resolved_relative_to_including_file(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    main = INCLUDE_DIR / "main.yaml"
    ConfigurationReader().load(main.as_posix(), "advanced")


def test_nested_include_expands():
    main = INCLUDE_DIR / "main.yaml"
    data = load_yaml_with_includes(main)
    temp = data["parameters"]["sensors"]["children"]["temperature"]
    assert temp["primitive"] == "f32"
    assert temp["local_id"] == 1


def test_scalar_include_substitutes_value():
    cfg = INCLUDE_DIR / "scalar_default.yaml"
    data = load_yaml_with_includes(cfg)
    assert data["parameters"]["param_float"]["default"] == pytest.approx(3.14)


def test_missing_include_raises_clear_error(tmp_path):
    parent = tmp_path / "parent.yaml"
    parent.write_text("id_space_shift: 8\nparameters: !include missing.yaml\n")
    with pytest.raises(OdinIncludeNotFoundError) as excinfo:
        load_yaml_with_includes(parent)
    msg = str(excinfo.value)
    assert "missing.yaml" in msg
    assert str(parent) in msg


def test_fragment_picks_subsection_from_shared_file():
    cfg = INCLUDE_DIR / "fragment.yaml"
    model_context, _ = ConfigurationReader().load(cfg.as_posix(), "advanced")
    children = model_context.root_model.children
    assert "enabled" in children["config"].children["driver"].children
    assert "reading" in children["data"].children["driver"].children


def test_fragment_drills_multiple_levels(tmp_path):
    driver = INCLUDE_DIR / "modules" / "driver.yaml"
    expected = load_yaml_with_includes(driver)["config"]["children"]["enabled"]
    parent = tmp_path / "parent.yaml"
    parent.write_text(f"deep: !include {driver}#config/children/enabled\n")
    assert load_yaml_with_includes(parent)["deep"] == expected


def test_fragment_missing_key_lists_available(tmp_path):
    parent = tmp_path / "parent.yaml"
    sub = tmp_path / "sub.yaml"
    sub.write_text("alpha: 1\nbeta: 2\n")
    parent.write_text("value: !include sub.yaml#gamma\n")
    with pytest.raises(OdinIncludeError) as excinfo:
        load_yaml_with_includes(parent)
    msg = str(excinfo.value)
    assert "gamma" in msg and "alpha" in msg and "beta" in msg


def test_fragment_into_non_mapping_errors(tmp_path):
    parent = tmp_path / "parent.yaml"
    sub = tmp_path / "sub.yaml"
    sub.write_text("alpha: 42\n")
    parent.write_text("value: !include sub.yaml#alpha/deeper\n")
    with pytest.raises(OdinIncludeError) as excinfo:
        load_yaml_with_includes(parent)
    assert "non-mapping" in str(excinfo.value)


def test_cycle_raises_with_chain(tmp_path):
    a = tmp_path / "a.yaml"
    b = tmp_path / "b.yaml"
    a.write_text("!include b.yaml\n")
    b.write_text("!include a.yaml\n")
    with pytest.raises(OdinIncludeCycleError) as excinfo:
        load_yaml_with_includes(a)
    msg = str(excinfo.value)
    assert "a.yaml" in msg and "b.yaml" in msg
