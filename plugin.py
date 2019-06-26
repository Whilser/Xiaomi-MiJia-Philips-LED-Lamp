#
#           Philips LED Lamp python Plugin for Domoticz
#           Version 0.1.2

#           Powered by lib python miio https://github.com/rytilahti/python-miio
#

"""
<plugin key="PhilipsLED" name="Xiaomi MiJia Philips LED Lamp" author="Whilser" version="0.1.2" wikilink="https://www.domoticz.com/wiki/Xiaomi_MiJia_Philips_LED_Lamp" externallink="https://github.com/Whilser/Xiaomi-MiJia-Philips-LED-Lamp">
    <description>
        <h2>Xiaomi MiJia Philips LED Lamp</h2><br/>
        <h3>Configuration</h3>
        Enter the IP Address and Token of your Philips Lamp. The Scene parameter creates a selector of the standard Philips lamp scenes.  <br/>
        Set the scene parameter "show" to display scenes, otherwise set to "hide".

    </description>
    <params>
        <param field="Address" label="IP Address" width="200px" required="true" default=""/>
        <param field="Mode1" label="Token" width="300px" required="true" default=""/>
        <param field="Mode3" label="Scenes" width="75px">
            <options>
                <option label="Show" value="Show" default="True" />
                <option label="Hide" value="Hide" />
            </options>
        </param>
        <param field="Mode2" label="Debug" width="75px">
            <options>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal" default="True" />
            </options>
        </param>
    </params>
</plugin>
"""

import os
import sys
import time
import os.path
import json
import random
import binascii

import Domoticz

module_paths = [x[0] for x in os.walk( os.path.join(os.path.dirname(__file__), '.', '.env/lib/') ) if x[0].endswith('site-packages') ]
for mp in module_paths:
    sys.path.append(mp)

from miio import PhilipsBulb
from miio.philips_bulb import PhilipsBulbStatus, PhilipsBulbException

