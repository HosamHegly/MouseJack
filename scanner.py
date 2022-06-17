import argparse
import os
import random
from threading import Thread
from utils import nrf24_reset
from utils import nrf24
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


def arr_to_str(addr):
    return ':'.join('{:02X}'.format(x) for x in addr)


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
            address = arr_to_str(address)
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
    victim_num = input('choose the device of your victim by its number: ')
    while int(victim_num) >= len(devices) or int(victim_num) < 0:
        victim_num = input('please choose a number from 0 to, ', len(devices), ':')
    for i in devices:
        if devices[i]['number'] == victim_num:
            return i


def attack(victim_mac):
    # sniffer mode allows us to spoof the mac address
    radio.sniffer_mode(victim_mac)


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
    attack(victim_mac)
