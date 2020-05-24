import requests
import json
import pyrebase
from datetime import datetime
from kivy.app import App

class Firebase():
    def __init__(self):

        config = {
        "apiKey": "AIzaSyD8izkrqW466gor_Hm5uRNWUxCIyXzlky4",
        "authDomain": "investmentsummary-94034.firebaseapp.com",
        "databaseURL": "https://investmentsummary-94034.firebaseio.com/",
        "storageBucket": "investmentsummary-94034.appspot.com" }

        firebase = pyrebase.initialize_app(config)
        self.db = firebase.database()
        self.auth = firebase.auth()        
        self.app = App.get_running_app()

    def sign_up(self,email, password):
        #send email and password to firebase
        #firebase will return localid authtoken and refreshtoken
        email = email.replace("\n","")
        password = password.replace("\n","")        

        try:
            sign_up_data = self.auth.create_user_with_email_and_password(email, password)
            refresh_token = sign_up_data['refreshToken']
            localId = sign_up_data['localId']
            idToken = sign_up_data['idToken']
            email = sign_up_data['email']

            with open(self.app.refresh_token_file, 'w') as f:
                f.write(refresh_token)

            #save localid to a variable 
            self.app.local_id = localId
            self.app.id_token = idToken
            self.app.email_address = email            

            my_data = {"buy":"","sell":"","history":""}
            self.db.child(localId).set(my_data,idToken)      
            self.app.change_screen('input_screen')
        
        except requests.HTTPError as e:
            error_json = e.args[1]
            error_message  = json.loads(error_json)["error"]['message']
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
        try:
            sign_up_data = self.auth.sign_in_with_email_and_password(email, password)
            refresh_token = sign_up_data['refreshToken']
            localId = sign_up_data['localId']
            idToken = sign_up_data['idToken']
            email = sign_up_data['email']
            # Save refreshToken to a file
            with open(self.app.refresh_token_file, "w") as f:
                f.write(refresh_token)
            # Save localId to a variable in main app class
            # Save idToken to a variable in main app class
            self.app.local_id = localId
            self.app.id_token = idToken
            self.app.email_address = email
            # Create new key in database from localId
            self.app.on_start()

        except requests.HTTPError as e:
            error_json = e.args[1]
            error_message  = json.loads(error_json)["error"]['message']
            self.app.root.ids['login_screen'].ids['login_message'].text ="EMAIL EXISTS - " + error_message.replace("_", " ")    

    def exchange_refresh_token(self, refresh_token):
        refresh_req = self.auth.refresh(refresh_token)
        local_id = refresh_req['userId']
        idToken = refresh_req['idToken']

        return idToken, local_id

    def reset_password(self, email):
        self.auth.send_password_reset_email(email) 
        self.app.root.ids['account_screen'].ids['reset_message'].text = "Password Reset sent to: {}".format(email)

    def add_to_history(self,direction, price, qty, ticker, identifier, method):

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        history_data = { "timestamp": now,
                        "price": price,
                        "qty": qty,
                        "ticker": ticker,
                        "method": method,
                        "direction": direction,
                        "id": identifier
        }

        self.db.child(self.app.local_id).child('history').push(history_data,self.app.id_token)


    def add_detail(self, direction,price,qty,ticker):

        a=self.db.child(self.app.local_id).child(ticker).get(self.app.id_token)
        if a.val() == None:
            my_data = { "price": price,
                        "qty": qty,
                        "direction": direction,
                        "id": 1
            }                  
            self.db.child(self.app.local_id).child(ticker).set({"nextId": 2},self.app.id_token)
            self.db.child(self.app.local_id).child(ticker).push(my_data,self.app.id_token)
            identifier = 1
            self.add_to_history(direction,price,qty,ticker,identifier,method="insert")
        else:
            currId = self.db.child(self.app.local_id).child(ticker).get(self.app.id_token).val()["nextId"]
            nextId = currId + 1 
            self.db.child(self.app.local_id).child(ticker).update({"nextId": nextId},self.app.id_token)
            my_data = { "price": price,
            "qty": qty,
            "direction": direction,
            "id": currId
                }               
            self.db.child(self.app.local_id).child(ticker).push(my_data,self.app.id_token)
            self.add_to_history(direction,price,qty,ticker,currId,method="insert")       

    def getData(self):
        return self.db.child(self.app.local_id).get(self.app.id_token).val()

    def getTickerData(self,ticker):
        return self.db.child(self.app.local_id).child(ticker).get(self.app.id_token).val()

    def getHistoryData(self):
        return self.db.child(self.app.local_id).child('history').get(self.app.id_token).val()

    def removeData(self,ticker,generatedId):
        a = self.db.child(self.app.local_id).child(ticker).child(generatedId).get(self.app.id_token).val()
        self.add_to_history(a['direction'],a['price'],a['qty'],ticker,a['id'],method="delete")

        b = self.db.child(self.app.local_id).child(ticker).get(self.app.id_token).val()
        if len(b) == 2:
            return self.db.child(self.app.local_id).child(ticker).remove(self.app.id_token) 
        else:
            return self.db.child(self.app.local_id).child(ticker).child(generatedId).remove(self.app.id_token)

    
    def modifyData(self,ticker,generatedId, direction,price,qty,identifier):
        my_data = { "price": price,
        "qty": qty,
        "direction": direction
            }       
        self.db.child(self.app.local_id).child(ticker).child(generatedId).update(my_data, self.app.id_token)
        self.add_to_history(direction,price,qty,ticker, identifier, "modify")