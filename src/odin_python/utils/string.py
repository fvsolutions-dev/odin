REPLACE_DICT = {
    "\\": "\\\\",  # must run first so the escapes we add below aren't re-escaped
    '"': '\\"',
    "\n": "\\n",
    "\t": "\\t",
    "\r": "\\r",
}


def escape_string(s: str) -> str:
    """Escape a string for use in a C string literal."""
    # dict preserves insertion order: backslash first, then the rest.
    for k, v in REPLACE_DICT.items():
        s = s.replace(k, v)
    return s


def c_name_and_description(name: str, description: str) -> str:
    r"""Build the name_and_description C initialiser: name, a NUL, then the
    description. Emitted as three adjacent string literals — "name" "\0" "desc"
    — NOT one literal "name\0desc". A single literal breaks when the description
    starts with a digit: C parses the `\0` plus that digit as one octal escape
    (e.g. `\07` -> 0x07), swallowing the terminator and the digit, so the dump
    prints the description fused onto the name. Adjacent literals concatenate
    after each is escaped independently, keeping the NUL intact."""
    return f'"{escape_string(name)}" "\\0" "{escape_string(description)}"'
