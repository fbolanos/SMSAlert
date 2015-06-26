''' @author Federico Bolanos
    @date   June 26 2015
    @Description A simple script that checks the RFID line and if stays continously
        high for more than 5 minutes it sends a text message to the numbers in the list.
        The text message alerts you of the possibility of a stuck mouse.
'''
import json
import requests
import RPi.GPIO as GPIO
import time
from datetime import datetime

### CONSTANTS ###
HOSTNAME = "hostname"


#url of the free service! Limit to 75 texts per day.
URL = 'http://textbelt.com/canada' 

#List of Numbers to send the text to.
NUMBERS = ['7780000000', # LM1
           '7781234567'] # LM2

#The data that will be POSTed to the url.
DATA_LIST = [ { 'number': number,
              'message': ('\n\nA mouse has been inside the chamber continously for more than 5 minutes.\n' \
                          'Cage: ' + HOSTNAME + '\nDate: ') }
        for number in NUMBERS]

#GPIO line of the RFID tag in range pin.
G_RANGE_PIN = 24

#Small time(s) to sleep to avoid CPU overload
T_CPU_REST = 0.01

#Time in minutes required to assume mouse is stuck.
T_MOUSE_STUCK = 10

### FUNCTIONS ###

def setup_GPIO():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(G_RANGE_PIN, GPIO.IN)
    

def send_sms(date):
    request_list = []
    for data in DATA_LIST:
        data['message'] += date
        request_list.append(requests.post(URL, data=data))

    for req in request_list:
        print req.text
                            
    
def run_loop():
    print 'Main loop running!'
    is_range_pin_high = False
    
    while (True):
        if GPIO.input(G_RANGE_PIN):
            is_range_pin_high = True
            print 'Range pin is high...'
        else:
            time.sleep(T_CPU_REST)
            
        if is_range_pin_high:
            time_clock_start = time.time()
            while (time.time()-time_clock_start < T_MOUSE_STUCK):
                if (not GPIO.input(G_RANGE_PIN)):
                    is_range_pin_high = False
                    print 'Range pin became low...'
                    break
                else:
                    time.sleep(T_CPU_REST)
            ### end of while
            if is_range_pin_high: ### Mouse seems stuck, send SMS
                date = str(datetime.now())
                print 'Sending SMS Alert on ' + date
                send_sms(date)
                print 'Done Sending!'
                return
            else:
                print 'Mouse left with no problem!'


def main():
    print 'Initiating SMS Alert...',
    setup_GPIO(),
    print '[DONE]'
    
    run_loop()







if __name__ == '__main__':
    main()
