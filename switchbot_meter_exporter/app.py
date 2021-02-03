import os
import time
import uuid

from bluepy import btle
from prometheus_client import Gauge, Summary, CollectorRegistry, generate_latest
from flask import Flask, request

from switchbot_meter_exporter.delegate import Delegate


app = Flask(__name__)


REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')


@app.route('/metrics')
@REQUEST_TIME.time()
def metrics():
    target = request.args.get('target', None)
    if target is None:
        return 'require target parameter', 400

    registry = CollectorRegistry()
    uid = str(uuid.uuid1()).split('-')[0]
    body, status = get_metrics(target, registry, uid)
    return body, status, {'Content-Type': 'text/plane; charset=utf-8'}


def get_metrics(target, registry, uid):
    with ElapsedTime(uid):
        battery = Gauge('switchbot_meter_battery', 'meter battery value', registry=registry)
        temperature = Gauge('switchbot_meter_temperature', 'meter temp value', registry=registry)
        humidity = Gauge('switchbot_meter_humidity', 'meter humidity value', registry=registry)
        scanner = btle.Scanner().withDelegate(Delegate(target))
        scanner.scan(5.0)
        value = scanner.delegate.value
        if value is None:
            return 'failed', 500

        battery.set(value['battery'])
        temperature.set(value['temperature'])
        humidity.set(value['humidity'])

    return generate_latest(registry), 200


class ElapsedTime(object):
    def __init__(self, uid):
        self.uid = uid
        self.start = 0

    def __enter__(self):
        self.start = time.time()

    def __exit__(self, type, value, traceback):
        elapsed_time = time.time() - self.start
        app.logger.info(f'[{self.uid}] elapsed_time: {elapsed_time}s')


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 9234))
    app.run(debug=True, port=port)
