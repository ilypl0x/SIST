import requests
import json
from kivy.app import App

class Firebase():
    def __init__(self):
        self.wak = "AIzaSyD8izkrqW466gor_Hm5uRNWUxCIyXzlky4" #Web api key
        self.app = App.get_running_app()

    def sign_up(self,email, password):
        #send email and password to firebase
        #firebase will return localid authtoken and refreshtoken
        signup_url = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/signupNewUser?key=" + self.wak
        signup_data = {"email": email, "password": password, "returnSecureToken": True}
        sign_up_request = requests.post(signup_url, data = signup_data)
        sign_up_data = json.loads(sign_up_request.content.decode())

        if sign_up_request.ok == True:
            refresh_token = sign_up_data['refreshToken']
            localId = sign_up_data['localId']
            idToken = sign_up_data['idToken']
            #create new key in database from localId
            #save refresh token to a file
            with open("refresh_token.txt", 'w') as f:
                f.write(refresh_token)

            #save localid to a variable 
            self.app.local_id = localId
            self.app.id_token = idToken

            # my_data = { "buy": {"ticker":"","price":"","qty":""},"sell": {"ticker":"","price":"","qty":""},"total": {"percent": "", "pnl": ""} }
            my_data = {"buy":"","sell":"","qty":""}

            post_request = requests.patch("https://investmentsummary-94034.firebaseio.com/"+ localId + ".json?auth=" + idToken,
                            data = json.dumps(my_data))
            print(post_request.ok)
            print(json.loads(post_request.content.decode()))

            self.app.change_screen('home_screen')

        if sign_up_request.ok == False:
            error_data = json.loads(sign_up_request.content.decode())
            error_message  = error_data["error"]['message']
            App.get_running_app().root.ids['login_screen'].ids['login_message'].text = error_message
        pass


    def exchange_refresh_token(self, refresh_token):
        refresh_url = 'https://securetoken.googleapis.com/v1/token?key=' + self.wak
        refresh_payload = '{"grant_type": "refresh_token", "refresh_token": "%s"}' % refresh_token
        refresh_req = requests.post(refresh_url, data = refresh_payload)

        local_id = refresh_req.json()['user_id']
        id_token = refresh_req.json()['id_token']

        return id_token, local_id