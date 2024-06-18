"""Config flow for sanche-test."""
# import my_pypi_dependency

import logging

import voluptuous as vol

from homeassistant import config_entries

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def validate_input(hass, data):
    pass


class ExampleConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            try:
                await validate_input(self.hass, user_input)
                return self.async_create_entry(title=user_input["url"], data=user_input)
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
        result = self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {vol.Required("password"): str, vol.Required("url"): str}
            ),
            errors=errors,
        )
        return result
