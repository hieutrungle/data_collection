import paho.mqtt.client as mqtt  # import the client1
import time
import json
import sys
import utils
from queue import Queue

mqtt.Client.connected_flag = False


def on_log(client, userdata, level, buf):
    print("log: ", buf)


def on_subscribe(client, userdata, mid, granted_qos):
    print(f"Client {client} subscribes with qos {str(granted_qos)}")


def subcribe(host, port, username, password, topic, interval_ms, verbose):
    """generate data and send it to an MQTT broker"""
    sub_client_0 = utils.MQTTClient("sub_1")
    sub_client_0.on_message = utils.on_message  # attach function to callback
    # sub_client_0.on_log=on_log
    sub_client_0.on_connect = utils.on_connect
    sub_client_0.on_disconnect = utils.on_disconnect
    sub_client_0.on_subscribe = on_subscribe

    if username:
        sub_client_0.username_pw_set(username, password)

    sub_client_0.connect(host, port)

    interval_secs = interval_ms / 1000.0

    sub_client_0.loop_start()
    ret = sub_client_0.subscribe(topic)

    try:
        time.sleep(10)
    finally:
        sub_client_0.loop_stop()

    while not sub_client_0.messages.empty():
        message = sub_client_0.messages.get()
        if message is None:
            continue
        print("received from queue", message)


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

            subcribe(host, port, username, password, topic, interval_ms, verbose)
    except IOError as error:
        print("Error opening config file '%s'" % config_path, error)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        print("usage %s config.json" % sys.argv[0])
