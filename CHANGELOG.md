## [1.0.0] - 2026-11-13
### Added
- `delcom904x.__version__` exposes the installed package version.
- `--version` option for `control-delcom904x`.
- `--buzz [N]`, `--buzz-freq HZ` and `--silence` options for `control-delcom904x`.
- `DelcomMultiColorIndicator(reset=False)` attaches without turning off the LEDs and buzzer.

### Changed
- Colors are now the `delcom904x.Color` IntFlag (e.g. `Color.RED`), replacing the `green`, `red`, `blue` and `yellow` module constants.
- `delcom904x.list()` was changed to `delcom904x.list_devices()`.
- `delcom904x.info()` returns a dict rather than just printing to the console.
- Cleanly exit after listing devices.
- `enable_buzzer()` now takes keyword-only `frequency` (Hz), `on_ms`, `off_ms` and `repeat` arguments, validates their ranges and actually applies the frequency.
- `--buzzer` was replaced by `--buzz [N]`; buzzer options no longer require a color to be specified.
- `control-delcom904x` no longer resets the device on startup, so a running buzzer isn't silenced (use `--reset` explicitly).

### Fixed
- The MSB of the serial number was incorrectly parsed.
- The firmware version was incorrectly parsed.
- `--intensity 0` was ignored and would not adjust the intensity.

## [0.5.0] - 2025-03-25
- Improve closing of HID handle.
- Packaging improvements.

## [0.4.0] - 2023-08-10
- Minor naming, other changes.
- #1 Fix CLI throwing "No module named" error.

## [0.3.0] - 2021-04-07
- Minor naming, other changes.

## [0.2.1] - 2019-10-05
- Updated for Python 3. Packaged and uploaded to PyPi.

## [0.1.0] - 2014-12-15
- Initial release.

[Unreleased]: https://github.com/linville/delcom904x/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/linville/delcom904x/compare/v0.5.0...v1.0.0
[0.5.0]: https://github.com/linville/delcom904x/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/linville/delcom904x/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/linville/delcom904x/compare/v0.2.1...v0.3.0
[0.2.1]: https://github.com/linville/delcom904x/compare/v0.1.0...v0.2.1
[0.1.0]: https://github.com/linville/delcom904x/releases/tag/v0.1.0