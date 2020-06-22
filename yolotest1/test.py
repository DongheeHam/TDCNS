import requests, json

example={
    "rno":1,
    "dtc":[
        [111, 111],
        [222, 222],
        [333, 333],
        [444, 444]
    ],
    "ldtc":[
        [
            [123, 123],
            [234, 234],
            [345, 345],
            [456, 456]
        ],[
            [121, 121],
            [232, 232],
            [343, 343],
            [454, 454]
        ],[
            [131, 131],
            [242, 242],
            [353, 353],
            [464, 464]
        ],[
            [122, 122],
            [233, 233],
            [344, 344],
            [4455, 4455]
        ]
    ]
}
headers = {'Content-Type': 'application/json; charset=utf-8'}
example2 = {"a":"aaaa","b":"bbbb"}
URL = 'http://localhost:8080/rest/setDtc.json'
response = requests.post(URL, headers=headers, data=json.dumps(example))
print("status : ",response.status_code)
print("text : ",response.text)