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
            [455, 455]
        ]
    ]
}
URL = 'http://localhost:8080/rest/setLdtc.json'
response = requests.post(URL, data=example)
print("status : ",response.status_code)
print("text : ",response.text)