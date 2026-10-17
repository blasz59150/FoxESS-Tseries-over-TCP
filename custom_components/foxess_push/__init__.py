"""FoxESS Tseries telemetry over a local TCP push connection."""

import asyncio
import logging
from datetime import datetime, timezone

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_send

from .const import (
    DEFAULT_NO_DATA_TIMEOUT,
    DEFAULT_RECONNECT_DELAY,
    DOMAIN,
    FRAME_END,
    FRAME_HEADER,
    FUNCTION_REALTIME,
    EXPECTED_REALTIME_LENGTH,
    MAX_DIAGNOSTIC_EVENTS,
    OPT_NO_DATA_TIMEOUT,
    OPT_RECONNECT_DELAY,
)

_LOGGER = logging.getLogger(__name__)
SIGNAL_UPDATE = f"{DOMAIN}_update"
SIGNAL_DIAGNOSTICS = f"{DOMAIN}_diagnostics"


def _now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _event(runtime: dict, message: str, level: str = "info"):
    """Keep a small in-memory event history for diagnostics."""
    events = runtime.setdefault("events", [])
    events.append({"time": _now_iso(), "level": level, "message": message})
    del events[:-MAX_DIAGNOSTIC_EVENTS]


def _extract_frames(buffer: bytearray):
    """Extract complete framed messages from a byte stream."""
    frames = []
    while True:
        start = buffer.find(FRAME_HEADER)
        if start < 0:
            buffer[:] = buffer[-1:] if buffer.endswith(FRAME_HEADER[:1]) else b""
            break
        if start:
            del buffer[:start]
        if len(buffer) < 9:
            break
        payload_length = int.from_bytes(buffer[7:9], "big")
        frame_length = 13 + payload_length
        if frame_length > 4096:
            del buffer[0]
            continue
        if len(buffer) < frame_length:
            break
        if buffer[frame_length - 2:frame_length] != FRAME_END:
            del buffer[0]
            continue
        frames.append(bytes(buffer[:frame_length]))
        del buffer[:frame_length]
    return frames


def _decode_realtime(frame: bytes):
    """Decode the known realtime payload layout. CRC validation is not implemented yet."""
    if len(frame) < 13 or frame[2] != FUNCTION_REALTIME:
        return None
    payload_length = int.from_bytes(frame[7:9], "big")
    if payload_length != EXPECTED_REALTIME_LENGTH or len(frame) != 13 + payload_length:
        return None
    data = frame[9:9 + payload_length]

    def u16(offset):
        return int.from_bytes(data[offset:offset + 2], "big")

    def s16(offset):
        return int.from_bytes(data[offset:offset + 2], "big", signed=True)

    def s32(offset):
        return int.from_bytes(data[offset:offset + 4], "big", signed=True)

    def u32(offset):
        return int.from_bytes(data[offset:offset + 4], "big")

    return {
        "feed_in_power": s32(0), "inverter_output_power": s32(4), "load_power": s32(8),
        "grid_voltage_r": u16(12) / 10, "grid_current_r": s16(14) / 10,
        "grid_frequency_r": u16(16) / 100, "grid_power_r": s16(18),
        "grid_voltage_s": u16(20) / 10, "grid_current_s": s16(22) / 10,
        "grid_frequency_s": u16(24) / 100, "grid_power_s": s16(26),
        "grid_voltage_t": u16(28) / 10, "grid_current_t": s16(30) / 10,
        "grid_frequency_t": u16(32) / 100, "grid_power_t": s16(34),
        "pv1_voltage": u16(36) / 10, "pv1_current": u16(38) / 10,
        "pv2_voltage": u16(42) / 10, "pv2_current": u16(44) / 10,
        "pv3_voltage": u16(48) / 10, "pv3_current": u16(50) / 10,
        "pv4_voltage": u16(54) / 10, "pv4_current": u16(56) / 10,
        "boost_temperature": s16(60), "inverter_temperature": s16(62),
        "ambient_temperature": s16(64), "energy_today": u16(66) / 10,
        "energy_total": u32(68) / 10,
    }


async def _notify_diagnostics(hass: HomeAssistant, runtime: dict):
    async_dispatcher_send(hass, SIGNAL_DIAGNOSTICS, dict(runtime))


