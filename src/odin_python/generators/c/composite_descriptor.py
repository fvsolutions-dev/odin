"""Runtime composite (struct field-layout) descriptors for CUSTOM types.

For every CUSTOM-typed parameter the C codegen emits, once per type (deduped by
c_typename), an ODIN_type_descriptor_t plus its ODIN_field_descriptor_t[] array,
and attaches an ODIN_EXTENSION_TYPE_COMPOSITE extension pointing at it. This lets
the runtime (and the self-describing odin-stream) break a struct into its named,
typed fields without any external schema.
"""

import struct

from ...data_types.type_registry import CustomDataType
from .odin_defs import ODIN_ElementTypeEnum

# Prefix for the generated per-type descriptor symbols.
DESCRIPTOR_PREFIX = "odin_typedesc_"


def descriptor_symbol(custom_type: CustomDataType) -> str:
    """Stable C symbol for a custom type's descriptor (deduped by c_typename)."""
    return f"{DESCRIPTOR_PREFIX}{custom_type.c_typename}"


def crc16_ccitt(data: bytes) -> int:
    """CRC16-CCITT (poly 0x1021, init 0xFFFF) — deterministic 16-bit type id."""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return crc


def type_id(type_name: str) -> int:
    """Stable 16-bit id derived from the source-YAML type name."""
    return crc16_ccitt(type_name.encode("utf-8"))


def _fields(custom_type: CustomDataType):
    """Yield (name, element_type_enum, size, offset) for each struct field.

    Offsets are derived from struct.calcsize of the packed prefix, so they match
    the wire/struct layout exactly even if a field is itself composite. Fields
    that are themselves custom types are tagged ODIN_ELEMENT_TYPE_CUSTOM.

    TODO(nested): nested-struct fields are tagged CUSTOM but their own nested
    field layout is not emitted here; the wire can later resolve them by type_id
    once the referenced type's descriptor (also emitted) carries that id.
    """
    model = custom_type.model
    if not isinstance(model.root, dict):
        return

    running_format = "<"
    for field_name, field_model in model.to_flat_dict(depth=0).items():
        offset = struct.calcsize(running_format)
        field_type = field_model.root
        c_typename = getattr(field_type, "c_typename", None)
        if field_model.is_custom or c_typename is None:
            element_type = ODIN_ElementTypeEnum.ODIN_ELEMENT_TYPE_CUSTOM
        else:
            element_type = ODIN_ElementTypeEnum.from_c_type(c_typename)

        yield field_name, element_type, field_model.size, offset
        running_format += f"{field_model.elements}{field_model.struct_format(depth=-1)}"


def emit_descriptor(custom_type: CustomDataType) -> str:
    """Return the C definition (fields array + descriptor) for a custom type."""
    symbol = descriptor_symbol(custom_type)
    fields = list(_fields(custom_type))

    lines: list[str] = []
    if fields:
        lines.append(f"static const ODIN_field_descriptor_t {symbol}_fields[] = {{")
        for name, element_type, size, offset in fields:
            lines.append(f'    {{ "{name}", {element_type.value}, {size}, {offset} }},')
        lines.append("};")
        fields_ref = f"{symbol}_fields"
    else:
        # No primitive fields (e.g. an opaque/forward custom type); keep a valid
        # descriptor with a NULL field array and zero count.
        fields_ref = "NULL"

    tid = type_id(custom_type.typename)
    lines.append(f"static const ODIN_type_descriptor_t {symbol} = {{")
    lines.append(
        f'    "{custom_type.typename}", 0x{tid:04X} /*type_id*/, '
        f"{custom_type.size} /*size*/, {len(fields)} /*field_count*/, {fields_ref},"
    )
    lines.append("};")
    return "\n".join(lines)
