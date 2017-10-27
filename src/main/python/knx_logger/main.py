import asyncio
from datetime import datetime
from xknx import XKNX
from influxdb import InfluxDBClient

client = InfluxDBClient('localhost', 8086, 'root', 'root', 'metrics')

try:
    client.create_database('metrics')
except Exception as e:
    print(e)


def get_current_time():
    return datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')


def send_metric_datapoint(measurement, location, value, timestamp):
    json_body = [
        {
            "measurement": measurement,
            "tags": {
                "location": location
            },
            "time": timestamp,
            "fields": {
                "value": value
            }
        }
    ]
    try:
        client.write_points(json_body, database="metrics")
    except Exception as e:
        print(e)


def telegram_received_cb(telegram):
    print("Telegram received: {0}".format(telegram))
    return []


def device_updated_cb(device):
    name = device.name
    value = device.resolve_state()

    parts = str(name).split(".", 1)
    location = parts[0]
    measurement = parts[1]
    current_time = get_current_time()

    print("{0}: {1} {2} is {3}".format(current_time, location, measurement, value))
    send_metric_datapoint(measurement, location, value, current_time)
    return []


async def main():
    xknx = XKNX(config='/root/xknx.yaml', telegram_received_cb=telegram_received_cb, device_updated_cb=device_updated_cb)
    await xknx.start(daemon_mode=True)
    await xknx.stop()


# pylint: disable=invalid-name
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()
