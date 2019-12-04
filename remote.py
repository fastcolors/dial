"""Platform for sensor integration."""
import asyncio
import json

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
    vol.Required(CONF_NAME): cv.string,
    vol.Optional(CONF_ICON): cv.icon,
    vol.Optional(CONF_FRIENDLY_NAME): cv.string,
})

url = 'http://192.168.0.12:8008/ssdp/device-desc.xml'
# servers = pydial.discover()

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""
    name = config.get(CONF_NAME)
    host = config.get(CONF_HOST)
    port = config.get(CONF_PORT)
    icon = config.get(CONF_ICON)
    if not icon:
        icon = 'mdi:television'
    server = url
    client = pydial.DialClient(server)
    device = client.get_device_description()
    status = device.friendly_name
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

    def async_update(self):
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        """
        server = url
        client = pydial.DialClient(server)
        device = client.get_device_description()
        status = device.friendly_name
        self._state = status
        attributes['host'] = host
        attributes['port'] = port
        self.custom_attributes = attributes
