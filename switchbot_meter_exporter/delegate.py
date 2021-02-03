from bluepy import btle


class Delegate(btle.DefaultDelegate):
    def __init__(self, macaddr):
        btle.DefaultDelegate.__init__(self)
        self.macaddr = macaddr
        self.value = None

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if dev.addr == self.macaddr:
            for (adtype, desc, value) in dev.getScanData():
                if adtype == 22:
                    self._decode(value)

    def _decode(self, value):
        data = bytes.fromhex(value[4:])
        batt = data[2] & 0b01111111
        is_temperature_above_freezing = data[4] & 0b10000000
        t1 = data[3] & 0b00001111
        t2 = data[4] & 0b01111111
        humid = data[5] & 0b01111111
        temp = t1 / 10 + t2
        if not is_temperature_above_freezing:
            temp = -temp
        self.value = {
            'battery': batt,
            'temperature': temp,
            'humidity': humid,
        }
