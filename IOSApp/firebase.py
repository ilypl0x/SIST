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
        email = email.replace("\n","")
        password = password.replace("\n","")        
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
            with open(self.app.refresh_token_file, 'w') as f:
                f.write(refresh_token)

            #save localid to a variable 
            self.app.local_id = localId
            self.app.id_token = idToken

            # my_data = { "buy": {"ticker":"","price":"","qty":""},"sell": {"ticker":"","price":"","qty":""},"total": {"percent": "", "pnl": ""} }
            my_data = {"buy":"","sell":"","qty":""}

            post_request = requests.patch("https://investmentsummary-94034.firebaseio.com/"+ localId + ".json?auth=" + idToken,
                            data = json.dumps(my_data))

            self.app.change_screen('home_screen')

        if sign_up_request.ok == False:
            error_data = json.loads(sign_up_request.content.decode())
            error_message  = error_data["error"]['message']
            if error_message == "EMAIL_EXISTS":
                self.sign_in_existing_user(email,password)
            else:
                self.app.root.ids['login_screen'].ids['login_message'].text = error_message.replace("_", "")
        pass

    def on_error(self, req, result):
        print("Failed to get user data")
        print(result)

    def sign_in_existing_user(self, email, password):
        """Called if a user tried to sign up and their email already existed."""
        signin_url = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key=" + self.wak
        signin_payload = {"email": email, "password": password, "returnSecureToken": True}
        signin_request = requests.post(signin_url, data=signin_payload)
        sign_up_data = json.loads(signin_request.content.decode())
        self.app = App.get_running_app()

        if signin_request.ok == True:
            refresh_token = sign_up_data['refreshToken']
            localId = sign_up_data['localId']
            idToken = sign_up_data['idToken']
            # Save refreshToken to a file
            with open(self.app.refresh_token_file, "w") as f:
                f.write(refresh_token)

            # Save localId to a variable in main app class
            # Save idToken to a variable in main app class
            self.app.local_id = localId
            self.app.id_token = idToken

            # Create new key in database from localId
            #self.friend_get_req = UrlRequest("https://friendly-fitness.firebaseio.com/next_friend_id.json?auth=" + idToken, on_success=self.on_friend_get_req_ok)
            self.app.on_start()

        elif signin_request.ok == False:
            error_data = json.loads(signin_request.content.decode())
            error_message = error_data["error"]['message']
            self.app.root.ids['login_screen'].ids['login_message'].text = "EMAIL EXISTS - " + error_message.replace("_", " ")        

    def exchange_refresh_token(self, refresh_token):
        refresh_url = 'https://securetoken.googleapis.com/v1/token?key=' + self.wak
        refresh_payload = '{"grant_type": "refresh_token", "refresh_token": "%s"}' % refresh_token
        refresh_req = requests.post(refresh_url, data = refresh_payload)

        local_id = refresh_req.json()['user_id']
        id_token = refresh_req.json()['id_token']

        return id_token, local_id