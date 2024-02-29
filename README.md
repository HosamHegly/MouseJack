# MouseJack

## Overview
MouseJack is a research tool developed to demonstrate vulnerabilities in wireless mouse and keyboard devices that operate over the 2.4 GHz frequency band. These vulnerabilities allow for keystroke injection attacks, where an attacker can send arbitrary keystrokes to a victim's computer, potentially leading to unauthorized access or malicious command execution. This project aims to raise awareness about these security issues and encourage manufacturers to enhance the security of their wireless devices.

## Features
Device Discovery: Scan for vulnerable wireless mouse and keyboard devices within range.

Keystroke Injection: Execute keystroke injection attacks against vulnerable devices.

Sniffing: Optionally, the tool can sniff packets to identify devices and understand the communication protocol.

## Requirements
A compatible USB dongle (NRF24LU1+ based dongle with custom firmware)

Python 3.6 or later

Operating System: Linux or Windows (with specific setup instructions)

## Installation

<img width="644" alt="image" src="https://github.com/HosamHegly/MouseJack/assets/57544654/6015619f-d2b9-4e55-a9d4-ea3814224602">

## Usage

Before using MouseJack, ensure your compatible dongle is plugged in.

## Scanning for Devices

## Executing a Keystroke Injection Attack
To execute a keystroke injection attack, use:
<img width="453" alt="image" src="https://github.com/HosamHegly/MouseJack/assets/57544654/df9d976c-9bda-4d93-aa15-ea9cedf5569e">

<img width="182" alt="image" src="https://github.com/HosamHegly/MouseJack/assets/57544654/3fa415a8-7705-4c9c-aa81-ef4043286ad5">

To scan for vulnerable devices, run:
![Uploading image.png…]()

