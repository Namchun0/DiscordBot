from pathlib import Path
import requests
import json
import ast

URL_TOKEN        = 'https://id.twitch.tv/oauth2/token'
URL_VALIDATE     = 'https://id.twitch.tv/oauth2/validate'
URL_CHECK_ISLIVE = 'https://api.twitch.tv/helix/search/channels?query='

CLIENT_ID     = 'your client id'
CLIENT_SECRET = 'your client secret'

JSON_PATH  = './streamers.json'
TOKEN_PATH = './twitch_token.txt'

SUCCESS_STATUS = 200
TOKEN_EXPIRATION = 1000000

fileWrite = lambda file, text: Path(file).write_text(text)
fileRead = lambda file: Path(file).read_text()
jsonLoad = lambda path: json.loads(fileRead(path))



class TwitchApi:
    def __init__(self):
        STREAMERS_JSON = jsonLoad(JSON_PATH)
        self.STREAMERS_ID = STREAMERS_JSON['streamer_id']
        self.STREAMERS_STATUS = STREAMERS_JSON['streamer_status']
        
        self.TOKEN = fileRead(TOKEN_PATH).strip()

        self.HEADERS = {
            'Authorization' : f'Bearer {self.TOKEN}',
            'Client-Id' : CLIENT_ID
        }
        self.PARAMS = {
            'client_id' : CLIENT_ID,
            'client_secret' : CLIENT_SECRET,
            'grant_type' : 'client_credentials'
        }



    # 토큰 재발행
    def resetToken(self):
        res = requests.post(URL_TOKEN, params=self.PARAMS)
        if res.status_code == SUCCESS_STATUS:
            res_json = res.json()
            self.TOKEN = res_json['access_token']
            fileWrite(TOKEN_PATH, self.TOKEN)
    


    # live 여부 확인 및 상태 저장
    def checkIsLive(self):
        try:
            for streamer in self.STREAMERS_ID:
                res = requests.get(URL_CHECK_ISLIVE + streamer, headers=self.HEADERS)
                if res.status_code == SUCCESS_STATUS:
                    res_json = res.json()
                    info_streamers = res_json['data']

                    for info_streamer in info_streamers:
                        if info_streamer['broadcaster_login'] == streamer:
                            is_live = info_streamer['is_live']
                            
                            self.STREAMERS_STATUS[streamer] = is_live
                            break
        except:
            self.validateToken()
        


    # live 상태가 바뀌었는지 확인
    # 방송이 켜진 스트리머와 방송이 꺼진 스트리머의 리스트를 반환
    def checkChanged(self):
        self.old_status = jsonLoad(JSON_PATH)['streamer_status']

        self.live_streamer, self.off_streamer  = [], []

        for streamer, new_status in self.STREAMERS_STATUS.items():
            if new_status != self.old_status[streamer]:
                if new_status:
                    self.live_streamer.append(self.STREAMERS_ID[streamer])
                else:
                    self.off_streamer.append(self.STREAMERS_ID[streamer])
        
        if not self.live_streamer:
            self.live_streamer = False
        if not self.off_streamer:
            self.off_streamer  = False
    


    # json 파일에 업데이트된 상태 저장
    def updateStatus(self):
        origin_str = jsonLoad(JSON_PATH)
        origin_str = str(origin_str)
        update_str = origin_str.replace(str(self.old_status), str(self.STREAMERS_STATUS))
        update_dict = ast.literal_eval(update_str)

        with open(JSON_PATH, 'w', encoding="utf-8") as f:
            json.dump(update_dict, f, indent='\t')
        


    # 토큰 만료시간 검사
    def validateToken(self):
        res = requests.get(URL_VALIDATE, headers={'Authorization' : f'Bearer {self.TOKEN}'})
        if res.status_code == SUCCESS_STATUS:
            res_json = res.json()

            if res_json['expires_in'] < TOKEN_EXPIRATION:
                self.resetToken()



    def run(self):
        self.checkIsLive()
        self.checkChanged()
        self.updateStatus()

        return self.live_streamer, self.off_streamer
