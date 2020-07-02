# TDCNS
# 1. dtc, ldtc, counter 정보 등록하기
  1 define_area.py 실행
  2 road_number, 영상정보는 필수로 입력해줘야함
    * road_number int이며 임시로 정해놨음 현재까지 정의된 road_number은 1,2,3,68임 
      - 1=Sample1,2,3.avi영상, 2,3번은 내가 촬영한 영상임. 2=승현이네 집 육교 3=오른쪽 상단에 외각순환고속도로 보이는 영상 
        68은 목동오거리 cctv임 cctv스트림 url은 진행사항ppt에 있고 road_numer은 url상 맨 마지막 숫자에서 따왔음
      - road_number를 -r 뒤에 입력하면 됨.
    * 영상정보는 두가지임
      - 스트리밍 (cctv) : -st 뒤에 url입력하면 됨
      - 동영상 : -r 뒤에 영상의 상대경로를 입력하면 됨.
    * ex) python define_area.py -r 68 -st rtmp://210.179.218.51/live/68.stream

# 2. 인식 모듈 실행
  * tdc_main.py 실행
  * road_number, 영상정보를 필수로 입력해야함 : 입력방법윈 위와 같음.
  * 건너뛸 프레임 수를 입력해주면 좋음 : -ic 뒤에 숫자를 넣어주면 해당 숫자만큼의 프레임마다 객체인식 연산을 함 (ex: -ic 10 하면 10프레임에 한번씩만 객체인식을 하기 때문에 속도가 잘 나옴)
 
## 3. admin server은 cloud에 올려놨음
* console.cloud.google.com -> computing engine -> vm인스턴스 -> ssh를 누르면 클라우드 가상머신으로 접속됨 접속된 리눅스 pc에서 tomcat 서버가 돌아가고 있음
* mysql이 설치되어 있으니 우리가 아는 방법으로 mysql들어가서 테이블 정보 확인 가능
