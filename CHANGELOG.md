# Changelog

All notable changes to this project are documented here.

## [Unreleased]

### Added
- C generator options `data_attributes`, `no_init` and `default_object` (`config.c_generator`):
  place the variables in a memory section (e.g. shared memory between cores), define them
  without initial values, and emit the defaults as a separate const object to initialise
  them from

### Fixed
- `printf` format warning in the TLV codec on 32-bit targets
- `schema.json` regenerated (it lacked the composite extension)

### Initial public release
- First public release of `odin`.
