from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the binary_sensor platform."""
    print("async_setup_entry: sensor")
    api_obj = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([api_obj.last_update_sensor])

class LastUpdateSensor(SensorEntity):
    """Representation of an uptime sensor."""

    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(self, entry: ConfigEntry, api_obj) -> None:
        """Initialize the uptime sensor."""
        self._host = entry.data["url"]
        self._entry_id = entry.entry_id
        self._api_obj = api_obj
        self._attr_native_value = api_obj.last_packet_time

    @property
    def device_info(self) -> DeviceInfo:
        # https://developers.home-assistant.io/docs/device_registry_index#automatic-registration-through-an-entity
        return DeviceInfo(
            identifiers={(DOMAIN, self._host, self._entry_id)},
            name=f"Lifeline {self._host}",
        )

    @property
    def should_poll(self):
        return False

    @property
    def unique_id(self) -> str:
        return f"{self._entry_id}_last_update"

    @property
    def name(self):
        return "Last Update"

    def push_value(self, value, extra_attributes=None):
        print(f"LastUpdateSensor.update: {value}")
        self._attr_native_value = value
        if extra_attributes:
            self._attr_extra_state_attributes = extra_attributes
        self.schedule_update_ha_state()

