from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN

# def setup_platform(
#     hass: HomeAssistant,
#     config: ConfigType,
#     add_entities: AddEntitiesCallback,
#     discovery_info: DiscoveryInfoType | None = None
# ) -> None:
#     """Set up the sensor platform."""
#     add_entities([HostReachableSensor()])


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the binary_sensor platform."""
    print("async_setup_entry")
    api_obj = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([HostReachableSensor(entry, api_obj)])


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

    def update(self):
        last_response = self._api_obj.last_response
        self._state = last_response is not None and last_response.status_code == 200
        print(
            f"HostReachableSensor.update: {self._state} (last_response: {last_response})"
        )

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
