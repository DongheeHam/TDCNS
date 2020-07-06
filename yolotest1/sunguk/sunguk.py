import numpy as np
import argparse
import cv2 as cv
import subprocess
import time
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from utils import parse
from configure import getSizecut, getArea
from detector import Detector
from data_processing import DataProcessing

def repeat():
    count =[[0,0],[0,0],[0,0]]
    lane_count = [[1, 0] for _ in count]
    print(lane_count)
    for i, test in enumerate(lane_count):
        print(i,test)

repeat()
