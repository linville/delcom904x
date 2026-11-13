## [Unreleased]
### Changed
- `delcom904x.list()` was changed to `delcom904x.list_devices()`.
- `delcom904x.info()` returns a dict rather than just printing to the console.
- Cleanly exit after listing devices.

### Fixed
- The MSB of the serial number was incorrectly parsed.
- The firmware version was incorrectly parsed.
- `--intensity 0` was ignored and would not adjust the intensity.

## [0.5.0]

## [0.4.0]

## [0.3.0]

## [0.2.1]

## [0.1.0]

[Unreleased]: https://github.com/linville/delcom904x/compare/v0.5.0...HEAD
[0.5.0]: https://github.com/linville/delcom904x/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/linville/delcom904x/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/linville/delcom904x/compare/v0.2.1...v0.3.0
[0.2.1]: https://github.com/linville/delcom904x/compare/v0.1.0...v0.2.1
[0.1.0]: https://github.com/linville/delcom904x/releases/tag/v0.1.0