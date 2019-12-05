"""Platform for sensor integration."""
import asyncio
import json
import wakeonlan

import voluptuous as vol
from . import pydial
from homeassistant.components.remote import PLATFORM_SCHEMA
from homeassistant.const import (CONF_HOST, CONF_PORT, CONF_FRIENDLY_NAME, CONF_ICON, CONF_NAME)
from homeassistant.helpers.entity import Entity
import homeassistant.helpers.config_validation as cv
from time import time, sleep

# REQUIREMENTS = ['pytuya==7.0.4']

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Required(CONF_PORT): cv.string,
    vol.Optional(CONF_NAME): cv.string,
    vol.Optional(CONF_ICON): cv.icon,
    vol.Optional(CONF_FRIENDLY_NAME): cv.string,
})

servers = pydial.discover()
# host = config.get(CONF_HOST)
# for s in servers:
#     if config.get(CONF_HOST) in str(servers[s]):
#         server = servers[s][0]
#         mac = servers[s][1]
#     else:
#         server = None
#         mac = None

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""
    host = config.get(CONF_HOST)
    count = 0
    for s in servers:
        if config.get(CONF_HOST) in str(servers[count]):
            server = servers[count][0]
            mac = servers[count][1]
        else:
            server = None
            mac = None
        count += 1
    # server = config.get(CONF_HOST)
    port = config.get(CONF_PORT)
    icon = config.get(CONF_ICON)
    if not icon:
        icon = 'mdi:television'
    client = pydial.DialClient(server)
    device = client.get_device_description()
    name = config.get(CONF_NAME)
    if not name:
        name = device.friendly_name
    status = 'False'
    add_entities([DialRemote(name,host,port,icon,status)])

class DialRemote(Entity):
    """Representation of a Sensor."""

    def __init__(self,name,host,port,icon,status):
        """Initialize the sensor."""
        self._state = status
        self._name = name
        self._icon = icon
        self._port = port
        attributes = {}
        attributes['host'] = host
        attributes['port'] = port
        self.custom_attributes = attributes

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return self._icon

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def device_state_attributes(self):
        """Return the state attributes of the sensor."""
        return self.custom_attributes

    def async_turn_on(self, **kwargs):
        """Turn the device on."""
        if self._broadcast_address:
            wakeonlan.send_magic_packet(
                self._mac_address, ip_address=self._broadcast_address
            )
        else:
            wakeonlan.send_magic_packet(self._mac_address)

    def async_turn_off(self, **kwargs):
        """Turn the device off."""

    def async_update(self):
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        """
        self._state = 'False'