async def _listener(hass: HomeAssistant, entry: ConfigEntry, runtime: dict):
    """Maintain the TCP stream and reconnect after timeout or disconnect."""
    host = entry.data["host"]
    port = entry.data["port"]
    while True:
        writer = None
        runtime["connection_state"] = "connecting"
        runtime["last_attempt"] = _now_iso()
        _event(runtime, f"Łączenie z bramką {host}:{port}")
        await _notify_diagnostics(hass, runtime)
        try:
            reader, writer = await asyncio.open_connection(host, port)
            runtime["connection_state"] = "connected"
            runtime["last_connected"] = _now_iso()
            runtime["last_error"] = ""
            _event(runtime, f"Połączono z {host}:{port}")
            _LOGGER.info("Connected to FoxESS gateway at %s:%s", host, port)
            await _notify_diagnostics(hass, runtime)
            buffer = bytearray()
            timeout = int(entry.options.get(OPT_NO_DATA_TIMEOUT, DEFAULT_NO_DATA_TIMEOUT))
            while True:
                try:
                    chunk = await asyncio.wait_for(reader.read(4096), timeout=timeout)
                except asyncio.TimeoutError as err:
                    raise TimeoutError(f"No TCP data received from FoxESS gateway for {timeout} seconds") from err
                if not chunk:
                    raise ConnectionError("Gateway closed the TCP connection")

                now = datetime.now(timezone.utc)
                runtime["last_tcp_data"] = now
                runtime["last_tcp_data_iso"] = now.isoformat(timespec="seconds")
                runtime["bytes_received"] = runtime.get("bytes_received", 0) + len(chunk)
                runtime["chunks_received"] = runtime.get("chunks_received", 0) + 1
                buffer.extend(chunk)
                frames = _extract_frames(buffer)
                runtime["frames_received"] = runtime.get("frames_received", 0) + len(frames)
                valid_count = 0
                for frame in frames:
                    values = _decode_realtime(frame)
                    if values is None:
                        runtime["invalid_frames"] = runtime.get("invalid_frames", 0) + 1
                        continue
                    valid_count += 1
                    runtime["last_valid_frame"] = now
                    runtime["last_valid_frame_iso"] = now.isoformat(timespec="seconds")
                    runtime["valid_frames"] = runtime.get("valid_frames", 0) + 1
                    runtime["last_frame_length"] = len(frame)
                    runtime["values"].update(values)
                    runtime["last_update"] = now
                    runtime["last_update_iso"] = now.isoformat(timespec="seconds")
                    runtime["connection_state"] = "connected"
                    async_dispatcher_send(hass, SIGNAL_UPDATE, dict(runtime["values"]))
                    async_dispatcher_send(hass, f"{DOMAIN}_availability", now)
                if valid_count:
                    _event(runtime, f"Odebrano {valid_count} poprawną ramkę/ramki telemetryczne")
                await _notify_diagnostics(hass, runtime)
        except asyncio.CancelledError:
            raise
        except Exception as err:
            runtime["connection_state"] = "disconnected"
            runtime["last_error"] = f"{type(err).__name__}: {err}"
            runtime["last_disconnect"] = _now_iso()
            runtime["reconnect_count"] = runtime.get("reconnect_count", 0) + 1
            _event(runtime, runtime["last_error"], "warning")
            _LOGGER.warning("FoxESS TCP issue: %s; reconnecting", runtime["last_error"])
            await _notify_diagnostics(hass, runtime)
        finally:
            if writer is not None:
                writer.close()
                try:
                    await writer.wait_closed()
                except Exception:
                    pass
        delay = int(entry.options.get(OPT_RECONNECT_DELAY, DEFAULT_RECONNECT_DELAY))
        runtime["connection_state"] = "waiting_to_reconnect"
        runtime["next_retry_in"] = delay
        await _notify_diagnostics(hass, runtime)
        await asyncio.sleep(delay)


async def async_setup(hass: HomeAssistant, config: dict):
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    runtime = {
        "values": {}, "last_update": None, "last_update_iso": "",
        "last_tcp_data": None, "last_tcp_data_iso": "",
        "last_valid_frame": None, "last_valid_frame_iso": "",
        "connection_state": "starting", "last_error": "", "last_attempt": "",
        "last_connected": "", "last_disconnect": "", "reconnect_count": 0,
        "bytes_received": 0, "chunks_received": 0, "frames_received": 0,
        "valid_frames": 0, "invalid_frames": 0, "last_frame_length": 0,
        "next_retry_in": 0, "events": [],
    }
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = runtime
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor", "binary_sensor"])
    runtime["task"] = hass.async_create_background_task(
        _listener(hass, entry, runtime), name="FoxESS TCP listener"
    )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    runtime = hass.data.get(DOMAIN, {}).get(entry.entry_id, {})
    task = runtime.get("task")
    if task is not None:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
    unloaded = await hass.config_entries.async_unload_platforms(entry, ["sensor", "binary_sensor"])
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Reload the integration when timing options change."""
    await hass.config_entries.async_reload(entry.entry_id)
