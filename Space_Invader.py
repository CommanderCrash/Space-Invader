#!/usr/bin/env python3

import sys
import argparse
import random
from termcolor import colored
import pigpio
import time

class Protocol:
    def __init__(self, pulselength, sync_high, sync_low, zero_high, zero_low, one_high, one_low):
        self.pulselength = pulselength
        self.sync_high = sync_high
        self.sync_low = sync_low
        self.zero_high = zero_high
        self.zero_low = zero_low
        self.one_high = one_high
        self.one_low = one_low

PROTOCOLS = (None,
             Protocol(450, 1, 31, 1, 3, 3, 1),  # 1
             Protocol(350, 32, 40, 1, 2, 3, 1),  # 2
             Protocol(670, 15, 52, 3, 3, 5, 1),  # 3
             Protocol(320, 36, 1, 1, 2, 2, 1),  # 4
             Protocol(365, 18, 1, 3, 2, 1, 3),  # 5
             Protocol(380, 1, 6, 1, 3, 3, 1),   # 6
             Protocol(450, 23, 1, 1, 2, 2, 1),  # 7
             Protocol(270, 36, 1, 1, 2, 2, 1),  # 8
             Protocol(650, 1, 10, 1, 2, 2, 1),  # 9
             Protocol(500, 6, 14, 1, 2, 2, 1),  # 10
             Protocol(100, 30, 71, 4, 11, 9, 6),  # 11
             Protocol(200, 30, 7, 16, 7, 16, 3),  # 12
             Protocol(150, 2, 62, 1, 6, 6, 1),  # 13
             Protocol(250, 1, 10, 1, 2, 2, 1))  # 14

class RFDevice:
    def __init__(self, gpio):
        self.gpio = gpio
        self.pi = pigpio.pi()
        self.tx_repeat = 10
        self.pi.set_mode(self.gpio, pigpio.OUTPUT)

    def enable_tx(self):
        pass

    def cleanup(self):
        self.pi.stop()

    def tx_code(self, code, protocol_num, pulselength, length, sync_pulse, sync_space, zero_pulse, zero_space, one_pulse, one_space):
        if protocol_num >= len(PROTOCOLS) or protocol_num <= 0:
            raise ValueError(f"Unsupported protocol {protocol_num}")

        protocol = PROTOCOLS[protocol_num]
        if protocol is None:
            raise ValueError(f"Unsupported protocol {protocol_num}")

        effective_pulselength = pulselength if pulselength is not None else protocol.pulselength

        for _ in range(self.tx_repeat):
            self.send_sync(protocol, effective_pulselength, sync_pulse, sync_space)
            self.send_data(code, protocol, effective_pulselength, length, zero_pulse, zero_space, one_pulse, one_space)

    def send_sync(self, protocol, pulselength, sync_pulse, sync_space):
        high_pulse = sync_pulse if sync_pulse is not None else protocol.sync_high
        low_space = sync_space if sync_space is not None else protocol.sync_low
        self.pi.write(self.gpio, 1)
        time.sleep(high_pulse * pulselength / 1000000)
        self.pi.write(self.gpio, 0)
        time.sleep(low_space * pulselength / 1000000)

    def send_data(self, code, protocol, pulselength, length, zero_pulse, zero_space, one_pulse, one_space):
        for bit in format(code, f'0{length}b'):
            if bit == '0':
                self.send_bit(zero_pulse if zero_pulse is not None else protocol.zero_high,
                              zero_space if zero_space is not None else protocol.zero_low,
                              pulselength)
            else:
                self.send_bit(one_pulse if one_pulse is not None else protocol.one_high,
                              one_space if one_space is not None else protocol.one_low,
                              pulselength)

    def send_bit(self, high, low, pulselength):
        self.pi.write(self.gpio, 1)
        time.sleep(high * pulselength / 1000000)
        self.pi.write(self.gpio, 0)
        time.sleep(low * pulselength / 1000000)

def generate_random_code(bit_length, exclude_set):
    while True:
        code = random.getrandbits(bit_length)
        if code not in exclude_set:
            exclude_set.add(code)
            return code

def send_code(rfdevice, code, protocol_num, pulselength, length, timeout, sync_pulse, sync_space, zero_pulse, zero_space, one_pulse, one_space):
    protocol = PROTOCOLS[protocol_num]
    bin_code = bin(code)[2:].zfill(length)
    hex_code = hex(code)[2:].upper()
    protocol_info = f"Protocol: {colored(str(protocol_num), 'green')}" if protocol else ""
    print(f"{colored('Sending Code:', 'cyan')} {colored(str(code), 'yellow')}\n"
          f"Binary: {colored(bin_code, 'green')}\n"
          f"Decimal: {colored(str(code), 'green')}\n"
          f"Hexadecimal: {colored(hex_code, 'green')}\n"
          f"{protocol_info}")
    rfdevice.tx_code(code, protocol_num, pulselength, length, sync_pulse, sync_space, zero_pulse, zero_space, one_pulse, one_space)
    time.sleep(0.05)
    if timeout > 0:
        time.sleep(timeout / 1000.0)

def bruteforce_mode_1(rfdevice, bit_length, protocols, pulselength, length):
    for code in range(2**length):
        for protocol in protocols:
            send_code(rfdevice, code, int(protocol), pulselength, length, 0, None, None, None, None, None, None)

