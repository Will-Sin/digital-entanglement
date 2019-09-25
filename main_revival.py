#Libraries
import RPi.GPIO as GPIO
import time
import mplayer
 
#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)

'''testing with sensors 1, 7, 6, 3'''

sensors = {
    1 : {'ECHO' : 3, 'TRIG' : 2, 's1' : 0, 's2' : 0, 's3' : 0, 's4' : 0},
    #2 : {'ECHO' : 14, 'TRIG' : 4, 's1' : 0, 's2' : 0, 's3' : 0, 's4' : 0},
    3 : {'ECHO' : 18, 'TRIG' : 15, 's1' : 0, 's2' : 0, 's3' : 0, 's4' : 0},
    #4 : {'ECHO' : 27, 'TRIG' : 17, 's1' : 0, 's2' : 0, 's3' : 0, 's4' : 0},
    #5 : {'ECHO' : 23, 'TRIG' : 22, 's1' : 0, 's2' : 0, 's3' : 0, 's4' : 0},
    6 : {'ECHO' : 10, 'TRIG' : 24, 's1' : 0, 's2' : 0, 's3' : 0, 's4' : 0},
    7 : {'ECHO' : 25, 'TRIG' : 9, 's1' : 0, 's2' : 0, 's3' : 0, 's4' : 0},
    #8 : {'ECHO' : 8, 'TRIG' : 11, 's1' : 0, 's2' : 0, 's3' : 0, 's4' : 0}
}

volumes = [0,0,0,0]
invertvolumes = [0,0,0,0]
players = ['p1', 'p2', 'p3', 'p4']
audio = ['../1.ogg','../2.ogg','../3.ogg','../4.ogg']
smallestDistancesSmoother = [1,1,1,1,1]

def distance(TRIG, ECHO):
    #print('distance')
    #set GPIO Pins
    GPIO_TRIGGER = TRIG
    GPIO_ECHO = ECHO
 
    #set GPIO direction (IN / OUT)
    GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
    GPIO.setup(GPIO_ECHO, GPIO.IN)

    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()
 
    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
 
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2

    if distance >= 400:
        distance = 400

    return distance

def Smoother(i, dist):
    #print('Smoother')
    sensors[i]['s1'] = sensors[i]['s2']
    sensors[i]['s2'] = sensors[i]['s3']
    sensors[i]['s3'] = sensors[i]['s4']
    sensors[i]['s4'] = dist
    smoothDist = (sensors[i]['s1'] + sensors[i]['s2'] + sensors[i]['s3'] + sensors[i]['s4'])/4
    return (smoothDist - 25.0)

'''def overallDistance():
    average = 0

    #check all distances for every sensors and add the distance to a total amount
    for i in sensors:
        dist = distance(sensors[i]['TRIG'], sensors[i]['ECHO'])
        sDist = Smoother(i, dist)
        average += sDist
        #print(i, sDist)
        #60ms divided by the amount of sensors
        #time.sleep(0.0075)
        #below only for testing
        time.sleep(0.0075)
    finalDistance = average/8
    return finalDistance'''

def smallestDistance():
    #print('smallestDistance')
    smallestD = []
    for i in sensors:
        dist = distance(sensors[i]['TRIG'], sensors[i]['ECHO'])
        #print(i, dist)
        smoothDist = Smoother(i, dist)
        smallestD.append(smoothDist)
        time.sleep(0.01)
    c = min(float(s) for s in smallestD)
    smallestDistancesSmoother[0] = smallestDistancesSmoother[1]
    smallestDistancesSmoother[1] = smallestDistancesSmoother[2]
    smallestDistancesSmoother[2] = smallestDistancesSmoother[3]
    smallestDistancesSmoother[3] = smallestDistancesSmoother[4]
    smallestDistancesSmoother[4] = c
    theSmallestDistance = (sum(smallestDistancesSmoother))/5
    #some glitch occurs that makes this less than 0, too lazy to fix
    if theSmallestDistance < 0:
        theSmallestDistance = 0
    #print(theSmallestDistance)
    #print(smallestD)
    return theSmallestDistance
'''
def calculateVolume(dist):
    takes the overall distance and for every 50cm a sequential sound
file reaches 100 in volume (max) and the remainder is addd to the nwext
available volume list item that isn't 100

    x = dist
    y = x % 50
    z = int((x-y) / 50)
    if z == 0:
        volumes[0] = x*2
    else:
        volumes[z] = y*2
        while z != 0:
            volumes[z-1] = 100
            z = z-1
    print(volumes)
    return volumes
'''
def calculateVolume2(dist):
    '''new version from last function'''
    #sets all volumes to zero to reset
    for i in range(len(volumes)):
            volumes[i] = 0
    x = dist
    y = x % 100
    z = int((x-y) / 100)
    if z == 0:
        volumes[0] = x
    else:
        for i in range(z):
            volumes[i] = 100
        volumes[z] = y
    #print(volumes)
    return volumes

def calculateVolume3(dist):
    #print('calculateVolume3')
    p = 100/70
    for i in range(len(volumes)):
            volumes[i] = 0
    if 231 < dist < 300:
        x = 300 - dist
        volumes[0] = x*p
    if dist < 230:
        invert = 300 - dist
        x = invert - 30
        y = x % 70
        z = int((x-y) / 70)
        if z == 0:
            volumes[0] = x*p
        else:
            for i in range(z):
                volumes[i] = 100
            volumes[z] = y*p
    #print(volumes)
    return volumes
    
def audioPlayer(players, audio):
    #print('audioPlayer')
    '''generates audio players and sets correct settings'''
    z = 0
    for p in players:
        globals()[p] = mplayer.Player()
        globals()[p].loadfile(audio[z])
        globals()[p].volume = 0
        globals()[p].loop = 0
        #print(globals()[p])
        z += 1

def volumeAdjust(v, players):
    #print('volumeAdjust')
    '''accepts newly generated volumes and players array as arugments
    and adjusts volumes to new ones'''
    z = 0
    for p in players:
        globals()[p].volume = v[z]
        z += 1
        #print(globals()[p].volume)

def stopPlayers(players):
    '''on exit quits all auido players'''
    z = 0
    for p in players:
        globals()[p].quit()
        z += 1
    
if __name__ == '__main__':
    try:
        audioPlayer(players, audio)
        while True:
            #print('------')
            #d = overallDistance()
            d = smallestDistance()
            v = calculateVolume3(d)
            volumeAdjust(v, players)
 
        # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        stopPlayers(players)
        GPIO.cleanup()
