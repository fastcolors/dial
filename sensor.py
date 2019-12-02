"""Platform for sensor integration."""
from homeassistant.helpers.entity import Entity
from . import pydial

servers = pydial.discover()
client = pydial.DialClient(servers[0])
device = client.get_device_description()

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""
    add_entities([DialSensor()])


class DialSensor(Entity):
    """Representation of a Sensor."""

    def __init__(self):
        """Initialize the sensor."""
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return 'TV Name'

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    def update(self):
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        """
        self._state = device
