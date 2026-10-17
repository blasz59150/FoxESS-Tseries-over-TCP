"""Sensors for FoxESS push telemetry."""

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import (
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
    UnitOfTemperature,
)
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import DeviceInfo

from . import SIGNAL_UPDATE
from .const import DOMAIN


SENSORS = [
    ("feed_in_power", "Feed-in Power", UnitOfPower.WATT, SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, 0),
    ("inverter_output_power", "Inverter Output Power", UnitOfPower.WATT, SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, 0),
    ("load_power", "Load Power", UnitOfPower.WATT, SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, 0),
    ("grid_voltage_r", "Grid Voltage R", UnitOfElectricPotential.VOLT, SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT, 1),
    ("grid_current_r", "Grid Current R", UnitOfElectricCurrent.AMPERE, SensorDeviceClass.CURRENT, SensorStateClass.MEASUREMENT, 1),
    ("grid_frequency_r", "Grid Frequency R", UnitOfFrequency.HERTZ, SensorDeviceClass.FREQUENCY, SensorStateClass.MEASUREMENT, 2),
    ("grid_power_r", "Grid Power R", UnitOfPower.WATT, SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, 0),
    ("grid_voltage_s", "Grid Voltage S", UnitOfElectricPotential.VOLT, SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT, 1),
    ("grid_current_s", "Grid Current S", UnitOfElectricCurrent.AMPERE, SensorDeviceClass.CURRENT, SensorStateClass.MEASUREMENT, 1),
    ("grid_frequency_s", "Grid Frequency S", UnitOfFrequency.HERTZ, SensorDeviceClass.FREQUENCY, SensorStateClass.MEASUREMENT, 2),
    ("grid_power_s", "Grid Power S", UnitOfPower.WATT, SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, 0),
    ("grid_voltage_t", "Grid Voltage T", UnitOfElectricPotential.VOLT, SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT, 1),
    ("grid_current_t", "Grid Current T", UnitOfElectricCurrent.AMPERE, SensorDeviceClass.CURRENT, SensorStateClass.MEASUREMENT, 1),
    ("grid_frequency_t", "Grid Frequency T", UnitOfFrequency.HERTZ, SensorDeviceClass.FREQUENCY, SensorStateClass.MEASUREMENT, 2),
    ("grid_power_t", "Grid Power T", UnitOfPower.WATT, SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, 0),
    ("pv1_voltage", "PV1 Voltage", UnitOfElectricPotential.VOLT, SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT, 1),
    ("pv1_current", "PV1 Current", UnitOfElectricCurrent.AMPERE, SensorDeviceClass.CURRENT, SensorStateClass.MEASUREMENT, 1),
    ("pv2_voltage", "PV2 Voltage", UnitOfElectricPotential.VOLT, SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT, 1),
    ("pv2_current", "PV2 Current", UnitOfElectricCurrent.AMPERE, SensorDeviceClass.CURRENT, SensorStateClass.MEASUREMENT, 1),
    ("pv3_voltage", "PV3 Voltage", UnitOfElectricPotential.VOLT, SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT, 1),
    ("pv3_current", "PV3 Current", UnitOfElectricCurrent.AMPERE, SensorDeviceClass.CURRENT, SensorStateClass.MEASUREMENT, 1),
    ("pv4_voltage", "PV4 Voltage", UnitOfElectricPotential.VOLT, SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT, 1),
    ("pv4_current", "PV4 Current", UnitOfElectricCurrent.AMPERE, SensorDeviceClass.CURRENT, SensorStateClass.MEASUREMENT, 1),
    ("boost_temperature", "Boost Temperature", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, 0),
    ("inverter_temperature", "Inverter Temperature", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, 0),
    ("ambient_temperature", "Ambient Temperature", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, 0),
    ("energy_today", "Energy Today", UnitOfEnergy.KILO_WATT_HOUR, SensorDeviceClass.ENERGY, SensorStateClass.TOTAL, 1),
    ("energy_total", "Energy Total", UnitOfEnergy.KILO_WATT_HOUR, SensorDeviceClass.ENERGY, SensorStateClass.TOTAL, 1),
]


