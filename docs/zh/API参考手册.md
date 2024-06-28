# API 参考手册

中文 | [English](../en/API_Reference.md)

## 简介

该文档详述了终端 GT06 协议的功能接口与使用方法。该模块只实现了 GT06 协议的基础接口功能，实际开发中需要根据对接的服务平台进行二次开发，补充服务平台自定义的消息与消息补充项，不同的服务平台会有自己的定义规则，需参考其提供的开发文档进行二次开发。

## 功能接口

### GT06 模块导入初始化

**参数说明：**

|参数|类型|说明|
|:---|:---|:---|
|ip|str|服务端 IP 地址，默认：None，`ip` 与 `domain` 二选一|
|port|int|服务端端口号，默认：None|
|domain|str|服务端域名地址，默认：None，`ip` 与 `domain` 二选一|
|timeout|int|消息数据读取超时时间，单位：秒，默认：5|

**返回值：**

|数据类型|说明|
|:---|:---|
|obj|GT06 客户端实例对象|

**示例：**

```python
from usr.gt06 import GT06

# 替换成你自己的服务器 IP 和端口。
ip = "xxx.xxx.xxx.xxx"
port = 9000
domain = None
timeout = 5

gt06_obj = GT06(ip=ip, port=port, domain=domain, timeout=timeout)
```

### set_callback

- 设置回调函数，用于接收服务端下发的消息指令。
- GT06 协议中只有 `protocol_no` 为 `0x80` 时为服务端向终端发送指令，当收到该协议号的消息时，需使用 `report_device_cmd` 接口进行应答。
- 根据不同的服务平台，会有不同的消息定义，同理只要是服务端下发的消息，都可通过回调函数进行接受处理与应答。

**参数说明：**

|参数|类型|说明|
|:---|:---|:---|
|callback|function|回调函数，回到函数有一个形参 args，args 为一个字典，有 3 个 key 值，`protocol_no`，`msg_no`，`content`，详见`回调函数参数说明`|

**回调函数参数说明：**

|参数|类型|说明|
|:---|:---|:---|
|protocol_no|int|协议号，默认为`0x80`|
|msg_no|int|服务端消息流水号|
|content|dict|服务端下发指令信息<br>`server_flag`（int） - 服务器标志位<br>`cmd_data`（str） - 指令内容|

**返回值：**

|数据类型|说明|
|:---|:---|
|bool|`True` - 成功<br>`False` - 失败|

**示例：**

```python
def test_callback(args):
    protocol_no = args["protocol_no"]
    msg_no = args["msg_no"]
    content = args["content"]

gt06_obj.set_callback(test_callback)
# True
```

### set_device_status

- 设置设备状态，该功能用于上报设备状态信息消息，设置的状态信息会进行存储，因为该消息同时也作为心跳消息，所以当设备状态参数发生变化时，需及时调用该方法进行更新设备状态信息。

**参数说明：**

|参数|类型|说明|
|:---|:---|:---|
|defend|int|是否设防<br>1 - 是<br>0 - 否|
|acc|int|ACC 状态<br>1 - 高<br>0 - 低|
|charge|int|是否充电<br>1 - 已接电源充电<br>0 - 未接电源充电|
|alarm|int|告警信息<br>0 - 正常<br>1 - 震动告警<br>2 - 断电告警<br>3 - 低电告警<br>4 - SOS 求救|
|gps|int|GPS 是否已定位<br>1 - 是<br>0 - 否|
|power|int|油电状态<br>1 - 断开<br>0 - 接通|
|voltage_level|int|电压等级<br>0 - 无电（关机）<br>1 - 电量极低（不足以打电话发短信等）<br>2 - 电量很低（低电报警）<br>3 - 电量低（可正常使用）<br>4 - 电量中<br>5 - 电量高<br>6 - 电量极高|
|gsm_signal|int|GSM 信号强度等级<br>0 - 无信号<br>1 - 信号极弱<br>2 - 信号较弱<br>3 - 信号良好<br>4 - 信号强|

**返回值：**

|数据类型|说明|
|:---|:---|
|bool|`True` - 成功<br>`False` - 失败|

**示例：**

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

- 连接服务器。

**参数说明：**

- 无

**返回值：**

|数据类型|说明|
|:---|:---|
|bool|`True` - 成功<br>`False` - 失败|

**示例：**

```python
gt06_obj.connect()
# True
```

### disconnect

- 断开服务器连接。

**参数说明：**

- 无

**返回值：**

|数据类型|说明|
|:---|:---|
|bool|`True` - 成功<br>`False` - 失败|

**示例：**

```python
gt06_obj.disconnect()
# True
```

### login

- 设备登录。

**参数说明：**

|参数|类型|说明|
|:---|:---|:---|
|imei|str|IMEI|

**返回值：**

|数据类型|说明|
|:---|:---|
|bool|`True` - 成功<br>`False` - 失败|

**示例：**

```python
import modem

imei = modem.getDevImei()
gt06_obj.login(imei)
# True
```

### report_location

- GPS & LBS 定位信息与设备状态信息上报，当需要同步上传设备状态信息时，需确认设备信息是否有变化，如有变化需先调用 `set_device_status` 接口更新设备状态信息，再调用该接口进行信息上报。

**参数说明：**

|参数|类型|说明|
|:---|:---|:---|
|date_time|str|时间，数据格式: `YYMMDDHHmmss`|
|satellite_num|int|卫星数，取值范围: 0 ~ 15|
|latitude|float|纬度，单位: 度|
|longitude|float|经度，单位: 度|
|speed|int|速度，单位: km/h|
|course|int|航向，单位: 度，范围: 0 ~ 360，正北为0度|
|lat_ns|int|纬度方位，0 - 南纬，1 - 北纬|
|lon_ew|int|经度方位，0 - 东经，1 - 西经|
|gps_onoff|int|GPS是否已定位，0 - 未定位，1 - 已定位|
|is_real_time|int|实时/差分 GPS，0 - 实时，1 - 差分|
|mcc|int|移动用户所属国家代号（Mobile Country Code）|
|mnc|int|移动网号码（Mobile Network Code）|
|lac|int|位置区码（Location Area Code）|
|cell_id|int|移动基站（Cell Tower ID）取值范围: 0x000000 ~ 0xFFFFFF|
|include_device_status|bool|是否同步上传设备状态<br>`True` - 是<br>`False` - 否<br>默认：`False`|

**返回值：**

|数据类型|说明|
|:---|:---|
|bool|`True` - 成功<br>`False` - 失败|

**示例：**

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

- 设备状态信息上报，该接口与 `set_device_status` 接口结合使用，在调用之前需先调用 `set_device_status` 接口更新设备状态信息，再进行设备信息状态上报。

**参数说明：**

- 无

**返回值：**

|数据类型|说明|
|:---|:---|
|bool|`True` - 成功<br>`False` - 失败|

**示例：**

```python
gt06_obj.report_device_status()
# True
```

### report_device_cmd

- 服务端下发指令应答接口，该接口为应答服务端下发的指令消息，具体的指令数据规则由服务端规定。

**参数说明：**

|参数|类型|说明|
|:---|:---|:---|
|server_flag|int|服务器标志位，从回调函数参数中获取|
|cmd_data|str|设备端指令执行结果信息|

**返回值：**

|数据类型|说明|
|:---|:---|
|bool|`True` - 成功<br>`False` - 失败|

**示例：**

```python
server_flag = 12345
cmd_data = "DYD=Success!"
gt06_obj.report_device_cmd(server_flag, cmd_data)
# True
```
