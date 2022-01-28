import os
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (100,100) # this line lets you position the window on your screen

import random
import math
import pgzrun

WIDTH = 1000
HEIGHT = 750
MAX_DUCKS = 3                               # maximum ducks on screen
MAX_DUCKLIVES = 6                           # number of ducks you can lose before game over
DUCKSPEEDS = [1.5, -2, 2, -1]               # speeds for the ducks when they are spawned are chosen from this list
BOOM_IMAGES = ['boom1', 'boom2', 'boom3']   # images for the animation of an exploding drone
MAX_DRONES = 3
DRONEXLIMIT = 60                            # horizontal boundary for the movements of a drone
DRONEYLIMIT = 120                           # vertical boundary for the movements of a drone
MAX_PLAYTIME = 300.0
gameStatus = 0
hero = Actor('hero_r')
ducklives = MAX_DUCKLIVES
duckspeeds = random.sample(DUCKSPEEDS, len(DUCKSPEEDS))    # mix up the list of duckspeeds randomly 
dronedelay = 60                             # wait a 60 before spawning the first drone
lasers = []
drones = []
ducks = []
score = 0
highScores = []
direction = 1

def draw():
    screen.blit('background', (0, 0))
    if gameStatus == 0: # display the title page
        drawCentreText("DRONE HUNTER\n\n\npress Enter to start\n(arrow keys to move, space to fire)")
    if gameStatus == 1: # play the game
        screen.draw.text(str(score), bottomright=(WIDTH-50, HEIGHT-20), owidth=0.5, ocolor=(255,255,255), color=(0,64,255), fontsize=48)
        drawLives()
        drawLasers()
        drawDrones()
        drawDucks()
        hero.draw()
    if gameStatus == 2: # game over, you ran out of ducks
        drawCentreText("DRONE HUNTER\n\nGAME OVER\n\nYOUR SCORE:  " + str(score) + "\nHIGH SCORE:  " + str(highScores[0]) + "\n\nPRESS ENTER TO PLAY AGAIN")
    if gameStatus == 3: # game over, maximum playtime reached
        drawCentreText("DRONE HUNTER\n\nMAXIMUM PLAYTIME REACHED\n\nYOUR SCORE:  " + str(score) + "\nHIGH SCORE:  " + str(highScores[0]) + "\n\nPRESS ENTER TO PLAY AGAIN")

def drawLives():
    for l in range(ducklives):
        screen.blit("duckface", (20+(l*42), HEIGHT-50))

def drawLasers():
    for l in range(len(lasers)): lasers[l].draw()

def drawDrones():
    for d in range(len(drones)):
        if drones[d].status > 0:
            drones[d].image = BOOM_IMAGES[math.floor(drones[d].status/10)]  # animation, change image every 10th iteration
        drones[d].draw()

def drawDucks():
    for a in range(len(ducks)): ducks[a].draw()

