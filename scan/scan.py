#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2014, LCI Technology Group, LLC
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#  Redistributions of source code must retain the above copyright notice, this
#  list of conditions and the following disclaimer.
#
#  Redistributions in binary form must reproduce the above copyright notice,
#  this list of conditions and the following disclaimer in the documentation
#  and/or other materials provided with the distribution.
#
#  Neither the name of LCI Technology Group, LLC nor the names of its
#  contributors may be used to endorse or promote products derived from this
#  software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import threading
import Queue
import socket
import errno
import sys
import time

TC = 5

# These are the top 1000 ports from the nmap services file.
PORTS = [80, 23, 443, 21, 22, 25, 3389, 110, 445, 139, 143, 53, 135, 3306,
         8080, 1723, 111, 995, 993, 5900, 1025, 587, 8888, 199, 1720, 465,
         548, 113, 81, 6001, 10000, 514, 5060, 179, 1026, 2000, 8443, 8000,
         32768, 554, 26, 1433, 49152, 2001, 515, 8008, 49154, 1027, 5666, 646,
         5000, 5631, 631, 49153, 8081, 2049, 88, 79, 5800, 106, 2121, 1110,
         49155, 6000, 513, 990, 5357, 427, 49156, 543, 544, 5101, 144, 7, 389,
         8009, 3128, 444, 9999, 5009, 7070, 5190, 3000, 5432, 1900, 3986, 13,
         1029, 9, 5051, 6646, 49157, 1028, 873, 1755, 2717, 4899, 9100, 119,
         37, 1000, 3001, 5001, 82, 10010, 1030, 9090, 2107, 1024, 2103, 6004,
         1801, 5050, 19, 8031, 1041, 255, 1048, 1049, 1053, 1054, 1056, 1064,
         1065, 2967, 3703, 17, 808, 3689, 1031, 1044, 1071, 5901, 100, 9102,
         1039, 2869, 4001, 5120, 8010, 9000, 2105, 636, 1038, 2601, 1, 7000,
         1066, 1069, 625, 311, 280, 254, 4000, 1761, 5003, 2002, 1998, 2005,
         1032, 1050, 6112, 3690, 1521, 2161, 1080, 6002, 2401, 4045, 902, 787,
         7937, 1058, 2383, 32771, 1033, 1040, 1059, 50000, 5555, 10001, 1494,
         2301, 3, 593, 3268, 7938, 1022, 1234, 1035, 1036, 1037, 1074, 8002,
         9001, 464, 1935, 2003, 497, 6666, 6543, 1352, 24, 3269, 1111, 407,
         500, 20, 2006, 1034, 1218, 15000, 3260, 4444, 264, 2004, 33, 1042,
         42510, 3052, 999, 1023, 1068, 222, 7100, 888, 563, 1717, 2008, 32770,
         992, 32772, 7001, 2007, 8082, 5550, 1043, 2009, 512, 5801, 1700,
         2701, 50001, 7019, 4662, 2065, 2010, 42, 161, 2602, 3333, 9535, 5100,
         2604, 4002, 5002, 1047, 1051, 1052, 1055, 1060, 1062, 1311, 16992,
         16993, 20828, 23502, 2702, 32769, 3283, 33354, 35500, 4443, 5225,
         5226, 52869, 55555, 55600, 6059, 64623, 64680, 65000, 65389, 6789,
         8089, 8192, 8193, 8194, 8651, 8652, 8701, 9415, 9593, 9594, 9595,
         1067, 13782, 366, 5902, 9050, 1002, 5500, 85, 10243, 1863, 1864,
         45100, 49999, 51103, 5431, 8085, 49, 6667, 90, 1503, 27000, 6881,
         1500, 340, 8021, 2222, 5566, 8088, 8899, 9071, 1501, 32773, 32774,
         5102, 6005, 9101, 9876, 163, 5679, 146, 1666, 648, 901, 83, 14238,
         3476, 5004, 5214, 8001, 8083, 8084, 9207, 12345, 30, 912, 2030, 2605,
         6, 541, 1248, 3005, 4, 8007, 2500, 306, 880, 1086, 1088, 1097, 2525,
         4242, 52822, 8291, 9009, 6101, 900, 2809, 7200, 1083, 12000, 211,
         32775, 800, 987, 705, 20005, 711, 13783, 6969, 10002, 10012, 10024,
         10025, 1045, 1046, 10566, 1057, 1061, 10616, 10617, 10621, 10626,
         10628, 10629, 1063, 1070, 1072, 1073, 1075, 1077, 1078, 1079, 1081,
         1082, 1085, 1093, 1094, 1096, 1098, 1099, 1100, 1104, 1106, 1107,
         1108, 11110, 1148, 1169, 11967, 1272, 1310, 13456, 14000, 14442,
         15002, 15003, 15660, 16001, 16016, 16018, 1687, 1718, 1783, 17988,
         1840, 19101, 1947, 19801, 19842, 20000, 20031, 20221, 20222, 2100,
         2119, 2135, 2144, 21571, 2160, 2190, 2260, 22939, 2381, 2399, 24800,
         2492, 25734, 2607, 2718, 27715, 2811, 28201, 2875, 30000, 3017, 3031,
         3071, 30718, 31038, 3211, 32781, 32782, 3300, 3301, 3323, 3325, 3351,
         3367, 33899, 3404, 34571, 34572, 34573, 3551, 3580, 3659, 3766, 3784,
         3801, 3827, 3998, 4003, 40193, 4126, 4129, 4449, 48080, 49158, 49159,
         49160, 50003, 50006, 5030, 50800, 5222, 5269, 5414, 5633, 5718,
         57294, 58080, 5810, 5825, 5877, 5910, 5911, 5925, 5959, 5960, 5961,
         5962, 5987, 5988, 5989, 60020, 6123, 6129, 6156, 63331, 6389, 65129,
         6580, 6788, 6901, 7106, 7625, 7627, 7741, 7777, 7778, 7911, 8086,
         8087, 8181, 8222, 8333, 8400, 8402, 8600, 8649, 8873, 8994, 9002,
         9010, 9011, 9080, 9220, 9290, 9485, 9500, 9502, 9503, 9618, 9900,
         9968, 691, 89, 1001, 1999, 2020, 212, 32776, 2998, 50002, 6003, 7002,
         2033, 32, 3372, 5510, 898, 425, 5903, 749, 99, 13722, 43, 458, 5405,
         6106, 6502, 7007, 10004, 10778, 1087, 1089, 1124, 1152, 1183, 1186,
         1247, 1296, 1334, 15742, 1580, 16012, 1782, 18988, 19283, 19315,
         19780, 2126, 2179, 2191, 2251, 24444, 2522, 27352, 27353, 27355,
         3011, 3030, 3077, 3261, 32784, 3369, 3370, 3371, 3493, 3546, 3737,
         3828, 3851, 3871, 3880, 3918, 3995, 4006, 4111, 4446, 49163, 49165,
         49175, 50389, 5054, 50636, 51493, 5200, 5280, 5298, 55055, 56738,
         5822, 5859, 5904, 5915, 5922, 5963, 61532, 61900, 62078, 7103, 7402,
         7435, 7443, 7512, 8011, 8090, 8100, 8180, 8254, 8500, 8654, 9091,
         9110, 9666, 9877, 9943, 9944, 9998, 1021, 32777, 32779, 9040, 2021,
         32778, 616, 666, 700, 1112, 1524, 2040, 38292, 4321, 49400, 545,
         5802, 84, 1084, 1600, 2048, 2111, 3006, 32780, 16080, 2638, 6547,
         6699, 9111, 1443, 1533, 2034, 2106, 555, 5560, 6007, 667, 720, 801,
         10003, 10009, 10180, 10215, 1090, 1091, 11111, 1114, 1117, 1119,
         1122, 1131, 1138, 1151, 1175, 1199, 1201, 12174, 12265, 1271,
         14441, 15004, 16000, 16113, 17877, 18040, 18101, 1862, 19350, 2323,
         2393, 2394, 25735, 2608, 26214, 2725, 27356, 2909, 3003, 30951, 3168,
         3221, 32783, 32785, 3322, 3324, 3390, 3517, 3527, 3800, 3809, 3814,
         3826, 3869, 3878, 3889, 3905, 3914, 3920, 3945, 3971, 4004, 4005,
         40911, 41511, 4279, 44176, 4445, 44501, 4550, 4567, 4848, 4900,
         49161, 49167, 49176, 50300, 5033, 50500, 5061, 5080, 5087, 5221,
         52673, 52848, 54045, 54328, 5440, 55056, 5544, 56737, 5678, 5730,
         57797, 5811, 5815, 5850, 5862, 5906, 5907, 5950, 5952, 6025, 60443,
         6100, 6510, 6565, 6566, 6567, 6689, 6692, 6779, 6792, 6839, 7025,
         7496, 7676, 7800, 7920, 7921, 7999, 8022, 8042, 8045, 8093, 8099,
         8200, 8290, 8292, 8300, 8383, 8800, 9003, 9081, 9099, 9200, 9418,
         9575, 9878, 9898, 9917, 1009, 2022, 417, 4224, 4998, 617, 6346, 70,
         714, 722, 777, 981, 10082, 1076, 2041, 301, 524, 5999, 668, 765,
         1007, 1417, 1434, 1984, 2038, 2068, 259, 416, 4343, 44443, 6009,
         7004, 1010, 109, 1461, 2035, 2046, 4125, 6006, 687, 7201, 726, 9103,
         911, 1011, 125, 1455, 2013, 2043, 2047, 481, 6668, 6669, 683, 903,
         2042, 2045, 256, 31337, 406, 44442, 5998, 783, 843, 9929, 10008,
         10011, 10022, 10023, 10034, 10058, 10160, 10873, 1092, 1095, 1102,
         1105, 1113, 1121, 1123, 1126, 1130, 1132, 1137, 1141, 1145, 1147,
         1149, 1154, 1163, 1164, 1165, 1166, 1174, 1185, 1187, 1192, 1198,
         12006, 12021, 12059, 1213, 1216, 1217, 12215, 12262, 1233, 1236,
         12380, 1244, 12452, 1259, 1277, 1287, 1300, 1301, 1309, 1322, 1328,
         13724, 15001, 15402, 1556, 1583, 1594, 1641, 1658, 16705, 16800,
         16851, 1688, 1719, 1721, 17595, 18018]


