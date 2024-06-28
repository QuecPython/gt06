# Copyright (c) Quectel Wireless Solution, Co., Ltd.All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
@file      :gt06_msg.py
@author    :Jack Sun (jack.sun@quectel.com)
@brief     :<description>
@version   :1.0.0
@date      :2022-07-07 16:11:42
@copyright :Copyright (c) 2022
"""

import usys
import math
import ubinascii

from usr.crc_itu import crc16
from usr.logging import getLogger
from usr.common import str_fill, SerialNo

logger = getLogger(__name__)

_serial_no_obj = SerialNo(start_no=1)


class GT06MsgBase(object):
    """This is base class for GT06 protocol message."""

    def __init__(self):
        self.__msg_len = ""
        self.__protocal_no = ""
        self.__msg_no = ""
        self.__crc_code = ""
        self.__start_byte = "7878"
        self.__end_byte = "0d0a"
        self.__content_info = {}
        self.__content_byte = ""
        self.__serial_no_obj = _serial_no_obj

        self.__imei = ""
        self.__gps = ""
        self.__lbs = ""
        self.__device_status = ""
        self.__device_cmd = ""

    def __init_protocal_no(self, protocal_no):
        """Init protocal number to hex.

        Args:
            protocal_no(int): protocal number
                0x01 - login
                0x12 - GPS
                0x13 - device status(heart beat)
                0x15 - device command
                0x16 - GPS & device status
        """
        self.__protocal_no = str_fill(hex(protocal_no)[2:], target_len=2)

    def __init_content_byte(self):
        """Init message content by different protocal number.

        The function is implemented in the subclass.
        """
        pass

    def __init_msg_len(self):
        """Init message length.

        Raises:
            ValueError: Total message length is less than or equal to 250.
        """
        _msg_len = 5 + int(len(self.__content_byte) / 2)
        if _msg_len > 0xFF:
            raise ValueError("Message concent bit length is greater than 250!")
        self.__msg_len = str_fill(hex(_msg_len)[2:], target_len=2)

    def __init_msg_no(self):
        """Init message serial number.

        Serial number is start from 1.
        """
        _msg_no = self.__serial_no_obj.get_serial_no()
        self.__msg_no = str_fill(hex(_msg_no)[2:], target_len=4)

    def __init_crc_code(self):
        """Init error checking by CRC-ITU"""
        args = (self.__msg_len, self.__protocal_no, self.__content_byte, self.__msg_no)
        _msg_byte_info = ("{}" * len(args)).format(*args)
        _crc_code = crc16(bytearray([int(_msg_byte_info[i:i + 2], 16) for i in range(0, len(_msg_byte_info), 2)]))
        self.__crc_code = str_fill(hex(_crc_code)[2:], target_len=4)

    def get_msg(self):
        """Get byte message for different protocol number to send to server.

        Returns:
            tuple: (message_no, message_bytes)
                message_no(int): message serial number.
                message_bytes(byte): byte message infomation.
        """
        if not self.__protocal_no:
            return (-1, b'')

        self.__init_content_byte()
        self.__init_msg_len()
        self.__init_msg_no()
        self.__init_crc_code()

        args = (self.__start_byte, self.__msg_len, self.__protocal_no, self.__content_byte, self.__msg_no, self.__crc_code, self.__end_byte)
        logger.debug("get_msg args: %s" % str(args))
        _msg_byte_info = ("{}" * len(args)).format(*args)
        logger.debug("get_msg _msg_byte_info: %s" % _msg_byte_info)
        _msg_byte = bytearray([int(_msg_byte_info[i:i + 2], 16) for i in range(0, len(_msg_byte_info), 2)]).decode().encode()
        return (int(self.__msg_no, 16), _msg_byte)

    def set_gps(self, date_time, satellite_num, latitude, longitude, speed, course, lat_ns, lon_ew, gps_onoff, is_real_time):
        """Set GPS infomations.

        This function is necessary for protalcal number 0x12, 0x16.

        Args:
            date_time(str): This field format is `YYMMDDHHmmss`. .e.g: `220707164353`.
            satellite_num(int): Satellite numbers. This number is not greater than 15.
            latitude(float): latitude. unit: degree.
            longitude(float): longitude. unit: degree.
            speed(int): unit: km/h.
            course(int): unit: degree.
            lat_ns(int): latitude direction.
                0 - South
                1 - North
            lon_ew(int): longitude direction.
                0 - East
                1 - Western
            gps_onoff(int): whether GPS is positioned.
                0 - not targeted
                1 - targeted
            is_real_time(int): real time/Differential GPS
                0 - real time GPS
                1 - differential GPS

        Returns:
            bool: True - success, False - failed.
        """
        try:
            date_time_byte = ubinascii.hexlify(bytearray([int(date_time[i:i + 2]) for i in range(0, len(date_time), 2)])).decode()
            gps_len_byte = "c"
            satellite_num_byte = hex(satellite_num if satellite_num <= 15 else 15)[2:]
            latitude_byte = str_fill(hex(math.trunc(latitude * 6 * 3 * 10 ** 5))[2:], target_len=8)
            longitude_byte = str_fill(hex(math.trunc(longitude * 6 * 3 * 10 ** 5))[2:], target_len=8)
            speed_byte = str_fill(hex(int(speed))[2:], target_len=2)
            status_course_args = (is_real_time, gps_onoff, lon_ew, lat_ns, str_fill(bin(int(course))[2:], target_len=10))
            status_course_bit = ("{}" * len(status_course_args)).format(*status_course_args)
            status_course_byte = str_fill(hex(int(status_course_bit, 2))[2:], target_len=4)
            gps_args = (date_time_byte, gps_len_byte, satellite_num_byte, latitude_byte, longitude_byte, speed_byte, status_course_byte)
            logger.debug("set_gps gps_args: %s" % str(gps_args))
            self.__gps = ("{}" * len(gps_args)).format(*gps_args)
            logger.debug("set_gps self.__gps: %s" % str(self.__gps))
            return True
        except Exception as e:
            usys.print_exception(e)
            return False

    def set_lbs(self, mcc, mnc, lac, cell_id):
        """Set LBS infomation.

        This LBS infomation is not in GT06 protocol document.

        Args:
            mcc(int): Mobile Country Code
            mnc(int): Mobile Network Code
            lac(int): Location Area Code. Range: [0x0001:0xFFFE]
            cell_id(int): Cell Tower ID. Range: [0x000000:0xFFFFFF]

        Returns:
            bool: True - success, False - failed.
        """
        try:
            mcc_byte = str_fill(hex(mcc)[2:], target_len=4)
            mnc_byte = str_fill(hex(mnc)[2:], target_len=2)
            lac_byte = str_fill(hex(lac)[2:], target_len=4)
            if cell_id > 0xFFFFFF:
                cell_id = 0xFFFFFF
            cell_id_byte = str_fill(hex(cell_id)[2:], target_len=6)
            lbs_args = (mcc_byte, mnc_byte, lac_byte, cell_id_byte)
            logger.debug("set_lbs lbs_args: %s" % str(lbs_args))
            self.__lbs = ("{}" * len(lbs_args)).format(*lbs_args)
            logger.debug("set_lbs __lbs: %s" % str(self.__lbs))
            return True
        except Exception as e:
            usys.print_exception(e)
            return False

    def set_device_status(self, defend, acc, charge, alarm, gps, power, voltage_level, gsm_signal):
        """Set device status.

        Args:
            defend(int):
                0 - not defend.
                1 - defend.
            acc(int):
                0 - ACC low
                1 - ACC high
            charge(int):
                0 - not charge
                1 - charged
            alarm(int):
                0 - normal
                1 - vibration alarm
                2 - power outage alarm
                3 - low battery alarm
                4 - SOS
            gps(int):
                0 - not targeted
                1 - targeted
            power(int):
                0 - oil and electricity disconnected
                1 - oil and electricity connected
            voltage_level(int):
                0 - power down
                1 - very very low battery(Can't call or text)
                2 - very low battery(low battery alarm)
                3 - low battery(Normal use)
                4 - medium battery
                5 - high battery
                6 - full energe
            gsm_signal(int):
                0x00 - no signal
                0x01 - very weak signal
                0x02 - weak signal
                0x03 - good signal
                0x04 - strong signal

        Returns:
            bool: True - success, False - failed.
        """
        try:
            device_info_bit_args = (power, gps, str_fill(bin(alarm)[2:], target_len=3), charge, acc, defend)
            device_info_bit = ("{}" * len(device_info_bit_args)).format(*device_info_bit_args)
            _device_info = str_fill(hex(int(device_info_bit, 2))[2:], target_len=2)
            _voltage_level = str_fill(hex(voltage_level)[2:], target_len=2)
            _gsm_signal = str_fill(hex(gsm_signal)[2:], target_len=2)
            # This is additional info for server. Can change by different server.
            additional_alarm = str_fill(hex(int(alarm))[2:], target_len=2)
            language = "02"
            device_status_args = (_device_info, _voltage_level, _gsm_signal, additional_alarm, language)
            self.__device_status = ("{}" * len(device_status_args)).format(*device_status_args)
            logger.debug("set_device_status self.__device_status: %s" % self.__device_status)
            return True
        except Exception as e:
            usys.print_exception(e)
            return False


class GT06MsgParse(GT06MsgBase):
    """This class is for parsing server message."""

    def __init__(self):
        super().__init__()

    def __parse_msg_len(self):
        """Parse message len from server message."""
        self.__msg_len = self.__msg_byte[4:6]

    def __parse_protocol_no(self):
        """Parse protocol number from server message."""
        self.__protocal_no = self.__msg_byte[6:8]

    def __parse_content(self):
        """Parse content information from server message."""
        self.__content_byte = self.__msg_byte[8:-12]
        if self.__content_byte:
            _server_flag = int(self.__content_byte[2:10], 16)
            _cmd_data_byte = self.__content_byte[10:]
            _cmd_data = bytearray([_cmd_data_byte[i:i + 2] for i in range(0, len(_cmd_data_byte), 2)]).decode()
            self.__content_info = {
                "server_flag": _server_flag,
                "cmd_data": _cmd_data,
            }

    def __parse_msg_no(self):
        """Parse message serial number from server message."""
        self.__msg_no = self.__msg_byte[-12:-8]

    def __parse_crc_code(self):
        """Parse message error checking code (crc code) from server message."""
        self.__crc_code = self.__msg_byte[-8:-4]

    def __check_crc_code(self):
        """Check crc code is legal.

        Returns:
            bool: True - success, False - failed.
        """
        _msg_byte_info = self.__msg_byte[4:-8]
        _crc_code = crc16(bytearray([int(_msg_byte_info[i:i + 2], 16) for i in range(0, len(_msg_byte_info), 2)]))
        if _crc_code == int(self.__crc_code, 16):
            return True
        else:
            logger.error("Server message crc[%s] is not compare with actual calculation crc[%s]" % (int(self.__crc_code, 16), _crc_code))
            return False

    def set_msg(self, msg):
        """Set source server send message.

        Args:
            msg(byte): server message.

        Returns:
            bool: True - success, False - crc code check failed.
        """
        self.__msg_byte = ubinascii.hexlify(msg).decode()
        self.__parse_crc_code()
        if self.__check_crc_code():
            self.__parse_msg_len()
            self.__parse_protocol_no()
            self.__parse_content()
            self.__parse_msg_no()
            return True
        return False

    def get_msg_info(self):
        """Get parse message infomation.

        Returns:
            dict:
                protocol_no(int): protocal number
                msg_no(int): message serial number
                content(dict):
                    server_flag(int): server flag
                    cmd_data(str): server command data
        """
        _msg_info = {
            "protocol_no": int(self.__protocal_no, 16) if self.__protocal_no else -1,
            "msg_no": int(self.__msg_no, 16) if self.__msg_no else -1,
            "content": self.__content_info,
        }
        return _msg_info


class T01(GT06MsgBase):
    """Device login message."""

    def __init__(self):
        super().__init__()
        self.__init_protocal_no(0x01)

    def __init_content_byte(self):
        if not self.__imei:
            raise ValueError("IMEI is not set!")
        self.__content_byte = self.__imei

    def set_imei(self, imei):
        """Set device imei to login.

        Args:
            imei(str): IMEI number

        Returns:
            bool: True - success, False - failed.
        """
        try:
            self.__imei = str_fill(imei, target_len=16)
            return True
        except Exception as e:
            usys.print_exception(e)
            return False


class T12(GT06MsgBase):
    """Report GPS infomation.

    These functions set_gps, set_lbs are necessary for this message.
    """

    def __init__(self):
        super().__init__()
        self.__init_protocal_no(0x12)

    def __init_content_byte(self):
        if not self.__gps:
            raise ValueError("GPS info is not set!")
        self.__content_byte = self.__gps + self.__lbs


class T13(GT06MsgBase):
    """Report device status to server.

    This message is heart beat.

    The function set_device_status is necessary for this message.
    """

    def __init__(self):
        super().__init__()
        self.__init_protocal_no(0x13)

    def __init_content_byte(self):
        if not self.__device_status:
            raise ValueError("Device status is not set!")
        self.__content_byte = self.__device_status


class T15(GT06MsgBase):
    """Report device command to server."""

    def __init__(self):
        super().__init__()
        self.__init_protocal_no(0x15)

    def __init_content_byte(self):
        if not self.__device_cmd:
            raise ValueError("Device command info is not set!")
        self.__content_byte = self.__device_cmd

    def set_device_cmd(self, server_flag, cmd_data):
        """Set device command.

        Args:
            server_flag(int): this data is from server command message.
            cmd_data(str): device command data(This data format is provided by server.)

        Returns:
            bool: True - success, False - failed.
        """
        try:
            _server_flag = str_fill(hex(server_flag)[2:], target_len=8)
            _cmd_data = ubinascii.hexlify(cmd_data).decode()
            _cmd_len = str_fill(hex(4 + int(len(_cmd_data) / 2))[2:], target_len=2)
            cmd_args = (_cmd_len, _server_flag, _cmd_data)
            self.__device_cmd = ("{}" * len(cmd_args)).format(*cmd_args)
            return True
        except Exception as e:
            usys.print_exception(e)
            return False


class T16(GT06MsgBase):
    """Report GPS, LBS, device status to server by one message.

    These functions set_gps, set_lbs, set_device_status are necessary for this message.
    """

    def __init__(self):
        super().__init__()
        self.__init_protocal_no(0x16)

    def __init_content_byte(self):
        if not self.__gps:
            raise ValueError("GPS info is not set!")
        if not self.__device_status:
            raise ValueError("Device status is not set!")
        self.__content_byte = self.__gps + str_fill(hex(int(len(self.__lbs) / 2))[2:], target_len=2) + self.__lbs + self.__device_status
