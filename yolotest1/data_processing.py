import time
import threading
import csv
from datetime import datetime
import requests

import json

class DataProcessing:
    def __init__(self, detector, road_number):
        self.detector = detector
        self.road_number = road_number
        self.counting_flag = True

    def run_counting(self):
        print(f"run_counting!{datetime.today().hour}:{datetime.today().minute}:{datetime.today().second}")
        csvfile=open(f"data_storage/({self.road_number}){datetime.today().strftime('%Y_%m_%d')}.csv",'a',newline="")
        writer=csv.writer(csvfile)
        hour=datetime.today().hour
        minute=datetime.today().minute-(datetime.today().minute%5) # 매 5분단위로 내림. ex(8->5, 24->20)
        headers = {'Content-Type': 'application/json; charset=utf-8'}
        #url = 'http://35.224.46.11:80/rest/setDtc.json'
        url = 'http://35.224.46.11:80/dc/addDataRow.json'
        data = {"rno": self.road_number, "time": "%02d%02d" % (hour,minute)}
        lanes=[]
        for lane, count in enumerate(self.detector.lane_count):
            #print([self.road_number, "%02d%02d" % (hour,minute), lane+1, count[0], count[1]])
            #writer.writerow([self.road_number, "%02d%02d" % (hour,minute), lane+1, count[0], count[1]])
            lanes.append({"large":count[0],"small":count[1]})
        data["lane"]=lanes
        response = requests.post(url, headers=headers, data=json.dumps(data))
        self.detector.lane_count=[[0,0] for _ in self.detector.counter]
        if self.counting_flag:
            threading.Timer(60 * 5, self.run_counting).start()

    # def run_counting(self):
    #     a=1

    def stop_counting(self):
        self.counting_flag=False

    def start_counting(self):
        self.counting_flag = True
        self.run_counting()

    def dataProcess(self, unprocessed_data):
        # Todo some logic
        return None
