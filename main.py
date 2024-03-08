import time
import os

class Device:
    def __init__(self, name, ip):
        self.name = name
        self.ip = ip
        self.last_seen = time.time()
        self.up = ping_device(self)

    def __str__(self):
        return f'{self.name} {self.ip} is {"up" if self.up else "down"}'

    def five_minutes_ago(self):
        return time.time() - self.last_seen > 300

    def switch_up(self):
        self.up = True
        self.last_seen = time.time()

    def switch_down(self):
        self.up = False

    def check_up_status(self):
        if ping_device(self):
            if self.up:
                self.last_seen = time.time()
                return 1
            else:
                self.switch_up()
                self.last_seen = time.time()
                return 2
        else:
            if self.status_unknown():
                print(f'{self.name} might be down')
                return 3
            else:
                print(f'{self.name} is down')
                self.switch_down()
                return 0

    def status_unknown(self):
        if self.up:
            if not self.five_minutes_ago():
                return True
            else:
                return False

def later_than_6PM():
    return time.localtime().tm_hour > 18

class HueBridge:
    def __init__(self, ip):
        self.ip = ip
        self.authorization = os.environ.get('HUE_AUTHORIZATION', 'newdeveloper')
        print(f'Authorization: {self.authorization}')

class HueLight:
    def __init__(self, name, pk, bridge):
        self.name = name
        self.pk = pk
        self.bridge = bridge
        self.say_hello()

    def is_on(self):
        link = f'https://{self.bridge.ip}/api/{self.bridge.authorization}/groups/{self.pk}'
        response = os.popen(f'curl -k {link}').read()
        return '"on":true' in response

    def say_hello(self):
        if self.is_on():
            self.turn_off()
            self.turn_on()
        else:
            self.turn_on()
            self.turn_off()

    def __str__(self):
        return f'{self.name} is {"on" if self.is_on() else "off"}'

    def turn_on(self):
        link = f'https://{self.bridge.ip}/api/{self.bridge.authorization}/groups/{self.pk}/action'
        os.system(f'curl -k -X PUT -d \'{{"on":true}}\' {link}')

    def turn_off(self):
        link = f'https://{self.bridge.ip}/api/{self.bridge.authorization}/groups/{self.pk}/action'
        os.system(f'curl -k -X PUT -d \'{{"on":false}}\' {link}')

    def turn_red(self):
        link = f'https://{self.bridge.ip}/api/{self.bridge.authorization}/groups/{self.pk}/action'
        print(link)
        os.system(f'curl -k -X PUT -d \'{{"on":true, "xy":[0.675,0.322]}}\' {link}')

    def turn_green(self):
        link = f'https://{self.bridge.ip}/api/{self.bridge.authorization}/groups/{self.pk}/action'
        os.system(f'curl -k -X PUT -d \'{{"on":true, "xy":[0.409,0.518]}}\' {link}')

    def turn_blue(self):
        link = f'https://{self.bridge.ip}/api/{self.bridge.authorization}/groups/{self.pk}/action'
        os.system(f'curl -k -X PUT -d \'{{"on":true, "xy":[0.167,0.04]}}\' {link}')

    def turn_yellow(self):
        link = f'https://{self.bridge.ip}/api/{self.bridge.authorization}/groups/{self.pk}/action'
        os.system(f'curl -k -X PUT -d \'{{"on":true, "xy":[0.444,0.516]}}\' {link}')

    def turn_white(self):
        link = f'https://{self.bridge.ip}/api/{self.bridge.authorization}/groups/{self.pk}/action'
        os.system(f'curl -k -X PUT -d \'{{"on":true, "xy":[0.336,0.360]}}\' {link}')

    def turn_dark(self):
        link = f'https://{self.bridge.ip}/api/{self.bridge.authorization}/groups/{self.pk}/action'
        os.system(f'curl -k -X PUT -d \'{{"on":true, "bri":1}}\' {link}')

def ping_device(device):
    response = os.system(f'ping -c 1 -W 1 {device.ip} > /dev/null')
    print(f'Ping response for {device.name}: {response}')
    return response == 0



if __name__=='__main__':
    router = Device("FritzBox", "192.168.178.1")
    uli_device = Device("Uli's Phone", "192.168.178.34")
    micha_device = Device("Micha's Phone", "192.168.178.20")
    hue_bridge = HueBridge("192.168.178.26")
    living_room_light = HueLight("Wohnzimmer", "1", hue_bridge)
    corridor_light = HueLight("Flur", "81", hue_bridge)
    uli_room_light = HueLight("Uli's Zimmer", "82", hue_bridge)
    micha_room_light = HueLight("Micha's Zimmer", "83", hue_bridge)
 
    while True:
        router.check_up_status()
        if router.up:
            if time.localtime().tm_hour == 20 and time.localtime().tm_min == 0 and time.localtime().tm_sec  in range(0, 5):
                living_room_light.turn_dark()
                living_room_light.turn_red()
                corridor_light.turn_off()
                uli_room_light.turn_off()
                micha_room_light.turn_off()
            uli_status = uli_device.check_up_status()
            micha_status = micha_device.check_up_status()
            print(f'Uli: {uli_status}, Micha: {micha_status}')
            if uli_status == 2 or micha_status == 2 and later_than_6PM():
                if not corridor_light.is_on():
                    corridor_light.turn_on()
                else:
                    corridor_light.say_hello()
            if uli_status == 0 and micha_status == 0:
                if corridor_light.is_on():
                    corridor_light.turn_off()
        time.sleep(5)
        