class FoxESSSensor(SensorEntity):
    """Representation of one FoxESS sensor."""

    _attr_has_entity_name = True

    def __init__(self, hass, entry, runtime, description):
        """Initialize the sensor."""
        self.hass = hass
        self._runtime = runtime
        (
            self._key,
            self._name,
            self._unit,
            self._device_class,
            self._state_class,
            self._precision,
        ) = description

        self._attr_name = self._name
        self._attr_unique_id = f"{entry.entry_id}_{self._key}"
        self._attr_native_unit_of_measurement = self._unit
        self._attr_device_class = self._device_class
        self._attr_state_class = self._state_class
        self._attr_suggested_display_precision = self._precision
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="FoxESS T4-G3",
            manufacturer="FoxESS",
            model="T4-G3",
            configuration_url="https://github.com/blasz59150/foxess-tseries-over-tcp",
        )

    @property
    def native_value(self):
        """Return the latest value received from the inverter."""
        return self._runtime["values"].get(self._key)

    async def async_added_to_hass(self):
        """Subscribe to incoming telemetry."""
        await super().async_added_to_hass()
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, SIGNAL_UPDATE, self._handle_update
            )
        )

    def _handle_update(self, values):
        """Refresh the sensor after a new telemetry frame."""
        self.async_write_ha_state()


class FoxESSTimestampSensor(SensorEntity):
    """Expose the timestamp of the latest TCP or valid telemetry frame."""

    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(self, entry, runtime, key, name):
        self._entry = entry
        self._runtime = runtime
        self._key = key
        self._attr_name = name
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_entity_category = "diagnostic"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="FoxESS T4-G3", manufacturer="FoxESS", model="T4-G3",
            configuration_url="https://github.com/blasz59150/foxess-tseries-over-tcp",
        )

    @property
    def native_value(self):
        return self._runtime.get(self._key)

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        self.async_on_remove(async_dispatcher_connect(
            self.hass, f"{DOMAIN}_diagnostics", self._handle_update
        ))

    def _handle_update(self, _runtime):
        self.async_write_ha_state()


class FoxESSTCPDiagnosticsSensor(SensorEntity):
    """Summarize TCP status and recent diagnostic events in entity attributes."""

    _attr_has_entity_name = True
    _attr_name = "TCP Diagnostics"
    _attr_icon = "mdi:console"
    _attr_entity_category = "diagnostic"

    def __init__(self, entry, runtime):
        self._entry = entry
        self._runtime = runtime
        self._attr_unique_id = f"{entry.entry_id}_tcp_diagnostics"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="FoxESS T4-G3", manufacturer="FoxESS", model="T4-G3",
            configuration_url="https://github.com/blasz59150/foxess-tseries-over-tcp",
        )

    @property
    def native_value(self):
        return self._runtime.get("connection_state", "unknown")

    @property
    def extra_state_attributes(self):
        keys = (
            "last_tcp_data_iso", "last_valid_frame_iso", "last_update_iso",
            "last_attempt", "last_connected", "last_disconnect", "last_error",
            "reconnect_count", "bytes_received", "chunks_received", "frames_received",
            "valid_frames", "invalid_frames", "last_frame_length", "next_retry_in",
        )
        attributes = {key: self._runtime.get(key) for key in keys}
        attributes["recent_events"] = list(self._runtime.get("events", []))[-20:]
        return attributes

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        self.async_on_remove(async_dispatcher_connect(
            self.hass, f"{DOMAIN}_diagnostics", self._handle_update
        ))

    def _handle_update(self, _runtime):
        self.async_write_ha_state()


async def async_setup_entry(hass, entry, async_add_entities):
    runtime = hass.data[DOMAIN][entry.entry_id]
    entities = [FoxESSSensor(hass, entry, runtime, description) for description in SENSORS]
    entities.extend([
        FoxESSTimestampSensor(entry, runtime, "last_tcp_data", "Last TCP Packet"),
        FoxESSTimestampSensor(entry, runtime, "last_valid_frame", "Last Valid Frame"),
        FoxESSTCPDiagnosticsSensor(entry, runtime),
    ])
    async_add_entities(entities)
