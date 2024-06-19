from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
)
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

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
    async_add_entities([HostReachableSensor(entry)])

# async def async_will_remove_from_hass(hass, entry):
#     """Cleanup when removed."""
#     print("async_will_remove_from_hass")
    # hass.data[DOMAIN].remove_config_entry(entry)

class HostReachableSensor(BinarySensorEntity):

    def __init__(self, entry):
        self._state = False
        self._host = entry.data["url"]
        self._entry_id = entry.entry_id

    @property
    def name(self):
        return "Host Reachable"

    @property
    def is_on(self):
        return self._state

    def update(self):
        self._state = False
        print("HostReachableSensor.update")

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
