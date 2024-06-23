from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the binary_sensor platform."""
    print("async_setup_entry: binary_sensor")
    api_obj = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([api_obj.host_reachable_sensor])


# async def async_will_remove_from_hass(hass, entry):
#     """Cleanup when removed."""
#     print("async_will_remove_from_hass")


class HostReachableSensor(BinarySensorEntity):
    def __init__(self, entry, api_obj):
        self._state = False
        self._host = entry.data["url"]
        self._entry_id = entry.entry_id
        self._api_obj = api_obj

    @property
    def name(self):
        return "Host Reachable"

    @property
    def is_on(self):
        return self._state

    @property
    def should_poll(self):
        return False

    def push_value(self, value, extra_attributes=None):
        print(f"HostReachableSensor.update: {value}")
        if value != self._state or extra_attributes != self._attr_extra_state_attributes:
            self._state = value
            self._attr_extra_state_attributes = extra_attributes
            self.schedule_update_ha_state()

    @property
    def unique_id(self) -> str:
        return f"{self._entry_id}_host_reachable"

    @property
    def device_info(self) -> DeviceInfo:
        # https://developers.home-assistant.io/docs/device_registry_index#automatic-registration-through-an-entity
        return DeviceInfo(
            identifiers={(DOMAIN, self._host, self._entry_id)},
            name=f"Lifeline {self._host}",
        )

    @property
    def icon(self):
        return "mdi:server-network"
