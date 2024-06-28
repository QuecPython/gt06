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
@file      :test_gt06.py
@author    :Jack Sun (jack.sun@quectel.com)
@brief     :<description>
@version   :1.0.0
@date      :2022-07-09 14:38:27
@copyright :Copyright (c) 2022
"""

import net
import utime
import modem
from usr.gt06 import GT06
from usr.logging import getLogger

logger = getLogger(__name__)

gt06_obj = None


def test_init_location_args():
    now_time = utime.localtime()
    date_time = ("{:0>2d}" * 6).format(*now_time[:6])[2:]
    satellite_num = 12
    latitude = 31.824845156501
    longitude = 117.24091089413
    speed = 120
    course = 126
    lat_ns = 1
    lon_ew = 0
    gps_onoff = 1
    is_real_time = 1
    mcc = net.getServingMcc()
    mnc = net.getServingMnc()
    lac = net.getServingLac()
    cell_id = net.getServingCi()
    logger.debug("net.getServingCi(): %s" % cell_id)
    localtion_args = [date_time, satellite_num, latitude, longitude, speed, course, lat_ns, lon_ew, gps_onoff, is_real_time, mcc, mnc, lac, cell_id]
    return localtion_args


def test_gt06_server_callback(args):
    logger.debug("Server command args: %s" % str(args))


def test_gt06_init():
    # Replace it with your own server IP and port.
    ip = "xxx.xxx.xxx.xxx"
    port = 31450
    timeout = 5
    retry_count = 3
    life_time = 180

    global gt06_obj
    gt06_obj = GT06(ip=ip, port=port, timeout=timeout, retry_count=retry_count, life_time=life_time)
    err_msg = "Test GT06 init %s."

    assert isinstance(gt06_obj, GT06), err_msg % "falied"
    logger.debug(err_msg % "success")


def test_gt06_set_callback():
    err_msg = "Test GT06 set_callback %s"
    assert gt06_obj.set_callback(test_gt06_server_callback), err_msg % "falied"
    logger.debug(err_msg % "success")


def test_gt06_set_device_status():
    err_msg = "Test GT06 test_gt06_set_device_status %s"
    device_status = {
        "defend": 1,
        "acc": 1,
        "charge": 0,
        "alarm": 1,
        "gps": 1,
        "power": 0,
        "voltage_level": 5,
        "gsm_signal": 4,
    }
    assert gt06_obj.set_device_status(**device_status), err_msg % "falied"
    logger.debug(err_msg % "success")


def test_gt06_connect():
    err_msg = "Test GT06 connect %s"
    assert gt06_obj.connect(), err_msg % "falied"
    logger.debug(err_msg % "success")


def test_gt06_login():
    err_msg = "Test GT06 login %s"
    imei = modem.getDevImei()
    # imei = "0353413532150362"
    assert gt06_obj.login(imei), err_msg % "falied"
    logger.debug(err_msg % "success")


def test_gt06_report_location():
    err_msg = "Test GT06 report_location %s"
    localtion_args = test_init_location_args()
    localtion_args.append(False)
    assert gt06_obj.report_location(*localtion_args), err_msg % "falied"
    logger.debug(err_msg % "success")

    err_msg = "Test GT06 report location & device status %s"
    localtion_args = test_init_location_args()
    localtion_args.append(True)
    assert gt06_obj.report_location(*localtion_args), err_msg % "falied"
    logger.debug(err_msg % "success")


def test_gt06_report_device_status():
    err_msg = "Test GT06 report_device_status %s"
    assert gt06_obj.report_device_status(), err_msg % "falied"
    logger.debug(err_msg % "success")


def test_gt06_report_device_cmd():
    err_msg = "Test GT06 report_device_cmd %s"
    server_flag = 12345
    cmd_data = "DYD=Success!"
    assert gt06_obj.report_device_cmd(server_flag, cmd_data), err_msg % "falied"
    logger.debug(err_msg % "success")


def test_gt06_disconnect():
    err_msg = "Test GT06 disconnect %s"
    assert gt06_obj.disconnect(), err_msg % "falied"
    logger.debug(err_msg % "success")


def test_gt06():
    test_gt06_init()
    test_gt06_set_callback()
    test_gt06_set_device_status()
    test_gt06_connect()
    test_gt06_login()
    test_gt06_report_location()
    test_gt06_report_device_status()
    test_gt06_report_device_cmd()
    test_gt06_disconnect()


if __name__ == '__main__':
    test_gt06()
