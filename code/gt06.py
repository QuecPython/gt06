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
@file      :gt06.py
@author    :Jack Sun (jack.sun@quectel.com)
@brief     :GT06 Protocol Client
@version   :1.0.0
@date      :2022-07-05 10:22:43
@copyright :Copyright (c) 2022
"""

import usys
import utime
import _thread

from usr.logging import getLogger
from usr.common import TCPUDPBase
from usr.gt06_msg import GT06MsgParse, T01, T12, T13, T15, T16

logger = getLogger(__name__)


class GT06(TCPUDPBase):
    """This class is option for GT06 protocol."""

    def __init__(self, ip=None, port=None, domain=None, timeout=5):
        """
        Args:
            ip: server ip address (default: {None})
            port: server port (default: {None})
            domain: server domain (default: {None})
            timeout: socket read data timeout. (default: {5})
        """
        super().__init__(ip=ip, port=port, domain=domain, method="TCP", timeout=timeout)
        self.__response_res = {}
        self.__device_status = (0, 0, 0, 0, 0, 0, 0, 0)

    def __get_packet_from_message(self, message):
        msgs = list(bytearray(message))
        start_indexs = []
        end_indexs = []
        first_index = 0
        for index, item in enumerate(msgs):
            if index + 1 < len(msgs):
                if item == 0x78 and msgs[index + 1] == 0x78:
                    start_indexs.append(index)
                elif item == 0x0D and msgs[index + 1] == 0x0A:
                    end_indexs.append(index + 1)

                if start_indexs and not end_indexs:
                    first_index = 0
                elif not start_indexs and end_indexs:
                    first_index = 1
        if first_index == 1:
            end_indexs.pop(0)

        packets = []
        for index, item in enumerate(start_indexs):
            if index < len(end_indexs):
                packets.append(bytearray(msgs[index:end_indexs[index] + 1]))

        if len(start_indexs) > len(end_indexs):
            message = bytearray(msgs[start_indexs[-1]:]).decode().encode()
        else:
            message = b""

        return packets, message

    def __get_response(self, protocol_no, msg_no):
        """Get server response data.

        Args:
            protocol_no(int): server response message id.
            msg_no(int): terminal request serial number.

        Returns:
            bool: True - success, False - falied
        """
        response_res = False
        count = 0
        while count < self.__timeout * 10:
            if self.status() != 0:
                break
            if self.__response_res.get(protocol_no) is not None:
                if self.__response_res[protocol_no].get(msg_no) is not None:
                    response_res = self.__response_res[protocol_no].pop(msg_no)
                    if self.__response_res.get(protocol_no) is not None:
                        self.__response_res.pop(protocol_no)
                    break
                elif self.__response_res[protocol_no].get(protocol_no) is not None:
                    response_res = self.__response_res[protocol_no].pop(protocol_no)
                    if self.__response_res.get(protocol_no) is not None:
                        self.__response_res.pop(protocol_no)
                    break
            utime.sleep_ms(100)
            count += 1
        return response_res

    def __format_gps_lbs(self, date_time, satellite_num, latitude, longitude, speed, course, lat_ns, lon_ew, gps_onoff, is_real_time,
                         mcc, mnc, lac, cell_id):
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
            mcc(int): Mobile Country Code
            mnc(int): Mobile Network Code
            lac(int): Location Area Code
            cell_id(int): Cell Tower ID. Range: [0x0001:0xFFFE]

        Returns:
            bool: True - success, False - failed.
        """
        try:
            if len(date_time) != 12:
                raise ValueError("date_time format error.")
            if satellite_num < 0 or satellite_num > 15:
                raise ValueError("Satellite numbers range is [0, 15]")
            if speed < 0 or speed > 255:
                raise ValueError("speed range is [0, 255]")
            if course < 0 and course > 359:
                raise ValueError("course range is [0, 359]")
            if lat_ns not in (0, 1):
                raise ValueError("lat_ns is not in (0, 1).")
            if lon_ew not in (0, 1):
                raise ValueError("lon_ew is not in (0, 1).")
            if gps_onoff not in (0, 1):
                raise ValueError("gps_onoff is not in (0, 1).")
            if is_real_time not in (0, 1):
                raise ValueError("is_real_time is not in (0, 1).")

            _gps = (date_time, satellite_num, latitude, longitude, speed, course, lat_ns, lon_ew, gps_onoff, is_real_time)
            _lbs = (mcc, mnc, lac, cell_id)
            return (_gps, _lbs)
        except Exception as e:
            usys.print_exception(e)
            return ()

    def parse(self, message):
        try:
            if message:
                packets, message = self.__get_packet_from_message(message)

                # Parse each packet in order
                for msg in packets:
                    logger.debug("__read_response: %s" % msg)
                    gt_msg_parse = GT06MsgParse()
                    if gt_msg_parse.set_msg(msg):
                        msg_info = gt_msg_parse.get_msg_info()
                        logger.debug("__read_response msg_info: %s" % msg_info)
                        if msg_info["protocol_no"] == 0x80:
                            if self.__callback:
                                _thread.start_new_thread(self.__callback, (msg_info,))
                            else:
                                raise OSError("callback funcion is not exists!")
                        else:
                            self.__response_res[msg_info["protocol_no"]] = {msg_info["msg_no"]: msg_info}
        except Exception as e:
            usys.print_exception(e)
        return message

    def send(self, data, protocol_no, msg_no):
        """Send data to server

        Args:
            data(bytes): message info
            protocol_no(int): server response protocol no
            msg_no(int): this send message serial number.

        Returns:
            dict: Return empty dict if not get server response, eles return server response data.
        """
        send_res = self.__send(data)
        logger.debug("__send res: %s" % send_res)
        if protocol_no is not None:
            resp_res = self.__get_response(protocol_no, msg_no)
            logger.debug("__get_response res: %s" % resp_res)
            resp_res = True if resp_res else False
        else:
            resp_res = send_res

        return resp_res

    def login(self, imei):
        """Device login server.

        Args:
            imei(str): device imei number

        Returns:
            bool: True - success, False - failed.
        """
        up_msg_obj = T01()
        up_msg_obj.set_imei(imei)
        msg_no, data = up_msg_obj.get_msg()
        logger.debug("login data: %s" % data)
        send_res = self.send(data, 0x01, msg_no)
        logger.debug("login send res: %s" % send_res)
        return send_res

    def report_location(self, date_time, satellite_num, latitude, longitude, speed, course, lat_ns, lon_ew, gps_onoff, is_real_time,
                        mcc, mnc, lac, cell_id, include_device_status=False):
        """Report GPS and LBS to server.

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
            mcc(int): Mobile Country Code
            mnc(int): Mobile Network Code
            lac(int): Location Area Code
            cell_id(int): Cell Tower ID. Range: [0x0001:0xFFFE]
            include_device_status(bool): Whether to report device status or not.
                True - report device status together
                False - not report device status together

        Returns:
            bool: True - success, False - failed.
        """
        _gps_lbs = self.__format_gps_lbs(
            date_time, satellite_num, latitude, longitude, speed, course, lat_ns, lon_ew, gps_onoff, is_real_time,
            mcc, mnc, lac, cell_id
        )
        if _gps_lbs:
            _gps, _lbs = _gps_lbs
            if include_device_status:
                up_msg_obj = T16()
                up_msg_obj.set_device_status(*self.__device_status)
            else:
                up_msg_obj = T12()
            up_msg_obj.set_gps(*_gps)
            up_msg_obj.set_lbs(*_lbs)
            msg_no, data = up_msg_obj.get_msg()
            logger.debug("report_location data: %s" % data)
            if include_device_status:
                send_res = self.send(data, 0x16, msg_no)
            else:
                send_res = self.send(data, None, msg_no)
            logger.debug("report_location send res: %s" % send_res)
            return send_res
        return False

    def set_device_status(self, defend=0, acc=0, charge=0, alarm=0, gps=0, power=0, voltage_level=0, gsm_signal=0):
        """Set device status.

        This function is heart beat function, so call this function when args change, these args are saved to send heart beat.

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
            if defend not in (0, 1):
                raise ValueError("defend is not (0, 1)")
            if acc not in (0, 1):
                raise ValueError("acc is not (0, 1)")
            if charge not in (0, 1):
                raise ValueError("charge is not (0, 1)")
            if alarm not in (0, 1, 2, 3, 4):
                raise ValueError("alarm is not (0, 1, 2, 3, 4)")
            if gps not in (0, 1):
                raise ValueError("gps is not (0, 1)")
            if power not in (0, 1):
                raise ValueError("power is not (0, 1)")
            if voltage_level not in (0, 1, 2, 3, 4, 5, 6):
                raise ValueError("voltage_level is not (0, 1, 2, 3, 4, 5, 6)")
            if gsm_signal not in (0, 1, 2, 3, 4):
                raise ValueError("gsm_signal is not (0, 1, 2, 3, 4)")

            self.__device_status = (defend, acc, charge, alarm, gps, power, voltage_level, gsm_signal)
            return True
        except Exception as e:
            usys.print_exception(e)
            return False

    def report_device_status(self):
        """Report device status to server.

        Call set_device_status before call this function.

        Returns:
            bool: True - success, False - failed.
        """
        if self.__device_status:
            up_msg_obj = T13()
            up_msg_obj.set_device_status(*self.__device_status)
            msg_no, data = up_msg_obj.get_msg()
            logger.debug("report_device_status data: %s" % data)
            send_res = self.send(data, 0x13, msg_no)
            logger.debug("report_device_status send res: %s" % send_res)
            return send_res
        return False

    def report_device_cmd(self, server_flag, cmd_data):
        """Report device command to server.

        Args:
            server_flag(int): this data is from server command message.
            cmd_data(str): device command data(This data format is provided by server.)

        Returns:
            bool: True - success, False - failed.
        """
        up_msg_obj = T15()
        up_msg_obj.set_device_cmd(server_flag, cmd_data)
        msg_no, data = up_msg_obj.get_msg()
        logger.debug("report_device_cmd data: %s" % data)
        send_res = self.send(data, None, msg_no)
        logger.debug("report_device_cmd send res: %s" % send_res)
        return send_res
