''''
Real Time Face Recogition
	==> Each face stored on dataset/ dir, should have a unique numeric integer ID as 1, 2, 3, etc                       
	==> LBPH computed model (trained faces) should be on trainer/ dir
Based on original code by Anirban Kar: https://github.com/thecodacus/Face-Recognition    

Developed by Marcelo Rovai - MJRoBot.org @ 21Feb18  

'''

import cv2
import numpy as np
import os
from datetime import date
from datetime import datetime
import time
import random
import subprocess
#import RPi.GPIO as GPIO
import requests

recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read('trainer/trainer.yml')
cascadePath = "Cascades/haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascadePath);

font = cv2.FONT_HERSHEY_SIMPLEX

# Set up GPIO pins
#GPIO.setmode(GPIO.BCM)
#PIR_PIN = 17
#GPIO.setup(PIR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)



#iniciate id counter
id = 0
# Define a function to speak the text
def speak(text):
   subprocess.call(['espeak', '-ven', text])
   
#Function for whisper text
def whisperSpeak(text):
   subprocess.call(['espeak', '-s 80','-ven', '-a 35', text])
   
# names related to ids: example ==> Marcelo: id=1,  etc
names = ['None', 'Ole', 'Knut', 'Jabriil']


bool=True
while bool==True:
    #The user has to enter the time they want the rasberry to activate
    #Sets before everything else
    firsthour=int(input("Enter start hour (Between 1 and 24): "))
    lasthour=int(input("Enter stop hour(Between 1 and 24): "))
    
    #The time has to be between 1 and 24
    if firsthour>=1 and firsthour<=24 and lasthour>=1 and lasthour<=24:
        print("Certainly, the sensor will activate between",firsthour,"and",lasthour)
        bool=False
    else:
        print("The hour needs to be between 1 and 24")
         

#Get user id
userid = int(input("Enter the user ID: "))

#Get the date
#To put in the generated text and to check when the sensor is activated
#Date for check file
datecheck=date.today()
todayDate=str(datecheck)
yearmd=datecheck.strftime("%Y%m%d")

#Get todays name
daycheck=datetime.now()
dayName=daycheck.strftime("%A")

#Get the hour and minute right now
#To put in the generated text
timeNow=datetime.now()
timeNowHM=timeNow.strftime("%H:%M")

#Get the hour right now
#To check if the time is right
timeH=timeNow.strftime("%H")
timeH=int(timeH)

#Test for minutt
#Swap with date
timeM=timeNow.strftime("%M")
timeM=int(timeM)

#Generate list with greetings
greetList=[]
greetFile=open("greetings.txt",'r')
line=greetFile.readline().rstrip('\n')
while line!='':
    greetList.append(line)
    
    line=greetFile.readline().rstrip('\n')
    
greetFile.close()

#Generate funfacts 
funList=[]
funFile=open("funfacts.txt",'r')
line=funFile.readline().rstrip('\n')
while line!='':
    funList.append(line)
    
    line=funFile.readline().rstrip('\n')
    
funFile.close()

#Check the last time the function was triggered
checkList=[]
checkFile=open("checkfile.txt",'r')
line=checkFile.readline().rstrip('\n')
while line!='':
    checkList.append(line)
    
    line=checkFile.readline().rstrip('\n')
    
checkFile.close()

#Last time the function triggered
#lastTrigger="2023-04-16" og and lastTrigger!=todayDate i if setningen
#Get the last object in the list
lastTrigger=int(checkList[-1])

# Initialize and start realtime video capture
cam = cv2.VideoCapture(0)
cam.set(3, 640) # set video widht
cam.set(4, 480) # set video height

# Define min window size to be recognized as a face
minW = 0.1*cam.get(3)
minH = 0.1*cam.get(4)

#Array for checking the most recognised user in the cam
array = []

