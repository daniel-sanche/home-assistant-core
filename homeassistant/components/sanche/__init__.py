"""The sanche-test integration."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from functools import partial
import requests

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import TrackStates, async_track_state_change_event
from homeassistant.components.recorder import history
import homeassistant.util.dt as dt_util

from .binary_sensor import HostReachableSensor
from .sensor import LastUpdateSensor
from .const import DOMAIN

class HassEventListener:

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, heartbeat_minutes=5):
        self.hass = hass
        self.host = entry.data["url"]
        self.password = entry.data["password"]
        self.entities = entry.data["entities"]
        self._cancel_fn = None
        self._event_queue = []
        self.owned_entities = []
        self.last_response = None
        self.last_packet_time = None
        self.host_reachable_sensor = HostReachableSensor(entry, self)
        self.last_update_sensor = LastUpdateSensor(entry, self)
        # create a regular polling timer to send heartbeat
        self.hass.helpers.event.async_track_time_interval(self._heartbeat, timedelta(minutes=heartbeat_minutes))

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

    async def restore_last_update_time(self) -> bool:
        """
        Restore the last_update_time from the history database.

        last_update_time represents the last time we communicated with the host.
        """
        # should be run after: hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
        state_dict = await self.hass.async_add_executor_job(
            history.get_last_state_changes,
            self.hass,
            20,
            self.last_update_sensor.entity_id,
        )
        # filter out invalid timestamp values
        last_updates = [dt_util.parse_datetime(update.state) for update in state_dict.get(self.last_update_sensor.entity_id, []) if update.state != "unknown" and update.state and update.state != "unavailable"]
        last_updates = [update for update in last_updates if update is not None]
        # set last update time to the most recent, if one was found
        if last_updates:
            self.last_packet_time = last_updates[-1]
            return True
        return False

    async def find_events_since_last_update(self, with_flush=True) -> bool:
        """
        Search the history database for any state changes that occurred 
        since we last spoke with the host. This lets us send mising data even after 
        a restart/host downtime.
        """
        if self.last_packet_time is None:
            return False
        for entity_id in self.entities:
            # https://github.com/home-assistant/core/blob/6a3778c48eb0db8cbc59406f27367646e4dbc7f3/homeassistant/components/recorder/history/__init__.py#L155
            entity_history = await self.hass.async_add_executor_job(
                history.state_changes_during_period, 
                self.hass,
                self.last_packet_time,
                dt_util.utcnow(),
                entity_id,
                True,
            )
            found_events = entity_history[entity_id]
            prev_event = None
            found_changes = []
            for event in found_events:
                if prev_event is None or event.state != prev_event.state:
                    state_change = StateChange(entity_id=entity_id, new_state=event.state, timestamp=event.last_changed_timestamp)
                    if state_change.uid not in [state.uid for state in self._event_queue]:
                        found_changes.append(state_change)
                        prev_event = event
            # update internal state with found changes
            self._event_queue.extend(found_changes)
            if found_changes:
                print(f"Found {len(found_changes)} changes for {entity_id}")
                if with_flush:
                    await self.flush_queue()
                return True
        return False

    async def _handle_event(self, event):
        if event.data["old_state"] is not None and event.data["new_state"].state == event.data["old_state"].state:
            return
        state_change = StateChange(
            entity_id=event.data["entity_id"],
            new_state=event.data["new_state"].state,
            timestamp=event.time_fired_timestamp,
        )
        if state_change.uid in [state.uid for state in self._event_queue]:
            return
        print(f"State change: {state_change.entity_id}: {state_change.new_state} ({state_change.timestamp}, id: {state_change.uid})")
        self._event_queue.append(state_change)
        await self.flush_queue()

    async def flush_queue(self):
        while self._event_queue:
            state = self._event_queue[0]
            req_url = f"{self.host}/new_data"
            req_partial = partial(
                requests.post,
                req_url, 
                json={
                    "password": self.password,
                    "entity_id": state.entity_id,
                    "value": state.new_state,
                    "start_time": state.timestamp,
                    "uid": state.uid,
                },
                headers={"Content-Type": "application/json"})
            try:
                self.last_response = await self.hass.async_add_executor_job(req_partial)
                if self.last_response.status_code == 200:
                    self.last_packet_time = dt_util.utcnow()
                    self.last_update_sensor.push_value(self.last_packet_time)
                    self._event_queue.pop(0)
                else:
                    print(f"Flush Error: {self.last_response.status_code}")
                    return
            except requests.exceptions.ConnectionError:
                print(f"Connection error to {req_url}")
                self.last_response = None
                return
            finally:
                self.host_reachable_sensor.push_value(self.last_response is not None and self.last_response.status_code == 200)

    async def _heartbeat(self, now):
        print("Heartbeat")
        if self._event_queue:
            # don't send heartbeat if we have events that we haven't sent yet
            print(f"Skipping heartbeat, {len(self._event_queue)} events in queue")
            await self.flush_queue()
            return
        req_url = f"{self.host}/heartbeat"
        try:
            self.last_response = await self.hass.async_add_executor_job(requests.get, req_url)
        except requests.exceptions.ConnectionError:
            print(f"Connection error to {req_url}")
            self.last_response = None
            return
        finally:
            self.host_reachable_sensor.push_value(self.last_response is not None and self.last_response.status_code == 200)


@dataclass
class StateChange:
    entity_id: str
    new_state: str
    timestamp: float

    @property
    def uid(self):
        return str(abs(hash(self.entity_id + self.new_state + str(self.timestamp))))


PLATFORMS = ["binary_sensor", "sensor"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up sanche-test from a config entry."""
    print("start setup entry")

    hass.data.setdefault(DOMAIN, {})
    # TODO 1. Create API instance
    # TODO 2. Validate the API connection (and authentication)
    # TODO 3. Store an API object for your platforms to access
    listener = HassEventListener(hass, entry)
    hass.data[DOMAIN][entry.entry_id] = listener
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # get changes since last update
    await listener.restore_last_update_time()
    await listener.find_events_since_last_update()
    # start listening for new events
    listener.start()

    print("end setup entry")
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    print("start unload entry")
    # await hass.config_entries.async_forward_entry_unload(entry, PLATFORMS)

    hass.data[DOMAIN][entry.entry_id].stop()
    hass.data[DOMAIN].pop(entry.entry_id)

    print("end unload entry")
    return True
