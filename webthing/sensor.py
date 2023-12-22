"""Platform for webthing sensor integration."""
import logging
import aiohttp

import voluptuous as vol

import homeassistant.helpers.config_validation as cv

# Import the device class from the component that you want to support
from homeassistant.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_USERNAME,
    STATE_OFF,
    STATE_ON,
    DEVICE_CLASS_HUMIDITY,
    DEVICE_CLASS_ILLUMINANCE,
    DEVICE_CLASS_PRESSURE,
    DEVICE_CLASS_TEMPERATURE,
    TEMP_CELSIUS,
    PERCENTAGE,
)

from . import WebthingDevice

_LOGGER = logging.getLogger(__name__)

# Validation of the user's configuration
# PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
#     {
#         vol.Required(CONF_HOST): cv.string,
#         # vol.Optional(CONF_USERNAME, default="admin"): cv.string,
#         # vol.Optional(CONF_PASSWORD): cv.string,
#     }
# )

SENSOR_TYPES = {
    "temperature": [TEMP_CELSIUS, None],
    "humidity": [PERCENTAGE, None],
    "illumination": ["lm", None],
    "lux": ["lx", None],
    "pressure": ["hPa", None],
    "bed_activity": ["μm", None],
}

async def async_setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the webthing platform."""
    # Assign configuration variables.
    # The configuration check takes care they are present.
    # host = config[CONF_HOST]

    # Setup connection with devices/cloud
    things = hass.data["things"]
    # Verify that passed in configuration works
    # if not hub.is_valid_login():
    #     _LOGGER.error("Could not connect to AwesomeLight hub")
    #     return

    # Add devices
    devices = []
    for thing in things:
        if "Sensor" in thing["@type"]:
            if "temperature" in thing["@type"]:
                devices.append(WebthingSensor(thing, DEVICE_CLASS_TEMPERATURE))
            if "humidity" in thing["@type"]:
                devices.append(WebthingSensor(thing, DEVICE_CLASS_HUMIDITY))
            if "pressure" in thing["@type"]:
                devices.append(WebthingSensor(thing, DEVICE_CLASS_PRESSURE))

    print(devices)
    add_entities(devices)


class WebthingSensor(WebthingDevice):
    """Representation of an Webthing Sensor."""

    def __init__(self, thing, device_class):
        """Initialize an WebthingSensor."""
        WebthingDevice.__init__(self, thing)
        self._sensor = thing
        self._url = f"http://dev.wormhole.monad.site:8000/{self._uid}"
        self._state = ""
        self._battery_level = 100
        self._device_class = device_class

    @property
    def device_state_attributes(self):
        """Return the device state attributes."""
        return {"battery_level": self._battery_level}

    @property
    def state(self):
        """Return the state of the binary sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        try:
            return SENSOR_TYPES.get(self._device_class)[0]
        except TypeError:
            return None

    @property
    def device_class(self):
        """Return the class of this device, from component DEVICE_CLASSES."""
        return self._device_class

    async def async_update(self):
        """
        Fetch new state data for this light.
        This is the only method that should fetch new data for Home Assistant.
        """
        if self._ws.data.get("state") is not None:
            self._state = self._ws.data.get("state")
            print(f"{self.name} property state:{self._state}")
        if self._ws.data.get("temperature"):
            self._state = self._ws.data.get("temperature")
            print(f"{self.name} property state:{self._state}")
        if self._ws.data.get("humidity") is not None:
            self._state = self._ws.data.get("humidity")
            print(f"{self.name} property state:{self._state}")
        if self._ws.data.get("battery_level"):
            self._battery_level = self._ws.data.get("battery_level")
            print(f"property battery_level:{self._battery_level}")
