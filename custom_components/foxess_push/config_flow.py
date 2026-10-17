"""Config and options flow for FoxESS Tseries over TCP."""

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

from .const import (
    DEFAULT_HOST,
    DEFAULT_OFFLINE_AFTER,
    DEFAULT_PORT,
    DEFAULT_RECONNECT_DELAY,
    DEFAULT_NO_DATA_TIMEOUT,
    DOMAIN,
    MAX_OFFLINE_AFTER,
    MAX_RECONNECT_DELAY,
    MAX_TIMEOUT,
    MIN_OFFLINE_AFTER,
    MIN_RECONNECT_DELAY,
    MIN_TIMEOUT,
    OPT_NO_DATA_TIMEOUT,
    OPT_OFFLINE_AFTER,
    OPT_RECONNECT_DELAY,
)


class FoxESSPushConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle initial setup."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Set up the TCP gateway connection."""
        errors = {}
        if user_input is not None:
            host = user_input["host"].strip()
            port = user_input["port"]
            if not host:
                errors["host"] = "required"
            else:
                await self.async_set_unique_id(f"{host}:{port}")
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title="FoxESS Tseries over TCP",
                    data={"host": host, "port": port},
                )

        schema = vol.Schema(
            {
                vol.Required("host", default=DEFAULT_HOST): str,
                vol.Required("port", default=DEFAULT_PORT): vol.All(
                    int, vol.Range(min=1, max=65535)
                ),
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return FoxESSPushOptionsFlow(config_entry)


class FoxESSPushOptionsFlow(config_entries.OptionsFlow):
    """Manage reconnect and availability timing without editing code."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options = self.config_entry.options
        schema = vol.Schema(
            {
                vol.Required(
                    OPT_NO_DATA_TIMEOUT,
                    default=options.get(OPT_NO_DATA_TIMEOUT, DEFAULT_NO_DATA_TIMEOUT),
                ): vol.All(int, vol.Range(min=MIN_TIMEOUT, max=MAX_TIMEOUT)),
                vol.Required(
                    OPT_RECONNECT_DELAY,
                    default=options.get(OPT_RECONNECT_DELAY, DEFAULT_RECONNECT_DELAY),
                ): vol.All(
                    int,
                    vol.Range(min=MIN_RECONNECT_DELAY, max=MAX_RECONNECT_DELAY),
                ),
                vol.Required(
                    OPT_OFFLINE_AFTER,
                    default=options.get(OPT_OFFLINE_AFTER, DEFAULT_OFFLINE_AFTER),
                ): vol.All(
                    int,
                    vol.Range(min=MIN_OFFLINE_AFTER, max=MAX_OFFLINE_AFTER),
                ),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
