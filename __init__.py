""" hjhvhjv """

# # The domain of your component. Should be equal to the name of your component.
# import logging, time, hmac, hashlib, random, base64, json, socket, requests, re, threading, hashlib, string
# import voluptuous as vol
# import asyncio
#
# from datetime import timedelta
# from datetime import datetime
#
# from homeassistant.helpers.entity import Entity
# from homeassistant.helpers.event import async_track_time_interval
# from homeassistant.helpers import discovery
# from homeassistant.helpers import config_validation as cv
# from homeassistant.const import (
#     EVENT_HOMEASSISTANT_STOP, CONF_SCAN_INTERVAL,
#     CONF_EMAIL, CONF_PASSWORD, CONF_USERNAME,
#     HTTP_MOVED_PERMANENTLY, HTTP_BAD_REQUEST,
#     HTTP_UNAUTHORIZED, HTTP_NOT_FOUND)
#
# CONF_HOST     = 'host'
# CONF_PORT   = 'port'
# CONF_DEBUG    = 'debug'
#
# DOMAIN              = "dial"
#
# _LOGGER = logging.getLogger(__name__)
#
# CONFIG_SCHEMA = vol.Schema({
#     DOMAIN: vol.Schema({
#
#         vol.Required(CONF_HOST): cv.string,
#
#         vol.Required(CONF_PORT, default='1900'): cv.string,
#         vol.Optional(CONF_SCAN_INTERVAL, default=timedelta(seconds=30)): cv.time_period,
#
#         vol.Optional(CONF_DEBUG, default=False): cv.boolean
#     }, extra=vol.ALLOW_EXTRA),
# }, extra=vol.ALLOW_EXTRA)
#
# async def async_setup(hass, config):
#     """Setup the dial component."""
#
#     _LOGGER.debug("Create the main object")
#
#     hass.data[DOMAIN] = dial(hass, config)
#
#     for component in ['switch','sensor']:
#         discovery.load_platform(hass, component, DOMAIN, {}, config)
#
#     hass.bus.async_listen('dial_state', hass.data[DOMAIN].state_listener)
#
#         # close the websocket when HA stops
#         # hass.bus.listen_once(EVENT_HOMEASSISTANT_STOP, hass.data[DOMAIN].get_ws().close())
#
#     def update_devices(event_time):
#         asyncio.run_coroutine_threadsafe( hass.data[DOMAIN].async_update(), hass.loop)
#
#     async_track_time_interval(hass, update_devices, hass.data[DOMAIN].get_scan_interval())
#
#     return True
#
# class dial():
#     def __init__(self, hass, config):
#
#         self._hass          = hass
#
#         # get config details from from configuration.yaml
#         self._host      = config.get(DOMAIN, {}).get(CONF_HOST,'')
#         self._port    = config.get(DOMAIN, {}).get(CONF_PORT,'')
#         self._scan_interval = config.get(DOMAIN, {}).get(CONF_SCAN_INTERVAL)
#
#         self._sonoff_debug  = config.get(DOMAIN, {}).get(CONF_DEBUG, False)
#         self._sonoff_debug_log = []
#
#         self._devices       = []
#
#         self.write_debug('{}', new=True)
#
#     def get_scan_interval(self):
#         if DOMAIN in self._hass.data and self._hass.data[DOMAIN].get_debug_state():
#             self._scan_interval = timedelta(seconds=10)
#
#         elif self._scan_interval < timedelta(seconds=60):
#             self._scan_interval = timedelta(seconds=60)
#
#         return self._scan_interval
#
#     def get_debug_state(self):
#         return self._sonoff_debug
#
#     async def state_listener(self, event):
#         if not self.get_ws().connected:
#             _LOGGER.error('websocket is not connected')
#             return
#
#         _LOGGER.debug('received state event change from: %s' % event.data['deviceid'])
#
#         new_state = event.data['state']
#
#         # convert from True/False to on/off
#         if isinstance(new_state, (bool)):
#             new_state = 'on' if new_state else 'off'
#
#         device = self.get_device(event.data['deviceid'])
#         outlet = event.data['outlet']
#
#         if outlet is not None:
#             _LOGGER.debug("Switching `%s - %s` on outlet %d to state: %s", \
#                 device['deviceid'], device['name'] , (outlet+1) , new_state)
#         else:
#             _LOGGER.debug("Switching `%s` to state: %s", device['deviceid'], new_state)
#
#         if not device:
#             _LOGGER.error('unknown device to be updated')
#             return False
#
#         """
#         the payload rule is like this:
#           normal device (non-shared)
#               apikey      = login apikey (= device apikey too)
#
#           shared device
#               apikey      = device apikey
#               selfApiKey  = login apikey (yes, it's typed corectly selfApikey and not selfApiKey :|)
#         """
#         if outlet is not None:
#             params = { 'switches' : device['params']['switches'] }
#             params['switches'][outlet]['switch'] = new_state
#
#         else:
#             params = { 'switch' : new_state }
#
#         payload = {
#             'action'        : 'update',
#             'userAgent'     : 'app',
#             'params'        : params,
#             'apikey'        : device['apikey'],
#             'deviceid'      : str(device['deviceid']),
#             'sequence'      : str(time.time()).replace('.',''),
#             'controlType'   : device['params']['controlType'] if 'controlType' in device['params'] else 4,
#             'ts'            : 0
#         }
#
#         # this key is needed for a shared device
#         if device['apikey'] != self.get_user_apikey():
#             payload['selfApikey'] = self.get_user_apikey()
#
#         self.get_ws().send(json.dumps(payload))
#
#         # set also te pseudo-internal state of the device until the real refresh kicks in
#         for idxd, dev in enumerate(self._devices):
#             if dev['deviceid'] == device['deviceid']:
#                 if outlet is not None:
#                     self._devices[idxd]['params']['switches'][outlet]['switch'] = new_state
#                 else:
#                     self._devices[idxd]['params']['switch'] = new_state
#
#         data = json.dumps({'entity_id' : str(device['deviceid']), 'outlet': outlet, 'new_state' : new_state})
#         self.write_debug(data, type='S')
#
#     def on_message(self, *args):
#         data = args[-1] # to accomodate the weird behaviour where the function receives 2 or 3 args
#
#         _LOGGER.debug('websocket msg: %s', data)
#
#         data = json.loads(data)
#         if 'action' in data and data['action'] == 'update' and 'params' in data:
#             if 'switch' in data['params'] or 'switches' in data['params']:
#                 for idx, device in enumerate(self._devices):
#                     if device['deviceid'] == data['deviceid']:
#                         self._devices[idx]['params'] = data['params']
#
#                         if 'switches' in data['params']:
#                             for switch in data['params']['switches']:
#                                 self.set_entity_state(data['deviceid'], switch['switch'], switch['outlet'])
#                         else:
#                             self.set_entity_state(data['deviceid'], data['params']['switch'])
#
#                         break # do not remove
#
#         self.write_debug(json.dumps(data), type='W')
#
#     def on_error(self, *args):
#         error = args[-1] # to accomodate the case when the function receives 2 or 3 args
#         _LOGGER.error('websocket error: %s' % str(error))
#
#     def set_entity_state(self, deviceid, state, outlet=None):
#         entity_id = 'switch.%s%s%s' % (
#             'sonoff_' if self._entity_prefix else '',
#             deviceid,
#             '_'+str(outlet+1) if outlet is not None else ''
#         )
#
#         # possible @PATCH when (i assume) the device is reported offline in HA but an update comes from websocket
#         if hasattr(self._hass.states.get(entity_id), 'attributes'):
#             attr = self._hass.states.get(entity_id).attributes
#             self._hass.states.set(entity_id, state, attr)
#
#         data = json.dumps({'entity_id' : entity_id, 'outlet': outlet, 'state' : state})
#         self.write_debug(data, type='s')
#
#     def get_devices(self, force_update = False):
#         if force_update:
#             return self.update_devices()
#
#         return self._devices
#
#     def get_device(self, deviceid):
#         for device in self.get_devices():
#             if 'deviceid' in device and device['deviceid'] == deviceid:
#                 return device
#
#     async def async_update(self):
#         devices = self.update_devices()
#
#     ### sonog_debug.log section ###
#     def write_debug(self, data, type = '', new = False):
#
#         if self._sonoff_debug and self._hass.states.get('switch.sonoff_debug') and self._hass.states.is_state('switch.sonoff_debug','on'):
#
#             if not len(self._sonoff_debug_log):
#                 _LOGGER.debug("init sonoff debug data capture")
#                 self._sonoff_debug_log.append(".\n--------------COPY-FROM-HERE--------------\n\n")
#
#             data = json.loads(data)
#
#             # remove extra info
#             if isinstance(data, list):
#                 for idx, d in enumerate(data):
#                     for k in ['extra', 'sharedTo','settings','group','groups','deviceUrl','deviceStatus',
#                                 'location','showBrand','brandLogoUrl','__v','_id','ip',
#                                 'deviceid','createdAt','devicekey','apikey','partnerApikey','tags']:
#                         if k in d.keys(): del d[k]
#
#                     for k in ['staMac','bindInfos','rssi','timers','partnerApikey']:
#                         if k in d['params'].keys(): del d['params'][k]
#
#                     # hide deviceid
#                     if 'deviceid' in d.keys():
#                         m = hashlib.md5()
#                         m.update(d['deviceid'].encode('utf-8'))
#                         d['deviceid'] = m.hexdigest()
#
#                     data[idx] = d
#
#             data = json.dumps(data, indent=2, sort_keys=True)
#             data = self.clean_data(data)
#             data = json.dumps(json.loads(data))
#
#             data = "%s [%s] %s\n\n" % (datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3], type, data)
#             self._sonoff_debug_log.append(data)
#
#         elif self._sonoff_debug and len(self._sonoff_debug_log) and \
#             self._hass.states.get('switch.sonoff_debug') and \
#             self._hass.states.is_state('switch.sonoff_debug','off'):
#
#             _LOGGER.debug("end of sonoff debug log")
#             self._sonoff_debug_log.append("---------------END-OF-COPY----------------\n")
#             self._sonoff_debug_log = [x.encode('utf-8') for x in self._sonoff_debug_log]
#             self._hass.components.persistent_notification.async_create(str(b"".join(self._sonoff_debug_log), 'utf-8'), 'Sonoff debug')
#             self._sonoff_debug_log = []
#
#     def clean_data(self, data):
#         data = re.sub(r'"phoneNumber": ".*"', '"phoneNumber": "[hidden]",', data)
#         # data = re.sub(r'"name": ".*"', '"name": "[hidden]",', data)
#         data = re.sub(r'"ip": ".*",', '"ip": "[hidden]",', data)
#         #data = re.sub(r'"deviceid": ".*",', '"deviceid": "[hidden]",', data)
#         # data = re.sub(r'"_id": ".*",', '"_id": "[hidden]",', data)
#         data = re.sub(r'"\w{2}:\w{2}:\w{2}:\w{2}:\w{2}:\w{2}"', '"xx:xx:xx:xx:xx:xx"', data)
#         data = re.sub(r'"\w{8}-\w{4}-\w{4}-\w{4}-\w{12}"', '"xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"', data)
#         # data = re.sub(r'"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z"', '"xxxx-xx-xxxxx:xx:xx.xxx"', data)
#         return data
#
# class SonoffDevice(Entity):
#     """Representation of a Sonoff device"""
#
#     def __init__(self, hass, device):
#         """Initialize the device."""
#
#         self._sensor        = None
#         self._state         = None
#
#         self._hass          = hass
#         self._deviceid      = device['deviceid']
#         self._available     = device['online']
#
#         self._attributes    = {
#             'device_id'     : self._deviceid,
#         }
#
#     def get_device(self):
#         for device in self._hass.data[DOMAIN].get_devices():
#             if 'deviceid' in device and device['deviceid'] == self._deviceid:
#                 return device
#
#         return None
#
#     def get_state(self):
#         device = self.get_device()
#
#         return device['params']['switch'] == 'on' if device else False
#
#     def get_available(self):
#         device = self.get_device()
#
#         return device['online'] if device else False
#
#     @property
#     def should_poll(self):
#         """Return the polling state."""
#         return True
#
#     @property
#     def name(self):
#         """Return the name of the switch."""
#         return self._name
#
#     @property
#     def available(self):
#         """Return true if device is online."""
#         return self.get_available()
#
#     # @Throttle(MIN_TIME_BETWEEN_UPDATES)
#     def update(self):
#         """Update device state."""
#
#         # we don't update here because there's 1 single thread that can be active at anytime
#         # and the websocket will send the state update messages
#         pass
#
#     @property
#     def device_state_attributes(self):
#         """Return device specific state attributes."""
#         return self._attributes