class BasePlugin:

    UNIT_LAMP = 1
    UNIT_SCENES = 2

    pollTime = 1
    nextTimeSync = 0
    handshakeTime = 0

    def __init__(self):
        #self.var = 123
        return

    def onStart(self):
        Domoticz.Debug("onStart called")
        if Parameters['Mode2'] == 'Debug': Domoticz.Debugging(1)

        if self.UNIT_LAMP not in Devices:
            Domoticz.Device(Name='Lamp',  Unit=self.UNIT_LAMP, Type=241, Subtype=8, Switchtype=7, Used=1).Create()

        if ((Parameters['Mode3'] == 'Show') and (self.UNIT_SCENES not in Devices)):
            Options = { "Scenes": "|||||", "LevelNames": "Off|Bright|TV|Warm|Midnight", "LevelOffHidden": "true", "SelectorStyle": "0" }
            Domoticz.Device(Name="Scenes", Unit=self.UNIT_SCENES, Type=244, Subtype=62 , Switchtype=18, Options = Options, Used=1).Create()

        global Lamp
        Lamp = PhilipsBulb(Parameters['Address'],Parameters['Mode1'])

        self.pollTime = random.randrange(5, 16)
        self.nextTimeSync = 0

        DumpConfigToLog()
        Domoticz.Heartbeat(20)

        Domoticz.Debug('Plugin started.')
        Domoticz.Log('Poll time is every {0} minute'.format(self.pollTime))

    def onStop(self):
        Domoticz.Debug("onStop called")

    def onConnect(self, Connection, Status, Description):
        Domoticz.Debug("onConnect called")

    def onMessage(self, Connection, Data):
        Domoticz.Debug("onMessage called")

    def onCommand(self, Unit, Command, Level, Color):
        Domoticz.Debug("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level)+ ", Color: "+str(Color))

        if Unit == self.UNIT_SCENES:
            self.HandleScenes(Level)
            return

        Level = max(min(Level, 100), 1)

        try:

            if Command == 'On':
                Lamp.on()
                Devices[Unit].Update(nValue=1, sValue='On', TimedOut = False)

            elif Command == 'Off':
                Lamp.off()
                Devices[Unit].Update(nValue=0, sValue='Off', TimedOut = False)
                if self.UNIT_SCENES in Devices: Devices[self.UNIT_SCENES].Update(nValue=0, sValue='0')

            elif Command == 'Set Level':
                Lamp.set_brightness(Level)
                Devices[Unit].Update(nValue=1, sValue=str(Level), TimedOut = False)

            elif Command == 'Set Color':

                Hue = json.loads(Color)
                if Hue['m'] == 2:
                    Temp = 100-((100*Hue['t'])/255)
                    Temp = max(min(Temp, 100), 1)

                    Lamp.set_brightness_and_color_temperature(Level, Temp)
                    Devices[Unit].Update(nValue=1, sValue=str(Level), Color = Color, TimedOut = False)
        except Exception as e:
            Domoticz.Error('Error send command to {0} with IP {1}. Lamp is not responding, check power/network connection. Errror: {2}'.format(Parameters['Name'], Parameters['Address'], e.__class__))
            Devices[Unit].Update(nValue=Devices[Unit].nValue, sValue=Devices[Unit].sValue, TimedOut = True)
            self.handshakeTime = 0
            self.nextTimeSync = 0

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Debug("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        Domoticz.Debug("onDisconnect called")

    def onHeartbeat(self):
        Domoticz.Debug("onHeartbeat called")

        self.nextTimeSync -= 1
        self.handshakeTime -= 1

        try:

            if self.handshakeTime <= 0:
                Lamp.do_discover()
                Domoticz.Debug('Device ID: {0} '.format(binascii.hexlify(Lamp._device_id).decode()))
                self.handshakeTime = 3

            if (self.nextTimeSync <= 0) and (self.UNIT_LAMP in Devices):
                Domoticz.Debug('Sync on time: every {0} minute called'.format(self.pollTime))
                self.nextTimeSync = int((self.pollTime*60)/20)

                status = Lamp.status()

                if status.is_on:
                    hue = int((100 - int(status.color_temperature)) * 255 / 100)
                    if hue == 0: hue = 1

                    color = {}
                    color['m']  = 2
                    color['t']  = hue
                    color['r']  = 0
                    color['g']  = 0
                    color['b']  = 0
                    color['cw'] = 0
                    color['ww'] = 0
                    sColor = json.dumps(color)

                    if ((Devices[self.UNIT_LAMP].sValue != str(status.brightness)) or (Devices[self.UNIT_LAMP].nValue != 1) or (Devices[self.UNIT_LAMP].TimedOut == True)):
                        Devices[self.UNIT_LAMP].Update(nValue=1, sValue=str(status.brightness), Color = sColor, TimedOut = False)

                if not status.is_on:
                    if ((Devices[self.UNIT_LAMP].nValue != 0) or (Devices[self.UNIT_LAMP].TimedOut == True)):
                        Devices[self.UNIT_LAMP].Update(nValue=0, sValue='Off', TimedOut = False)

                if ((self.UNIT_SCENES in Devices) and (str(status.scene*10) != Devices[self.UNIT_SCENES].sValue)):
                    if status.scene == 0:
                        Devices[self.UNIT_SCENES].Update(nValue=0, sValue="0")
                    else: Devices[self.UNIT_SCENES].Update(nValue=1, sValue=str(status.scene*10))

        except Exception as e:
            Devices[self.UNIT_LAMP].Update(nValue=Devices[self.UNIT_LAMP].nValue, sValue=Devices[self.UNIT_LAMP].sValue, TimedOut = True)
            self.handshakeTime = 0
            self.nextTimeSync = 0

    def HandleScenes(self, Level):
        if (Level == 0): return

        try:
            Lamp.set_scene(int(Level)/10)

            if self.UNIT_SCENES in Devices:
                Devices[self.UNIT_SCENES].Update(nValue=1, sValue=str(Level))
                self.nextTimeSync = 0

        except:
            Domoticz.Error('Error set fixed scene on {0} with IP {1}. Check power/network connection.'.format(Parameters['Name'], Parameters['Address']))
            self.handshakeTime = 0

global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

    # Generic helper functions
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
        Domoticz.Debug("Device TimedOut: " + str(Devices[x].TimedOut))
    return
