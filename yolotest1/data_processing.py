import time
import threading
import csv
from datetime import datetime

class DataProcessing:
    def __init__(self, detector, road_number):
        self.detector = detector
        self.road_number = road_number
        self.counting_flag=True

    # def run_counting(self):
    #     print(f"run_counting!{datetime.today().hour}:{datetime.today().minute}:{datetime.today().second}")
    #     csvfile=open(f"data_storage/({self.road_number}){datetime.today().strftime('%Y_%m_%d')}.csv",'a',newline="")
    #     writer=csv.writer(csvfile)
    #     hour=datetime.today().hour
    #     minute=datetime.today().minute-(datetime.today().minute%5) # 매 5분단위로 내림. ex(8->5, 24->20)
    #
    #     for lane, count in enumerate(self.detector.lane_count):
    #         #print([self.road_number, "%02d%02d" % (hour,minute), lane+1, count[0], count[1]])
    #         writer.writerow([self.road_number, "%02d%02d" % (hour,minute), lane+1, count[0], count[1]])
    #
    #     self.detector.lane_count=[[0,0] for _ in self.detector.counter]
    #     if self.counting_flag:
    #         threading.Timer(60 * 5, self.run_counting).start()

    def run_counting(self):
        a=1

    def stop_counting(self):
        self.counting_flag=False

    def start_counting(self):
        self.counting_flag = True
        self.run_counting()

    def dataProcess(self, unprocessed_data):
        # Todo some logic
        return None
