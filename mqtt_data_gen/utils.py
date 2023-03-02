import time
import sys
import json
import paho.mqtt.client as mqtt
from queue import Queue


def on_connect(client, userdata, flags, return_code):
    if return_code == 0:
        client.connected_flag = True  # set flag
        print("Client connected")
    else:
        print("Bad connection Returned code=", return_code)
        client.bad_connection_flag = True

        while (
            not client.connected_flag and not client.bad_connection_flag
        ):  # wait in loop
            print("Reconnecting...")
            time.sleep(10)
        if client.bad_connection_flag:
            print("Bad connection. Exiting...")
            client.loop_stop()  # Stop loop
            sys.exit()


def on_message(client, userdata, message):
    client.messages.put(json.loads(message.payload.decode("utf-8")))
    # print(f"message= {json.loads(message.payload.decode('utf-8'))}")
    # print("topic=", message.topic)
    # print("qos=", message.qos)
    # print("retain flag=", message.retain)


def on_disconnect(client, userdata, rc):
    print("Disconnecting reason  " + str(rc))
    client.connected_flag = False
    client.disconnect_flag = True
    client.loop_stop()


class MQTTClient(mqtt.Client):
    def __init__(self, cname, **kwargs):
        super(MQTTClient, self).__init__(cname, **kwargs)
        self.messages = Queue()
        self.last_pub_time = time.time()
        self.topic_ack = []
        self.run_flag = False
        self.subscribe_flag = False
        self.bad_connection_flag = False
        self.connected_flag = False
        self.disconnect_flag = False
        self.disconnect_time = 0.0
        self.pub_msg_count = 0
        self.devices = []

    def get_queue(self):
        return self.messages

    def __repr__(self):
        return f"MQTTClient({self._client_id.decode('utf-8')})"
