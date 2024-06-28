# API Reference

[中文](../zh/API参考手册.md) | English

## Introduction

This document details the functional interface and usage of the terminal GT06 protocol. This module only implements the basic interface function of the GT06 protocol. In actual development, secondary development needs to be carried out according to the connected service platform to supplement the customized messages and message supplementary items of the service platform. Different service platforms will have their own definition rules, which need to be Refer to the development documents provided by it for secondary development.

## Functional interface

### GT06 module import initialization

**Parameter Description:**

|Parameters|Type|Description|
|:---|:---|:---|
|ip|str|Server IP address, default: None, choose one of `ip` and `domain`|
|port|int|Server port number, default: None|
|domain|str|Server domain name address, default: None, choose one of `ip` and `domain`|
|timeout|int|Message data reading timeout, unit: seconds, default: 5|

**Return Value:**

|Data type|Description|
|:---|:---|
|obj|GT06 client instance object|

**Example:**

```python
from usr.gt06 import GT06

# Replace it with your own server IP and port.
ip = "xxx.xxx.xxx.xxx"
port = 9000
domain = None
timeout = 5

gt06_obj = GT06(ip=ip, port=port, domain=domain, timeout=timeout)
```

### set_callback

- Set a callback function to receive message instructions sent by the server.
- In the GT06 protocol, only when `protocol_no` is `0x80`, the server sends instructions to the terminal. When receiving a message with this protocol number, it needs to use the `report_device_cmd` interface to respond.
- Depending on the service platform, there will be different message definitions. Similarly, as long as the message is sent by the server, it can be accepted, processed and responded to through the callback function.

**Parameter Description:**

|Parameters|Type|Description|
|:---|:---|:---|
|callback|function|Callback function. The return function has a formal parameter args. args is a dictionary with 3 key values, `protocol_no`, `msg_no`, `content`. For details, see `Callback Function Parameter Description`|

**Callback Function Parameter Description:**

|Parameters|Type|Description|
|:---|:---|:---|
|protocol_no|int|Protocol number, default is `0x80`|
|msg_no|int|Server message serial numberServer message serial number|
|content|dict|The server issues command information<br>`server_flag`(int) - server flag bit<br>`cmd_data`(str) - command content|

**Return Value:**

|Data type|Description|
|:---|:---|
|bool|`True` - Success<br>`False` - Fail|

**Example:**

```python
def test_callback(args):
    protocol_no = args["protocol_no"]
    msg_no = args["msg_no"]
    content = args["content"]

gt06_obj.set_callback(test_callback)
# True
```

### set_device_status

- Set the device status. This function is used to report device status information messages. The set status information will be stored. Because this message also serves as a heartbeat message, when the device status parameters change, this method needs to be called in time to update the device status information.

**Parameter Description:**

|Parameters|Type|Description|
|:---|:---|:---|
|defend|int|Whether to fortify<br>1 - Yes<br>0 - No|
|acc|int|ACC Status<br>1 - High<br>0 - Low|
|charge|int|Whether to charge<br>1 - Connected to the power supply for charging<br>0 - Not connected to the power supply for charging|
|alarm|int|Alarm information<br>0 - Normal<br>1 - Vibration alarm<br>2 - Power failure alarm<br>3 - Low power alarm<br>4 - SOS for help|
|gps|int|Has GPS positioned<br>1 - Yes<br>0 - No|
|power|int|Oil and electricity status<br>1 - Disconnected<br>0 - Connected|
|voltage_level|int|Voltage level<br>0 - No power (power off)<br>1 - Very low battery (not enough to make calls and text messages, etc.)<br>2 - Very low battery (low battery alarm)<br>3 - Low battery ( Can be used normally)<br>4 - Medium battery<br>5 - High battery<br>6 - Very high battery|
|gsm_signal|int|GSM signal strength level<br>0 - No signal<br>1 - Very weak signal<br>2 - Weak signal<br>3 - Good signal<br>4 - Strong signal|

**Return Value:**

|Data type|Description|
|:---|:---|
|bool|`True` - Success<br>`False` - Fail|

