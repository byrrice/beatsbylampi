from kivy.app import App
from kivy.properties import StringProperty
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from math import fabs
import platform
import pigpio
import lampi_util
from paho.mqtt.client import Client
from lamp_common import *
import json

MQTT_CLIENT_ID = "lamp_ui"

class SongApp(App):

    _updatingUI = False
    song = StringProperty()

    def on_start(self):
        self._publish_clock = None
        self.mqtt = Client(client_id=MQTT_CLIENT_ID)
        self.mqtt.on_connect = self.on_connect
        self.mqtt.connect(MQTT_BROKER_HOST, port = MQTT_BROKER_PORT,
                          keepalive = MQTT_BROKER_KEEP_ALIVE_SECS)
        self.mqtt.loop_start()
        self._update_song_text("No Song")
        self.set_up_GPIO_and_IP_popup()

    def on_connect(self, client, userdata, flags, rc):
        self.mqtt.subscribe(TOPIC_LAMP_CHANGE_NOTIFICATION)
        self.mqtt.message_callback_add(TOPIC_LAMP_CHANGE_NOTIFICATION,
                                       self.receive_new_lamp_state)
        print("on_connect reached")
    def receive_new_lamp_state(self, client, userdata, message):
        new_state = json.loads(message.payload)
        print("received state")
        Clock.schedule_once(lambda dt: self._update_ui(new_state), 0.01)

    def on_song(self, instance, value):
        if self._updatingUI:
            return
        if self._publish_clock is None:
            self._publish_clock = Clock.schedule_once(
                lambda dt: self._update_song_text(value), 0.01)

    def _update_ui(self, new_state):
        self._updatingUI = True
        try:
            if 'song' in new_state:
                self._update_song_text(new_state['song'])
        finally:
            self._updatingUI = False

    def _update_song_text(self, value):
        self.song = value
        self._publish_clock = None

    def set_up_GPIO_and_IP_popup(self):
        self.pi = pigpio.pi()
        self.pi.set_mode(17, pigpio.INPUT)
        self.pi.set_pull_up_down(17, pigpio.PUD_UP)
        Clock.schedule_interval(self._poll_GPIO, 0.05)
        self.popup = Popup(title='IP Addresses',
                           content=Label(text='IP ADDRESS WILL GO HERE'),
                           size_hint=(1, 1), auto_dismiss=False)
        self.popup.bind(on_open=self.update_popup_ip_address)

    def update_popup_ip_address(self, instance):
        interface = "wlan0"
        ipaddr = lampi_util.get_ip_address(interface)
        instance.content.text = "{}: {}".format(interface, ipaddr)

    def on_gpio17_pressed(self, instance, value):
        if value:
            self.popup.open()
        else:
            self.popup.dismiss()

    def _poll_GPIO(self, dt):
        # GPIO17 is the rightmost button when looking front of LAMPI
        self.gpio17_pressed = not self.pi.read(17)
