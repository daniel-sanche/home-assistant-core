"""Config flow for sanche-test."""
# import my_pypi_dependency

import voluptuous as vol

from homeassistant import config_entries

from .const import DOMAIN


class ExampleConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None):
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {vol.Required("password"): str, vol.Required("url"): str}
            ),
        )
