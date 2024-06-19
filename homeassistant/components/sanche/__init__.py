"""The sanche-test integration."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import TrackStates, async_track_state_change_event
from homeassistant.components.recorder import history

from .const import DOMAIN

class HassEventListener:

    def __init__(self, hass: HomeAssistant):
        self.hass = hass
        self._listeners = set()
        self._cancel_fn = None
        self._state_store = {}

    @property
    def _is_running(self):
        return self._cancel_fn is not None

    def register_config_entry(self, entry: ConfigEntry):
        print(f"register_config_entry: {entry}")
        self._listeners.add(entry)
        self._update_listener()

    def remove_config_entry(self, entry: ConfigEntry):
        print(f"remove_config_entry: {entry}")
        self._listeners.remove(entry)
        self._update_listener()

    async def _handle_event(self, event):
        data_pt = StateChange(
            entity_id=event.data["entity_id"],
            new_state=event.data["new_state"].state,
            timestamp=event.time_fired_timestamp,
        )
        old_state = self._state_store.get(data_pt.entity_id, None)
        if data_pt.new_state != old_state:
            self._state_store[data_pt.entity_id] = data_pt.new_state
            print(f"State change: {event.data['entity_id']}: {event.data['new_state'].state} ({event.time_fired})")

    def _update_listener(self):
        if self._is_running:
            self._cancel_fn()
        all_entites = set()
        for entry in self._listeners:
            all_entites.update(entry.data["entities"])
        if all_entites:
            print(f"Listening to entities: {all_entites}")
            self._cancel_fn = async_track_state_change_event(self.hass, all_entites, self._handle_event)
        else:
            print("No entities to listen to")
            self._cancel_fn = None

@dataclass
class StateChange:
    entity_id: str
    new_state: str
    timestamp: float


event_listener = None

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up sanche-test from a config entry."""
    print("start setup entry")
    # history_dict = {}
    # for entity_id in entry.data["entities"]:
    #     print(entity_id)
    #     # https://github.com/home-assistant/core/blob/6a3778c48eb0db8cbc59406f27367646e4dbc7f3/homeassistant/components/recorder/history/__init__.py#L155
    #     entity_history = await hass.async_add_executor_job(history.state_changes_during_period, hass, (datetime.now()- timedelta(days=1)).astimezone(), datetime.now().astimezone(), entity_id, True)
    #     history_dict.update(entity_history)

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
