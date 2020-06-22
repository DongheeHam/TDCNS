import numpy as np
import requests
import json

def getArea(road_number):
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    url = 'http://localhost:8080/rest/getArea.json'
    param = {"rno": road_number}
    response = requests.post(url, params=param, headers=headers)
    result = json.loads(response.text)["result"]
    #print(result)

    dtc = np.array(result["dtc"])
    result_ldtc = result["ldtc"]
    ldtc=[]
    for l in result_ldtc:
        ldtc.append(np.array(l))
    return (dtc, ldtc)

"""
get Detection Area
- 해당 진입로(road_number)에서 차량을 인식할 부분

Todo : config server 구축 완료시 http 통신으로 받아올 것.
"""
def getDtcArea(road_number):
    # (임시) 전농
    if road_number==0:
        return np.array([[450, 720], [450, 170], [650, 180], [900, 720]], np.int32)
    # (임시) Sample1,2,3 진입로
    elif road_number==1:
        return np.array([[90, 350], [140, 160], [360, 35], [520, 35], [700, 160], [912, 350]], np.int32)
    else :
        return np.array([])

"""
get Lane Detection Area
- 해당 진입로(road_number)에서 각 차선별 인식할 부분
return : 각 차선의 인식할 부분(np.array())의 list형 데이터 

Todo : config server 구축 완료시 http 통신으로 받아올 것.
"""
def getLdtcsArea(road_number):
    # (임시) Sample1,2,3 진입로
    if road_number==1:
        result=[]
        result.append(np.array( [[783, 253], [680, 163], [612, 155], [683, 255]] ))
        result.append(np.array([[581, 255], [531, 106], [558, 113], [615, 161], [682, 257]]))
        result.append(np.array([[476, 257], [483, 54], [507, 54], [582, 257]]))
        result.append(np.array([[371, 258], [454, 62], [483, 62], [478, 253]]))
        result.append(np.array( [[268, 262], [428, 60], [456, 62], [446, 86], [373, 253]] ))
        result.append(np.array( [[167, 264], [391, 58], [426, 62], [270, 257]] ))
        result.append(np.array( [[66, 293], [16, 284], [18, 244], [211, 141], [257, 137], [330, 67], [378, 67], [281, 163], [158, 225], [69, 291]] ))
        return result
    elif road_number==2:
        result=[]

    else:
        return [np.array([])]