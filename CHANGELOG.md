# Changelog

All notable changes to this project are documented here.

## [Unreleased]

### Added
- C generator options `data_attributes`, `no_init` and `default_object` (`config.c_generator`):
  place the variables in a memory section (e.g. shared memory between cores), define them
  without initial values, and emit the defaults as a separate const object to initialise
  them from
- Arrays and vectors from a string (`ODIN_decode_string_to_parameter`): a text for elements of
  type char (the quotes optional), `[a, b]` for the others; custom elements still unsupported

### Fixed
- `printf` format warning in the TLV codec on 32-bit targets
- `schema.json` regenerated (it lacked the composite extension)

### Initial public release
- First public release of `odin`.
