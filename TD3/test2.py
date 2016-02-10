#!/usr/bin/python
# -*- coding: utf-8 -*-

import serial


def open_serial(port, baud, to):
    ser = serial.Serial(port=port, baudrate=baud, timeout=to)
    if ser.isOpen():
        return ser
    else:
        print 'SERIAL ERROR'


def close(ser):
    ser.close()


def write_data(ser, data):
    ser.write(data)


def read_data(ser, size=1):
    return ser.read(size)


def to_hex(val):
    return chr(val)


def decode_data(data):
    res = ''
    for d in data:
        res += hex(ord(d)) + ' '

    return res

def calcul_checksum(param1,param2,param3,param4,param5):
    return (~(param1+param2+param3+param4+param5)) & 255


if __name__ == '__main__':

    # we open the port
    serial_port = open_serial('/dev/ttyUSB0', 1000000, to=0.1)

    # we create the packet for a LED ON command
    # two start bytes
    start = 0xff
    data_start = to_hex(start)

    # id of the motor (here 1), you need to change
    id2 = 0x02
    data_id = to_hex(id2)

    # lenght of the packet
    length = 0x04
    data_lenght = to_hex(length)

    # instruction write= 0x03
    instruction = 0x03
    data_instruction = to_hex(instruction)

    # instruction parameters
    param1 = 0x19
    param2 = 0x00
    data_param1 = to_hex(param1)  # LED address=0x19
    data_param2 = to_hex(param2)  # write 0x01

    # checksum (read the doc)
    data_checksum = calcul_checksum(id2,length,instruction,param1,param2)

    # we concatenate everything
    data = data_start + data_start + data_id + data_lenght + \
        data_instruction + data_param1 + data_param2 + to_hex(data_checksum)

    print decode_data(data)
    write_data(serial_port, data)

    # read the status packet (size 6)
    d = read_data(serial_port, 6)
    print decode_data(d)
