# Instruction Manual

[中文](../zh/使用说明手册.md) | English

**Note:**

- This project only provides GT06 protocol client functions. The server needs to connect to the server provided by the third party, or build an open source server by yourself for use.
- This project only provides the basic functional interface of the GT06 protocol, and the specific usage business needs to be developed separately.
- This project only implements the basic messages of the GT06 protocol. The message functions defined by the service platform require secondary development. The data format of the server's downlink data is provided by the service platform in definition documents.
- The GT06 protocol requires the storage and retransmission of failed data. This project does not store failed data. The storage and retransmission of failed data need to be implemented at the business layer.
- The protocol requires the device to send heartbeat data packets regularly. This logic is a business function. This protocol only provides device status update and reporting interfaces. The specific timing reporting logic will be developed in the business.
- Server-side downlink data is received and processed through the `set_callback` function to register a callback function.

## Instructions For Use

### 1. Function Module Import Initialization

- `ip`, `port`, `domain` should be replaced according to the actual docking service environment.

```python
from usr.gt06 import GT06

ip = "xxx.xxx.xxx.xxx"
port = 8888
domain = None
timeout = 5

gt06_obj = GT06(
    ip=ip, port=port, domain=domain, timeout=timeout
)
```

### 2. Set Callback Function

- The processing server delivers business data, and the data format must be processed according to the rules defined by the connected service platform.
- When referring to the documentation, I saw that some server-side instructions contain `unicode` encoded data. Currently, QuecPython does not support decoding and supports instructions in `utf-8` encoding format.

```python
def test_callback(args):
    protocol_no = args["protocol_no"]
    msg_no = args["msg_no"]
    content = args["content"]
    if protocol_no == 0x80:
        server_flag = content.get("server_flag")
        cmd_data = content.get("cmd_data")
        # TODO: Business logic processing and message response, the following are examples.
        if cmd_data == "DYD,000000#":
            device_cmd = "DYD=Success!"
            global gt06_obj
            gt06_obj.report_device_cmd(server_flag, device_cmd)

set_callback_res = gt06_obj.set_callback(test_callback)
```

### 3. Set Device Status Information

- This step is used to send heartbeat information. You need to manually call the device information reporting interface to send it, that is, step 8.

```python
defend = 1
acc = 1
charge = 0
alarm = 1
gps = 1
power = 0
voltage_level = 5
gsm_signal = 4

set_device_status_res = gt06_obj.set_device_status(
    defend, acc, charge, alarm, gps, power, voltage_level, gsm_signal
)
```

### 4. Connect To The Server

```python
connect_res = gt06_obj.connect()
```

### 6. Device Login

- Use the IMEI number of the device as the unique identifier of the device to log in. You need to enter the IMEI number of the device on the server before you can log in successfully.

```python
import modem

imei = modem.getDevImei()
login_res = gt06_obj.login(imei)
```

### 7. Report Device Location Information

- This interface can report device status information synchronously. If you need to report device status information synchronously, perform step 3 first, and then directly set the `include_device_status` parameter value to `True`.

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
    date_time, satellite_num, latitude, longitude, speed,
    course, lat_ns, lon_ew, gps_onoff, is_real_time,
    mcc, mnc, lac, cell_id, include_device_status
)
```

### 8. Report Device Status Information

- This message is also a heartbeat message, and the protocol requires that it be sent every three minutes. It is recommended that users call step 3 regularly to update the device status, and then report the status information.

```python
gt06_obj.report_device_status()
```
