"""The sanche-test integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up sanche-test from a config entry."""
    print("start setup entry")

    hass.data.setdefault(DOMAIN, {})
    # TODO 1. Create API instance
    # TODO 2. Validate the API connection (and authentication)
    # TODO 3. Store an API object for your platforms to access
    # hass.data[DOMAIN][entry.entry_id] = MyApi(...)

    # await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Listener to handle fired events
    async def handle_event(event):
        print(f"Received event: {event}")

    # Listen for when example_component_my_cool_event is fired
    hass.bus.async_listen("*", handle_event)

    print("end setup entry")
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    print("start unload entry")
    # if unload_ok := await hass.config_entries.async_unload_platforms(en:
    #     hass.data[DOMAIN].pop(entry.entry_id)

    print("end unload entry")
    return True
