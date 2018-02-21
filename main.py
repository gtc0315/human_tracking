# this is a test
import numpy as np
from pir_lib import pir, cam
import paho.mqtt.client as mqtt
import time
from datetime import datetime, timedelta
import pandas
import json
from Bluetooth import bluetooth_rssi


def collect_samples(pir,cam,addr,cycle, sampling_rate):
    print("collecting data...")
    start_time = datetime.now()
    timestamp = str(start_time)
    pir_values = []

    filenames = []
    index = 0
    for _ in range(cycle):
        pir_values.extend(pir.read_pir())
        if cam!=None:
            cam.take_picture(str(index) + ".jpg")
            filenames.append(str(index) + ".jpg")
            index += 1

        time.sleep(sampling_rate)

    if cam!=None:
        print("make gif")
        cam.make_gif(filenames, timestamp + ".gif")
    
    fh = open("pir.txt","a")
    fh.write(timestamp+"|"+",".join(map(str,pir_values))+"\n")
    fh.close()
    rssi = bluetooth_rssi(addr)
    return {"values": pir_values, "rssi":rssi, "timestamp": timestamp}


if __name__ == "__main__":
    pir = pir([23, 24, 25, 27, 22])
    blt_addr = '9C:F3:87:42:5C:32'
    # cam = cam()
    cam = None
    cycle = 2
    sampling_rate = 0.1
    refresh_rate = 0.5

    name = "raspberry_pi"
    topic = "tAxiY7W4P58QH5Oq/living_room/pir"
    broker_address = "iot.eclipse.org"
    client = mqtt.Client(name)
    client.connect(broker_address, 1883, 60)

    while True:
        if not np.all(pir.read_pir() == [0, 0, 0, 0, 0]):
            ans = collect_samples(pir,cam,blt_addr,cycle,sampling_rate)
            payload = json.dumps(ans)
            client.publish(topic, payload, qos=0, retain=False)
            print("publishing " + payload)
        else:
            time.sleep(refresh_rate)


