<p align="center"><img src="assets/icon.png" alt="FoxESS Tseries over TCP" width="820"></p>

# FoxESS Tseries over TCP

**A community Home Assistant custom integration for receiving local FoxESS T-series telemetry over TCP.** Maintained by `blasz59150`. This is not an official FoxESS or Home Assistant product.

[GitHub repository](https://github.com/blasz59150/foxess-tseries-over-tcp) · [Issues](https://github.com/blasz59150/foxess-tseries-over-tcp/issues) · [Polski README](README_PL.md) · [GPL-3.0-or-later](LICENSE)

## Project status

Source package version `1.1.0`. The code and documentation are prepared for review, but **this does not mean it has been tested against a live inverter or approved by HACS**. Do not represent it as a validated release until it has been checked in the target Home Assistant installation.

## Implemented in source

- UI-based TCP host and port setup;
- configurable no-data timeout, reconnect delay and OFFLINE threshold;
- FoxESS push frame reception and decoding of selected telemetry fields;
- entities for power, energy, grid phases, PV strings and temperatures;
- Online state, last TCP data timestamp, last valid frame timestamp and TCP Diagnostics entity;
- bounded in-memory connection event history;
- example YAML dashboard.

### Known limitations

- CRC16 is not currently validated.
- `Last TCP Packet` is the timestamp of the most recent TCP data chunk, not a stored raw packet dump.
- Diagnostics do not guarantee detection of every transmission error or every lost frame.
- Entity IDs may vary with the Home Assistant entity registry.
- Compatibility with every model and firmware version has not been confirmed.

## Quick start

1. Copy `custom_components/foxess_push/` to `/config/custom_components/foxess_push/`.
2. Restart Home Assistant.
3. Go to **Settings → Devices & services → Add integration → FoxESS Tseries over TCP**.
4. Enter the gateway IP address and TCP port. The reference setup uses `192.168.0.69:502`; use your own values.
5. Adjust reconnect options if needed.
6. Import/copy `dashboards/foxess_tcp.yaml` and adapt entity IDs.

**Detailed guides (Polish):** [Hardware](docs/HARDWARE_PL.md) · [EBYTE network setup](docs/NETWORK_AND_GATEWAY_PL.md) · [Software installation](docs/SOFTWARE_INSTALL_PL.md) · [Protocol notes](docs/PROTOCOL_AND_RESEARCH_PL.md).

## Reference hardware

| Item | Reference value |
|---|---|
| Inverter | FoxESS T4-G3 |
| Gateway | EBYTE NE2-D11 RS485-to-Ethernet |
| Gateway mode | TCP Server |
| TCP port | `502` |
| UART | `9600 8N1` |
| Pack Time / Pack Length | `1` / `1024` |

These are settings from one installation, not universal requirements. Pin numbers and wire colours are intentionally omitted until verified against the exact hardware revision. TCP port `502` does not mean this telemetry stream is standard Modbus TCP.

## Dashboard and HACS

The example dashboard is [`dashboards/foxess_tcp.yaml`](dashboards/foxess_tcp.yaml); check entity IDs before use. The repository includes `hacs.json`, but this is not proof of HACS approval. Manual installation is the documented method until current HACS requirements are verified.

## Authorship and license

Distributed under the [GNU General Public License v3 or later](LICENSE). GPL does not prevent copying; it requires compliance with its terms when distributing covered copies and modifications, including appropriate source-code availability. Preserve attribution, change history and provenance.

Maintainer: `blasz59150` · [AUTHORS](AUTHORS.md) · [CHANGELOG](CHANGELOG.md) · [SECURITY](SECURITY.md)

## Safety

Do not expose the gateway port to the public internet. Do not work inside the inverter without appropriate qualifications. Remove private network details from logs before sharing.