def drawCentreText(t):
    screen.draw.text(t , center=(WIDTH // 2, HEIGHT // 2), owidth=0.5, ocolor=(255,255,255), color=(255,64,0) , fontsize=60)

def on_key_down(key):
    global direction, hero, lasers, gameStatus
    if key == keys.RETURN:
        if gameStatus == 0 or gameStatus == 2 or gameStatus == 3:
            init()
        gameStatus = 1
    if key == keys.LEFT:
        if direction > 0:
            direction = 0
        else:
            direction -= 1
    if key == keys.RIGHT:
        if direction < 0:
            direction = 0
        else:
            direction += 1
    if direction < 0:
        hero.image = 'hero_l'
    else:
        hero.image = 'hero_r'
    if key == keys.SPACE:
        l = len(lasers)
        lasers.append(Actor('laser', (hero.x, hero.y-25)))
        lasers[l].status = 0

def readhighScores():
    global highScores, score
    highScores = []
    highScores.append(score)
    try:
        hsFile = open("highscores.txt", "r")
        for line in hsFile:
            highScores.append(int(line.rstrip()))
    except:
        pass
    highScores.sort(reverse=True)
    print(highScores)

def writehighScores():
    global highScores
    hsFile = open("highscores.txt", "w")
    if len(highScores) > 5: highScores.pop()        # discard the lowest score if there are more than 5 scores in the list
    for s in highScores:
        hsFile.write(str(s) + "\n")

def update():
    global direction, gameStatus, lasers, drones, ducks
    if gameStatus == 1:
        if hero.x > WIDTH-40:
            hero.x = WIDTH-40
            direction = 0
        elif hero.x < 40:
            hero.x = 40
            direction = 0
        else:
            hero.x += direction
        updateLasers()                 # update all Actors
        updateDrones()
        updateDucks()
        if len(ducks) == 0:            # on game over read and write the highscores.txt file
            readhighScores()
            writehighScores()
            gameStatus = 2
        lasers = listCleanup(lasers)   # delete all destroyed Actors from their Actor lists
        drones = listCleanup(drones)
        ducks = ducksCleanup(ducks)

def updateDucks():
    for d in range(len(ducks)):
        checkDroneCollision(d)
        if ducks[d].velocity < 0:
            flapDuckWings(d, 'ducklwingup', 'ducklwingdown')
            if ducks[d].x > -60:
                ducks[d].floatx += ducks[d].velocity
            else:
                ducks[d].floatx = float(WIDTH + 50)
                moveLastDuck(d)
        else:
            flapDuckWings(d, 'duckrwingup', 'duckrwingdown')
            if ducks[d].x < WIDTH + 60:
                ducks[d].floatx += ducks[d].velocity
            else:
                ducks[d].floatx = -50.0
                moveLastDuck(d)
        ducks[d].x = int(ducks[d].floatx)
        ducks[d].y = int(ducks[d].floaty)
        
def flapDuckWings(d, wingsUp, wingsDown):
    if ducks[d].wingstatus == 0:
        ducks[d].image = wingsUp
    if ducks[d].wingstatus == ducks[d].wingspeed:
        ducks[d].image = wingsDown
    if ducks[d].wingstatus > -ducks[d].wingspeed:
        ducks[d].wingstatus -= 1
    else:
        ducks[d].wingstatus = ducks[d].wingspeed

def moveLastDuck(d):        # Make sure the last duck isn't too easy
    if len(ducks) == 1:
        ducks[d].floaty = 220.0
        ducks[d].velocity = 2.5

def updateDrones():
    global dronedelay
    if len(drones) < MAX_DRONES:
        if dronedelay == 0: 
            d = len(drones)
            skyFound, x, y = findEmptySky()
            if skyFound:
                drones.append(Actor('drone', (x, y)))
                drones[d].initx = x
                drones[d].inity = y 
                drones[d].floatx = float(x)
                drones[d].floaty = float(y)
                drones[d].headingx = random.choice([-1,1]) * random.randint(1,4) / 4
                drones[d].headingy = random.choice([-1,1]) * random.randint(1,6) / 4
                drones[d].status = 0
                dronedelay = random.randint(30, 90)
        else:
            dronedelay -= 1
    for d in range(len(drones)):
        if abs(drones[d].x - drones[d].initx) >= DRONEXLIMIT:
            drones[d].headingx = -drones[d].headingx
        drones[d].floatx += drones[d].headingx
        drones[d].x = int(drones[d].floatx)
        if abs(drones[d].y - drones[d].inity) >= DRONEYLIMIT:
            drones[d].headingy = -drones[d].headingy
        drones[d].floaty += drones[d].headingy
        drones[d].y = int(drones[d].floaty)
        if drones[d].status > 0: drones[d].status += 2

def findEmptySky():          # find an empty piece of sky to place a new drone in. returns skyFound, x en y
    attempt = 1
    while attempt < 30:
        # try 30 times to make a new one
        x = random.randint(150, WIDTH-150)
        y = random.randint(150, 360)
        noduckzone = Rect((x-300, y-100), (x+300, y+100))
        noducks = True
        for du in range(len(ducks)):
            if ducks[du].colliderect(noduckzone):
                noducks = False
        if noducks == True:
            return True, x, y
        attempt += 1
    return False, 0, 0

def updateLasers():
    for l in range(len(lasers)):
        lasers[l].y -= 12               # this line determines the speed of the laser blasts
        checkPlayerLaserHit(l)
        if lasers[l].y < 30:
            lasers[l].status = 30

def listCleanup(l):
    newList = []
    for i in range(len(l)):
        if l[i].status < 30: newList.append(l[i])  # a status of 30 or larger cleans the Actor from the list immediatel
    return newList                                 # this provides time to show an animation, like an explosion

def ducksCleanup(l):
    global ducklives
    newList = []
    for i in range(len(l)):
        if l[i].status < 30:
            newList.append(l[i])
        if l[i].status >= 30:
            ducklives -= 1
            if ducklives >= MAX_DUCKS:           # Generate a new duck on screen as long as you have enough ducklives left
                s = duckspeeds[i]
                if s < 0:
                    newList.append(Actor('ducklwingup', (-50,100+i*120)))
                else:
                    newList.append(Actor('duckrwingup', (-50,100+i*120)))
                newList[-1].floatx = (newList[-1].x)
                newList[-1].floaty = float(newList[-1].y)
                newList[-1].velocity = s
                newList[-1].wingspeed = random.randint(10, 20)
                newList[-1].wingstatus = random.randint(0, 10)
                newList[-1].status = 0
    return newList

def checkPlayerLaserHit(l):
    global score
    for d in range(len(drones)):
        if drones[d].collidepoint((lasers[l].x, lasers[l].y)):
            lasers[l].status = 30
            drones[d].status = 2       # start animating the explosion
            score += 10*len(ducks)     # you get more points for shooting a drone with more ducks on screen 
    for d in range(len(ducks)):
        if ducks[d].collidepoint((lasers[l].x, lasers[l].y)):
            lasers[l].status = 30
            ducks[d].status = 30
            
def checkDroneCollision(du):
    global score
    for dr in range(len(drones)):
        if drones[dr].status == 0:
            if drones[dr].collidepoint((ducks[du].x, ducks[du].y)):
                ducks[du].status = 30
                drones[dr].status = 2       # start animating the explosion

def playTimeOver():
    global gameStatus
    readhighScores()
    writehighScores()
    gameStatus = 3

def init():
    global ducklives, duckspeeds, dronedelay, lasers, drones, ducks, score, highScores, direction
    ducklives = MAX_DUCKLIVES
    duckspeeds = random.sample(DUCKSPEEDS, len(DUCKSPEEDS))
    dronedelay = 60
    lasers = []
    drones = []
    ducks = []
    score = 0
    highScores = []
    direction = 1
    hero.x = 500
    hero.y = 544
    for d in range(MAX_DUCKS):
        s = duckspeeds[d]
        if s < 0:
            ducks.append(Actor('ducklwingup', (-200,100+d*120)))  # start the ducks here so they'll fly in from both sides
        else:
            ducks.append(Actor('duckrwingup', (-200,100+d*120)))  # the ducks are 120 px vertically separated
        ducks[d].floatx = float(ducks[d].x)
        ducks[d].floaty = float(ducks[d].y)
        ducks[d].velocity = s
        ducks[d].wingspeed = random.randint(10, 20)  # each duck flaps its wings at a randomly chosen frequency
        ducks[d].wingstatus = random.randint(0, 10)  # random start time for wings flapping
        ducks[d].status = 0
    clock.schedule(playTimeOver, MAX_PLAYTIME)  # game over after MAX_PLAYTIME seconds to prevent brain damage

pgzrun.go()