def print_results(fin, rq):
    while not fin.isSet():
        try:
            r = rq.get(timeout=1)
        except Queue.Empty:
            # No more results exit the thread.
            return

        print('{0}:{1} - {2}'.format(r[0], r[1], r[2]))


def check_port(fin, ip, pq, rq):
    while not fin.isSet():
        try:
            port = pq.get(timeout=1)
        except Queue.Empty:
            # No more ports to check exit the thread.
            return

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2.0)

        try:
            s.connect((ip, port))
            rq.put((ip, port, 'OPEN'))

        except socket.timeout:
            rq.put((ip, port, 'TIMEOUT'))

        except socket.error as e:
            if e.errno == errno.ECONNREFUSED:
                rq.put((ip, port, 'CLOSED'))

        finally:
            s.close()


def usage():
    print('Usage: scan.py ip_address [ports]')
    print('If ports is supplied it must be a comma delimited list. If it is')
    print('not supplied the list of Nmap top 10000 ports will be used.')

    sys.exit(1)


if __name__ == '__main__':

    # Process arguments.
    if len(sys.argv) == 2:
        ip = sys.argv[1]
        ports = PORTS

    elif len(sys.argv) == 3:
        ip = sys.argv[1]
        try:
            ports = sys.argv[2].split(',')
        except ValueError:
            print 'Ports must be a comma delimited list.'
            sys.exit(1)
    else:
        usage()


    # Setup the port and results queues and the finish event.
    pq = Queue.Queue()
    rq = Queue.Queue()
    fin = threading.Event()

    # Load the ports into the queue
    for p in ports:
        pq.put(p)

    # Setup and launch threads.
    for i in range(TC):
        t1 = threading.Thread(target=check_port, args=(fin, ip, pq, rq))
        t1.start()

    t = threading.Thread(target=print_results, args=(fin, rq))
    t.start()

    # Wait for threads to complete. Handle Ctrl-C if necessary.
    try:
        while threading.active_count() > 1:
            time.sleep(1)

    except KeyboardInterrupt:
        fin.set()
