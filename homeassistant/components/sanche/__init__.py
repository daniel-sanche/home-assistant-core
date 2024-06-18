"""The sanche-test integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN

class HassEventListener:

    def __init__(self, hass: HomeAssistant):
        self.hass = hass
        self._listeners = set()
        self._cancel_fn = None

    @property
    def _is_running(self):
        return self._cancel_fn is not None

    def register_config_entry(self, entry: ConfigEntry):
        print("register_config_entry")
        self._listeners.add(entry.entry_id)
        if not self._is_running:
            self._cancel_fn = self.hass.bus.async_listen("*", self._handle_event)

    def remove_config_entry(self, entry: ConfigEntry):
        print("remove_config_entry")
        self._listeners.remove(entry.entry_id)
        if not self._listeners:
            self._cancel_fn()
            self._cancel_fn = None

    async def _handle_event(self, event):
        print(f"Received event: {event}")

event_listener = None

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up sanche-test from a config entry."""
    print("start setup entry")

    hass.data.setdefault(DOMAIN, {})
    # TODO 1. Create API instance
    # TODO 2. Validate the API connection (and authentication)
    # TODO 3. Store an API object for your platforms to access
    # hass.data[DOMAIN][entry.entry_id] = MyApi(...)

    # await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    global event_listener
    if event_listener is None:
        event_listener = HassEventListener(hass)
    event_listener.register_config_entry(entry)

    print("end setup entry")
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    print("start unload entry")
    # if unload_ok := await hass.config_entries.async_unload_platforms(en:
    #     hass.data[DOMAIN].pop(entry.entry_id)

    if event_listener is not None:
        event_listener.remove_config_entry(entry)

    print("end unload entry")
    return True
