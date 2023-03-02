"""a simple sensor data generator that sends to an MQTT broker via paho"""
"script from https://gist.github.com/marianoguerra/be216a581ef7bc23673f501fdea0e15a"

import sys
import json
import time
import random
import paho.mqtt.client as mqtt
import utils


def on_publish(client, userdata, result):  # create function for callback
    print(f"client {client}; result: {result}")


def generate(host, port, username, password, topic, sensors, interval_ms, verbose):
    """generate data and send it to an MQTT broker"""
    pub_client_0 = utils.MQTTClient("pub_1")

    if username:
        pub_client_0.username_pw_set(username, password)
    pub_client_0.on_connect = utils.on_connect
    pub_client_0.on_disconnect = utils.on_disconnect
    # if verbose:
    pub_client_0.on_message = utils.on_message
    pub_client_0.on_publish = on_publish
    pub_client_0.connect(host, port)

    keys = list(sensors.keys())
    interval_secs = interval_ms / 1000.0

    pub_client_0.loop_start()
    if pub_client_0.connected_flag == False:
        print("Waiting for connection")
        time.sleep(1)
    pub_client_0.loop_stop()

    while True:
        sensor_id = "CPU Temp"
        sensor = sensors[sensor_id]

        min_val, max_val = sensor.get("range", [0, 100])
        val = random.randint(min_val, max_val)
        sensor_path = sensor.get("path", "")
        if sensor_path != "":
            with open(sensor.get("path")) as handle:
                read_val = handle.read().strip()
                read_val = float(read_val) / 1000
                val = read_val
        data = {"id": sensor_id, "value": val}

        for key in ["lat", "lng", "unit", "type", "description"]:
            value = sensor.get(key)

            if value is not None:
                data[key] = value

        payload = json.dumps(data)

        ret = pub_client_0.publish(topic, payload)
        time.sleep(interval_secs)


def main(config_path):
    """main entry point, load and validate config and call generate"""
    try:
        with open(config_path) as handle:
            config = json.load(handle)
            mqtt_config = config.get("mqtt", {})
            misc_config = config.get("misc", {})
            sensors = config.get("sensors")

            interval_ms = misc_config.get("interval_ms", 500)
            verbose = misc_config.get("verbose", False)

            if not sensors:
                print("no sensors specified in config, nothing to do")
                return

            host = mqtt_config.get("host", "192.168.0.2")
            port = mqtt_config.get("port", 1883)
            username = mqtt_config.get("username")
            password = mqtt_config.get("password")
            topic = mqtt_config.get("topic", "mqttgen")

            generate(
                host, port, username, password, topic, sensors, interval_ms, verbose
            )
    except IOError as error:
        print("Error opening config file '%s'" % config_path, error)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        print("usage %s config.json" % sys.argv[0])
