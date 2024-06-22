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

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        self.hass = hass
        self.entities = entry.data["entities"]
        self._cancel_fn = None
        self._state_store: dict[str, StateChange] = {}
        self.start()


    def start(self):
        if not self._is_running:
            self._cancel_fn = async_track_state_change_event(self.hass, self.entities, self._handle_event)

    def stop(self):
        if self._is_running:
            self._cancel_fn()
            self._cancel_fn = None

    @property
    def _is_running(self):
        return self._cancel_fn is not None

    async def _handle_event(self, event):
        # data_pt = StateChange(
        #     entity_id=event.data["entity_id"],
        #     new_state=event.data["new_state"].state,
        #     timestamp=event.time_fired_timestamp,
        # )
        # old_state = self._state_store.get(data_pt.entity_id, None)
        # if data_pt.new_state != old_state:
        #     self._state_store[data_pt.entity_id] = data_pt.new_state
        print(f"State change: {event.data['entity_id']}: {event.data['new_state'].state} ({event.time_fired})")

@dataclass
class StateChange:
    entity_id: str
    new_state: str
    timestamp: float


event_listener = None
lisner_store : dict[ConfigEntry, HassEventListener] = {}

PLATFORMS = ["binary_sensor"]

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

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    if lisner_store.get(entry):
        lisner_store[entry].stop()
    lisner_store[entry] = HassEventListener(hass, entry)

    print("end setup entry")
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    print("start unload entry")
    # await hass.config_entries.async_forward_entry_unload(entry, PLATFORMS)

    if lisner_store.get(entry):
        lisner_store[entry].stop()
        lisner_store.pop(entry)

    print("end unload entry")
    return True