**Example:**

```python
defend = 1
acc = 1
charge = 0
alarm = 1
gps = 1
power = 0
voltage_level = 5
gsm_signal = 4
gt06_obj.set_device_status(defend, acc, charge, alarm, gps, power, voltage_level, gsm_signal)
```

### connect

- Connect to the server.

**Parameter Description:**

- No Parameters.

**Return Value:**

|Data type|Description|
|:---|:---|
|bool|`True` - Success<br>`False` - Fail|

**Example:**

```python
gt06_obj.connect()
# True
```

### disconnect

- Disconnect from the server.

**Parameter Description:**

- No Parameters.

**Return Value:**

|Data type|Description|
|:---|:---|
|bool|`True` - Success<br>`False` - Fail|

**Example:**

```python
gt06_obj.disconnect()
# True
```

### login

- Device login.

**Parameter Description:**

|Parameters|Type|Description|
|:---|:---|:---|
|imei|str|IMEI|

**Return Value:**

|Data type|Description|
|:---|:---|
|bool|`True` - Success<br>`False` - Fail|

**Example:**

```python
import modem

imei = modem.getDevImei()
gt06_obj.login(imei)
# True
```

### report_location

- GPS & LBS positioning information and device status information are reported. When device status information needs to be uploaded synchronously, it is necessary to confirm whether the device information has changed. If there is a change, the `set_device_status` interface must be called first to update the device status information, and then call this interface to report the information. .

**Parameter Description:**

|Parameters|Type|Description|
|:---|:---|:---|
|date_time|str|Time, data format: `YYMMDDHHmmss`|
|satellite_num|int|Number of satellites, value range: 0 ~ 15|
|latitude|float|Latitude|
|longitude|float|Longitude|
|speed|int|Speed, unit: km/h|
|course|int|Heading, unit: degree, range: 0 ~ 360, true north is 0 degrees|
|lat_ns|int|Latitude direction, 0 - south latitude, 1 - north latitude|
|lon_ew|int|Longitude direction, 0 - east longitude, 1 - west longitude|
|gps_onoff|int|Whether the GPS has been positioned, 0 - not positioned, 1 - positioned|
|is_real_time|int|Real-time/Differential GPS, 0 - Real-time, 1 - Differential|
|mcc|int|Mobile Country Code|
|mnc|int|Mobile Network Code|
|lac|int|Location Area Code|
|cell_id|int|Cell Tower ID, Value range: 0x000000 ~ 0xFFFFFF|
|include_device_status|bool|Whether to upload device status synchronously<br>`True` - yes<br>`False` - no<br>default: `False`|

**Return Value:**

|Data type|Description|
|:---|:---|
|bool|`True` - Success<br>`False` - Fail|

**Example:**

```python
import net
import utime

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
include_device_status = False

gt06_obj.report_location(
    date_time, satellite_num, latitude, longitude, speed, course, lat_ns, lon_ew, gps_onoff, is_real_time,
    mcc, mnc, lac, cell_id, include_device_status
)
# True
```

### report_device_status

- To report device status information, this interface is used in conjunction with the `set_device_status` interface. Before calling, you need to call the `set_device_status` interface to update the device status information, and then report the device information status.

**Parameter Description:**

- No parameters.

**Return Value:**

|Data type|Description|
|:---|:---|
|bool|`True` - Success<br>`False` - Fail|

**Example:**

```python
gt06_obj.report_device_status()
# True
```

### report_device_cmd

- The server issues an instruction response interface. This interface responds to the instruction message issued by the server. The specific instruction data rules are specified by the server.

**Parameter Description:**

|Parameters|Type|Description|
|:---|:---|:---|
|server_flag|int|Server flag bit, obtained from callback function parameters|
|cmd_data|str|Device-side command execution result information|

**Return Value:**

|Data type|Description|
|:---|:---|
|bool|`True` - Success<br>`False` - Fail|

**Example:**

```python
server_flag = 12345
cmd_data = "DYD=Success!"
gt06_obj.report_device_cmd(server_flag, cmd_data)
# True
```
