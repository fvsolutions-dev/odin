import pytest
from odin_python.data_types.type_registry import (
    TypeRegistry,
    RegularCDataType,
    BASE_DATA_TYPES,
)


def test_type_registry_init():
    registry = TypeRegistry()
    assert registry.types == {}


def test_register_single_type():
    registry = TypeRegistry()
    data_type = RegularCDataType(typename="test_type", size=4, c_typename="int")
    registry.register(data_type)
    assert "test_type" in registry.types
    assert registry.types["test_type"] == data_type


def test_register_multiple_types():
    registry = TypeRegistry()
    registry.register(BASE_DATA_TYPES)
    for data_type in BASE_DATA_TYPES:
        assert data_type.typename in registry.types
        assert registry.types[data_type.typename] == data_type


def test_register_duplicate_type():
    registry = TypeRegistry()
    data_type = RegularCDataType(typename="test_type", size=4, c_typename="int")
    registry.register(data_type)
    with pytest.raises(ValueError, match="Type .* already registered"):
        registry.register(data_type)


def test_get_type():
    registry = TypeRegistry()
    data_type = RegularCDataType(typename="test_type", size=4, c_typename="int")
    registry.register(data_type)
    retrieved_type = registry.get_type("test_type")
    assert retrieved_type == data_type


def test_get_nonexistent_type():
    registry = TypeRegistry()
    with pytest.raises(ValueError, match="Type .* not found"):
        registry.get_type("nonexistent_type")