def bruteforce_mode_2(rfdevice, bit_length, protocols, pulselength, length):
    generated_codes = set()
    while True:
        code = generate_random_code(bit_length, generated_codes)
        for protocol in protocols:
            send_code(rfdevice, code, int(protocol), pulselength, length, 0, None, None, None, None, None, None)
        if len(generated_codes) == 2**bit_length:
            break

def bruteforce_mode_3(rfdevice, base_code_str, protocols, pulselength):
    length = len(base_code_str)
    positions = [i for i, char in enumerate(base_code_str) if char == '?']
    num_positions = len(positions)
    generated_codes = set()

    while True:
        binary_pattern = bin(random.getrandbits(num_positions))[2:].zfill(num_positions)
        code_str = list(base_code_str)

        for i, pos in enumerate(positions):
            code_str[pos] = binary_pattern[i]

        code = int(''.join(code_str), 2)

        if code not in generated_codes:
            generated_codes.add(code)
            for protocol in protocols:
                send_code(rfdevice, code, int(protocol), pulselength, length, 0, None, None, None, None, None, None)

        if len(generated_codes) == 2**num_positions:
            break

def main():

    # Message of the Day (MOTD)
    motd = """
                                          ##          ##
                                            ##      ##         
                                          ##############
                                       ####   #####   ####
                                      #####################
                                    ## ################### ##     
                                    ##   ##           ##   ##
                                           ####   ####
                                             _                     _               
                                            (_)                   | |              
                    ___ _ __   __ _  ___ ___ _ _ ____   ____ _  __| | ___ _ __ 
                   / __| '_ \ / _` |/ __/ _ \ | '_ \ \ / / _` |/ _` |/ _ \ '__/
                   \__ \ |_) | (_| | (_|  __/ | | | \ V / (_| | (_| |  __/ | 
                   |___/ .__/ \__,_|\___\___|_|_| |_|\_/ \__,_|\__,_|\___|_|  
                       | |                                                         
                       |_|                                                         
    """
    print(motd)
    parser = argparse.ArgumentParser(description='Sends a decimal code via a 433/315MHz GPIO device')
    parser.add_argument('-s', dest='base_code', metavar='BASE_CODE', type=str,
                        help="Base code to start guessing from in bruteforce mode 3")
    parser.add_argument('-g', dest='gpio', type=int, default=17,
                        help="GPIO pin (Default: 17)")
    parser.add_argument('-p', dest='pulselength', type=int, default=None,
                        help="Pulselength (Default: None, uses protocol's default)")
    parser.add_argument('-t', dest='protocol', nargs='+', default=['1'],
                        help="Protocol(s) to use. Use '-t all' to iterate through all protocols.")
    parser.add_argument('-l', dest='length', type=int, default=24,
                        help="Codelength (Default: 24)")
    parser.add_argument('-r', dest='repeat', type=int, default=10,
                        help="Repeat cycles (Default: 10)")
    parser.add_argument('-bf', dest='bruteforce_mode', type=int, choices=[1, 2, 3], default=None,
                        help="Bruteforce mode: 1 - Count up, 2 - Random, 3 - Guess based on '?'")
    parser.add_argument('-m', dest='code', metavar='BINARY_STRING', type=str,
                        help="Send a single code in binary string format. Not compatible with -bf or -l")
    parser.add_argument('-to', dest='timeout', type=int, default=0,
                        help="Timeout in milliseconds between protocols when using '-t all' (Default: 0)")
    parser.add_argument('--sync_pulse', type=int, default=None,
                        help="Override sync high pulse length")
    parser.add_argument('--sync_space', type=int, default=None,
                        help="Override sync low space length")
    parser.add_argument('--zero_pulse', type=int, default=None,
                        help="Override zero high pulse length")
    parser.add_argument('--zero_space', type=int, default=None,
                        help="Override zero low space length")
    parser.add_argument('--one_pulse', type=int, default=None,
                        help="Override one high pulse length")
    parser.add_argument('--one_space', type=int, default=None,
                        help="Override one low space length")

    args = parser.parse_args()

    rfdevice = RFDevice(args.gpio)
    rfdevice.enable_tx()
    rfdevice.tx_repeat = args.repeat

    protocols = args.protocol
    if protocols and 'all' in protocols:
        protocols = list(range(1, len(PROTOCOLS)))

    # Fixed logic for handling -m option
    if args.code is not None:
        # When using -m, we ignore -bf and -l
        for protocol in protocols:
            send_code(rfdevice, int(args.code, 2), int(protocol), args.pulselength, 
                     len(args.code), args.timeout, args.sync_pulse, args.sync_space, 
                     args.zero_pulse, args.zero_space, args.one_pulse, args.one_space)
    elif args.bruteforce_mode:
        if args.length is None and args.bruteforce_mode != 3:
            print("Bit length (-l) must be specified for bruteforce mode.")
            return
        bit_length = args.length if args.bruteforce_mode != 3 else None

        if args.bruteforce_mode == 1:
            bruteforce_mode_1(rfdevice, bit_length, protocols, args.pulselength, args.length)
        elif args.bruteforce_mode == 2:
            bruteforce_mode_2(rfdevice, bit_length, protocols, args.pulselength, args.length)
        elif args.bruteforce_mode == 3 and args.base_code is not None:
            bruteforce_mode_3(rfdevice, args.base_code, protocols, args.pulselength)
        else:
            print("For -bf 3, a base code (-s) must be specified.")
    else:
        print("Either -s (base code for bruteforce mode 3), -m (single code), or -bf (bruteforce mode) must be specified.")

    rfdevice.cleanup()

if __name__ == "__main__":
    main()
