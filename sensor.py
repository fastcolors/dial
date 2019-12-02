"""Platform for sensor integration."""
from homeassistant.helpers.entity import Entity
from . import pydial

servers = pydial.discover()
client = []
device_tuple = []
device = []
url = []
i = 0
c = 0
for item in servers:
    sclient = pydial.DialClient(servers[i])
    client.append(sclient)
    description = client[i].get_device_description()
    device_tuple.append(description)
    device.append(device_tuple[i].friendly_name)
    url.append(device_tuple[i].dev_url)
    i += 1

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""
    for item in servers:
        add_entities([DialSensor()])

class DialSensor(Entity):
    """Representation of a Sensor."""

    def __init__(self):
        """Initialize the sensor."""
        self._state = None
        self.custom_attributes = {}
        # self._url = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return 'Screen Name'

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return 'mdi:television'

    @property
    def device_state_attributes(self):
        """Return the state attributes of the sensor."""
        return self.custom_attributes

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    def update(self):
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        """
        c = 0
        for item in servers:
            self._state = device[c]
            attributes = {}
            attributes['mac'] = servers[c]
            attributes['url'] = url[c]
            self.custom_attributes = attributes
            c += 1
