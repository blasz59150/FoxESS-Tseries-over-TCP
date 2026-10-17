"""Connectivity entity for FoxESS TCP."""

from datetime import datetime, timedelta, timezone

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.event import async_track_time_interval

from .const import DEFAULT_OFFLINE_AFTER, DOMAIN, OPT_OFFLINE_AFTER

STATE_REFRESH_SECONDS = 5


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    runtime = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([FoxessOnlineSensor(entry, runtime)])


class FoxessOnlineSensor(BinarySensorEntity):
    _attr_has_entity_name = True
    _attr_name = "Online"
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_icon = "mdi:lan-connect"

    def __init__(self, entry: ConfigEntry, runtime: dict):
        self._entry = entry
        self._runtime = runtime
        self._attr_unique_id = f"{entry.entry_id}_online"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name="FoxESS T4-G3", manufacturer="FoxESS", model="T4-G3",
            configuration_url="https://github.com/blasz59150/foxess-tseries-over-tcp",
        )

    @property
    def is_on(self) -> bool:
        last_update = self._runtime.get("last_update")
        if last_update is None:
            return False
        offline_after = int(self._entry.options.get(OPT_OFFLINE_AFTER, DEFAULT_OFFLINE_AFTER))
        return (datetime.now(timezone.utc) - last_update).total_seconds() < offline_after

    async def async_added_to_hass(self):
        self.async_on_remove(async_dispatcher_connect(
            self.hass, f"{DOMAIN}_availability", self._handle_availability
        ))
        cancel = async_track_time_interval(
            self.hass, self._refresh_state, timedelta(seconds=STATE_REFRESH_SECONDS)
        )
        self.async_on_remove(cancel)

    @callback
    def _handle_availability(self, _last_update):
        self.async_write_ha_state()

    @callback
    def _refresh_state(self, _now):
        self.async_write_ha_state()
