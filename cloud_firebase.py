import os
import requests
import pyrebase
from io import BytesIO
from dotenv import load_dotenv
load_dotenv()


api_key = os.environ.get("API_KEY")
authDomain = os.environ.get("AUTH_DOMAIN")
projectId = os.environ.get("PROJECT_ID")
storageBucket = os.environ.get("STORAGE_BUCKET")
messaginSenderId = os.environ.get("MESSAGING_SEND_ID")
appId = os.environ.get("APP_ID")
measurementId = os.environ.get("MEASUREMENT_ID")


config = {
  "apiKey": api_key ,
  "authDomain": authDomain ,
  "projectId": projectId,
  "storageBucket": storageBucket,
  "messagingSenderId": messaginSenderId,
  "appId": appId,
  "measurementId": measurementId
}
firebase = pyrebase.initialize_app(config)
storage = firebase.storage()


def Send_QR(name_img, ruta):
    storage.child(f"qr/{name_img}").put(ruta)

def Link_Img(name_img):
 url = storage.child(f"qr/{name_img}").get_url(None)
 return url

#Es este
def Link_Download(img, url):
  response = requests.get(url)
  #with open(f"{img}", "wb") as f:
   # a = f.write(response.content)
  #print(type(response.content))
  #return a
  img = BytesIO()
  img.write(response.content)
  img.seek(0)
  return img




def Download(img):
  ruta = "gs://project-qrimg.appspot.com/qr/ESTUD0001"
  url = storage.child(ruta).get_url(token=None)
  print(url)
  return url

def Delete_Img(): 
    storage.delete(f"qr/new.png",None)