#Let the camera run
while True:
    #The AI does its thing
    ret, img =cam.read()
    img = cv2.flip(img, -1) # Flip vertically

    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

    faces = faceCascade.detectMultiScale( 
        gray,
        scaleFactor = 1.2,
        minNeighbors = 5,
        minSize = (int(minW), int(minH)),
       )

    for(x,y,w,h) in faces:

        cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)

        id, confidence = recognizer.predict(gray[y:y+h,x:x+w])
        
        # Check if confidence is less them 100 ==> "0" is perfect match 
        if (confidence < 100 ):
            #Check the id so we can add it in the array to be sure which person is recognised
            checker = id
            int(checker)
            id = names[id]
            confidence = "  {0}%".format(round(100 - confidence))
            
            array.append(checker)
        else:
            id = "unknown"
            confidence = "  {0}%".format(round(100 - confidence))
        
        cv2.putText(img, str(id), (x+5,y-5), font, 1, (255,255,255), 2)
        cv2.putText(img, str(confidence), (x+5,y+h-5), font, 1, (255,255,0), 1)
        
     #The array containing id's of who is spotted in cam   
    if len(array) >= 16:
        #Test
        print(array)
        #Gets the most added user id in the array, to be sure its the right person
        ofteste = max(set(array),key=array.count)
        print (ofteste)
        print (names[ofteste])
        
        # from if, was first condition: GPIO.input(PIR_PIN) and 
        #If every point checks out, the greeting can run       
        if  ofteste == userid and timeH>=firsthour and timeH<=lasthour and lastTrigger!=timeM:
            #Generated text
            randomGreet=random.randint(0,9)

            #Gets the amount of checkdates, to create index for the funfacts
            #First make a variable for each line in checkfile(sum of lines)
            factDay=sum(1 for line in open("checkfile.txt"))
            #Retrieves the fact of the day, based on the sum of checkdates
            factOfDay=funList[factDay]
            
            #Weather api from openweathermap.org
            api_key = '89237ec91daae2b690cf0fdc7ef8afb4' #Remove api key, use ur own api key
            city = 'Hønefoss'
            country_code = 'NO'
            api_url = f'https://api.openweathermap.org/data/2.5/weather?q={city},{country_code}&appid={api_key}&units=metric'

            response = requests.get(api_url)

            if randomGreet==9:
                #Number 9 is a whisper text
                greet=(greetList[randomGreet])
                greet = str(greet)
                os.system('echo "{0}" | festival --tts'.format(greet))

                texted="Today is",dayName,"and the time is currently",timeNowHM,"."
                texted = str(texted)
                os.system('echo "{0}" | festival --tts'.format(texted))
                print(texted)
                #If the api doesnt get an error, we get the weather
                if response.status_code == 200:
                    data = response.json() 
                    weather=data["weather"][0]["description"]
                    deegres=data["main"]["temp"]
                    report="If you look outside, its",weather,"and its",deegres,"°C"
                    report = str(report)
                    os.system('echo "{0}" | festival --tts'.format(report))
                    print(report)
                else:
                    print(f'Request failed with status code {response.status_code}')
                
                facts="Funfact of the day is:",factOfDay
                facts = str(facts)
                os.system('echo "{0}" | festival --tts'.format(facts))
                print(facts)
            else:
                #Normal voice 
                greet=(greetList[randomGreet])
                greet = str(greet)
                os.system('echo "{0}" | festival --tts'.format(greet))
                print(greet)
                
                texted="Today is",dayName,"and the time is currently",timeNowHM,"."
                texted = str(texted)
                os.system('echo "{0}" | festival --tts'.format(texted))
                print(texted)
                #If the api doesnt get an error, we get the weather
                if response.status_code == 200:
                    data = response.json() 
                    weather=data["weather"][0]["description"]
                    deegres=data["main"]["temp"]
                    report="If you look outside, its",weather,"and its",deegres,"°C"
                    report=str(report)
                    os.system('echo "{0}" | festival --tts'.format(report))
                    print(report)
                else:
                    print(f'Request failed with status code {response.status_code}')
                
                facts="Funfact of the day is:",factOfDay
                facts = str(facts)
                os.system('echo "{0}" | festival --tts'.format(facts))
                print(facts)

            
            #Set newtrigger to the checkfile
            newTrigger=str(timeM)
            newTrigger+='\n'
            checkfile=open("checkfile.txt","a")
            checkfile.write(newTrigger)
            checkfile.close()
            
            #Cleans up the array for a new reading
            array = []
            
        else:
            print("Detected something, but not valid for a greeting right now")
            array = []
            

        #Check the last time the function was triggered every time the loop runs
        checkList=[]
        checkFile=open("checkfile.txt",'r')
        line=checkFile.readline().rstrip('\n')
        while line!='':
            checkList.append(line)
            
            line=checkFile.readline().rstrip('\n')
            
        checkFile.close()

        #Gets the last trigger
        lastTrigger=int(checkList[-1])
        timeNow=datetime.now()
        timeM=timeNow.strftime("%M")
        timeM=int(timeM)   
        timeNowHM=timeNow.strftime("%H:%M")

        time.sleep(3)  # Pause for a short time between readings
            
        print("Looking for new recognition")
    
    cv2.imshow('camera',img) 

    k = cv2.waitKey(10) & 0xff # Press 'ESC' for exiting video
    if k == 27:
        break


# Do a bit of cleanup
print("\n [INFO] Exiting Program and cleanup stuff")
cam.release()
cv2.destroyAllWindows()