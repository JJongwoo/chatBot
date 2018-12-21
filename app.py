# -*- coding: utf-8 -*-
import json
import os
import re
import urllib.request
import random

from bs4 import BeautifulSoup
from slackclient import SlackClient
from flask import Flask, request, make_response, render_template
from datetime import datetime

app = Flask(__name__)

slack_token = "xoxb-506472500310-507316627348-Y9jUQUb7lBdUDPJQLiH8IN9h"
slack_client_id = "506472500310.508537563479"
slack_client_secret = "a7d3abb97c990be52be4235ccf392600"
slack_verification = "EGUMTML2dLHvBbxgR2qbuxzm"
sc = SlackClient(slack_token)

mv  = [{"sub" : "마약왕", "gen" : "범죄"}, {"sub" : "보헤미안랩소디" ,"gen" : "드라마"},{"sub" : "명량" ,"gen" : "액션"},\
       {"sub" : "명탐정코난","gen" : "애니메이션" },{"sub" : "도어락","gen" : "스릴러" }, {"sub": "신비한동물사전", "gen": "판타지"},\
       {"sub": "곤지암", "gen":"공포"}, {"sub":"킹콩", "gen":"모험"}, {"sub":"내부자들", "gen":"느와르"},\
       {"sub":"완벽한타인", "gen":"코미디"},{"sub":"실미도", "gen":"전쟁"}, {"sub":"아바타", "gen":"SF"},\
       {"sub": "신과함께", "gen":"판타지"},{"sub": "신과함께-인과연", "gen":"판타지"},{"sub": "신과함께-죄와벌", "gen":"판타지"},\
       {"sub":"암수살인", "gen":"범죄"}, {"sub":"안시성", "gen":"액션"}, {"sub":"창궐", "gen":"액션"}, {"sub":"퍼스트맨", "gen":"SF"}]

gn = {"범죄" : '16',"드라마" : '1', "액션" : '19', "애니메이션" : '15', "스릴러" : '7', "판타지":'2',\
      "공포":'4', "모험":'6', "느와르":'8', "코미디":'11',"전쟁":'14', "SF":'18' }

genre=""
# 크롤링 함수 구현하기
def _crawl_naver_keywords(text):
    # 여기에 함수를 구현해봅시다.....
    sorting_value = ""
    type = 0
    if '스릴러' in text:
        url = "https://movie.naver.com/movie/sdb/rank/rmovie.nhn?sel=cnt&date=20181219&tg=7"
        genre='스릴러'
        type=1
    elif '뮤지컬' in text:
        url = "https://movie.naver.com/movie/sdb/rank/rmovie.nhn?sel=cnt&date=20181219&tg=17"
        genre='뮤지컬'
        type=1
    elif '액션' in text:
        url = "https://movie.naver.com/movie/sdb/rank/rmovie.nhn?sel=cnt&date=20181219&tg=19"
        genre='액션'
        type=1
    elif '드라마' in text:
        url = "https://movie.naver.com/movie/sdb/rank/rmovie.nhn?sel=cnt&date=20181219&tg=1"
        genre='드라마'
        type=1
    elif '박스오피스' in text:
        url = "https://movie.naver.com/movie/sdb/rank/rboxoffice.nhn"
        type=4
    elif '예매' in text:
        url = "https://movie.naver.com/movie/running/current.nhn?view=list&tab=normal&order=reserve"
        sorting_value = "예매"
        type=2
    elif '평점' in text:
        url = "https://movie.naver.com/movie/running/current.nhn?view=list&tab=normal&order=point"
        sorting_value = "평점"
        type=2
    elif "오늘 개봉" in text:
        url= str("https://movie.naver.com/movie/sdb/browsing/bmovie.nhn?open="+datetime.today().strftime("%Y%m%d"))
        type=3
    elif '개봉순' in text:
        url = "https://movie.naver.com/movie/running/current.nhn?view=list&tab=normal&order=open"
        sorting_value = "개봉"
        type=2
    elif '안녕' in text:
        return u"안녕하세요. 어떤 영화를 알려드릴까요?"
    elif '뭐하' in text or '뭐해' in text:
        return u"영화보는 중이니 방해하지 마세요."
    elif 'help' in text or '헬프' in text:
        return u"=========저는 이런 기능이 있어요=========\n1. 장르별 영화 순위(ex.액션영화 순위 알려줘) \n2. 현재 상영중 영화 정보(ex. 상영중 영화 예매순으로 찾아줘) \n3. 이번주 박스오피스 순위(ex. 박스오피스 알려줘) \n4. 올해의 TOP10(ex. 올해 top10 알려줘)\n5. 유사영화 검색기능(ex. 마약왕 비슷한 영화 찾아줘)"
    elif 'top10' in text:
        url = "https://www.youtube.com/watch?v=zGcVuhe1GXM"
        print("다음 link를 누르시면 올해의 영화 top10을 보실수 있어요!")
        return url
    elif '비슷한' in text:
        type = 5
        gen1 = ""
        title = text.split()[1]
        for j in mv:
            if j["sub"] == title:
                gen1 = j["gen"]
                break
        if gen1=="":
            return "제가 모르는 영화에요. / 제목에는 공백과 오타가 없어야 해요."
        url = "https://movie.naver.com/movie/sdb/rank/rmovie.nhn?sel=pnt&date=20181219&tg=" + gn[gen1]
    else:
        return u"무슨 말인지 모르겠어요\n 'help'나 '헬프' 명령어를 통해 기능을 확인할 수 있어요."

    req = urllib.request.Request(url)
    sourcecode = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(sourcecode, "html.parser")

    lists = []
    i = 1
    if type==1:
        lists.append("============"+genre+" 장르의 영화 랭킹이에요.============")
        for data in soup.find("table", class_="list_ranking").find("tbody").find_all("tr")[1:]:
            if not data.find("a") in lists:
                if len(lists) >= 11:
                    break
            aa = str(i) + '위 : ' + data.find("div", class_="tit3").find("a").get_text()
            lists.append(aa)
            i = i + 1
    elif type==2:
        lists.append("========="+sorting_value+"순으로 정리한 상영중 영화에요.========")
        for data in soup.find("div", class_="lst_wrap").find_all("li"):
           if not data.find("dl").find("dt").find("a").get_text() in lists:
               if len(lists) >= 11:
                   break
           aa = str(i) + '위 : ' + data.find("dl").find("dt").find("a").get_text() + " / " + data.find("span",
                                                                                        class_="num").get_text()
           lists.append(aa)
           i = i + 1
    elif type==3:
        lists.append("=================오늘 개봉한 영화에요.=================")
        for data in soup.find("div", class_="type_1").find("div").find("ul", class_="directory_list").find_all("li")[0::7]:
            if len(lists) >= 10:
                break
            aa = "제목 : " + data.find("a").get_text() + " / " + "장르 : " + data.find_all("li")[4].find("a").get_text()
            if len(aa)==1:
                return "오늘 개봉한 영화가 없습니다."
            lists.append(aa)
    elif type==4:
        lists.append("==============이번주 박스오피스 순위에요.==============")
        for data in soup.find("table", class_="list_ranking list_ranking2").find("tbody").find_all("tr")[1:]:
            if len(lists) >= 11:
                break
            aa = str(i)+"위 : " + data.get_text().split("\n")[4]  + " / 주말 관객 : " + data.get_text().split("\n")[9]+ " / 점유율 : " + data.get_text().split("\n")[14]
            i=i+1
            lists.append(aa)
    elif type==5:
        lists.append("==============" +title+"과 비슷한 영화에요.==============")
        ranlist=[]

        for data in soup.find_all("div", class_="tit5"):
            if data.find("a").get_text() not in lists:
                if len(ranlist) >= 11:
                    break
                aa = "제목 : "+data.find("a").get_text()
                ranlist.append(aa)

        out = random.sample(ranlist,5)

        for index in out:
            lists.append(index)

    #print(lists[-1])
    # 한글 지원을 위해 앞에 unicode u를 붙혀준다.
    return u'\n'.join(lists)





# 이벤트 핸들하는 함수
def _event_handler(event_type, slack_event):
    print(slack_event["event"])

    if event_type == "app_mention":
        channel = slack_event["event"]["channel"]
        text = slack_event["event"]["text"]

        keywords = _crawl_naver_keywords(text)
        sc.api_call(
            "chat.postMessage",
            channel=channel,
            text=keywords
        )

        return make_response("App mention message has been sent", 200, )

    # ============= Event Type Not Found! ============= #
    # If the event_type does not have a handler
    message = "You have not added an event handler for the %s" % event_type
    # Return a helpful error message
    return make_response(message, 200, {"X-Slack-No-Retry": 1})


@app.route("/listening", methods=["GET", "POST"])
def hears():
    slack_event = json.loads(request.data)
    print(slack_event)
    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200, {"content_type":
                                                                 "application/json"
                                                             })

    if slack_verification != slack_event.get("token"):
        message = "Invalid Slack verification token: %s" % (slack_event["token"])
        make_response(message, 403, {"X-Slack-No-Retry": 1})

    if "event" in slack_event:
        event_type = slack_event["event"]["type"]
        return _event_handler(event_type, slack_event)

    # If our bot hears things that are not events we've subscribed to,
    # send a quirky but helpful error response
    return make_response("[NO EVENT IN SLACK REQUEST] These are not the droids\
                         you're looking for.", 404, {"X-Slack-No-Retry": 1})


@app.route("/", methods=["GET"])
def index():
    return "<h1>Server is ready.</h1>"


if __name__ == '__main__':
    app.run('127.0.0.1', port=5000)
