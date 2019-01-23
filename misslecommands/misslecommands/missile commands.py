import pygame, sys, time, random, bres, pygame.mixer  #import
from pygame.locals import *
#defining colors
wood_light = (166, 124, 54)
wood_dark = (76, 47, 0)
blue = (0, 100, 255)
dark_red = (166, 25, 50)
dark_green = (25, 100, 50)
dark_blue = (25, 50, 150)
black = (0, 0, 0)
white = (255, 255, 255)
yellow = (240, 230, 140)
grey = (153, 153, 153)
#end of defining colors
width, height = 1024, 768 #screen size
screen = None
#sounds
explosionSound = pygame.mixer.Sound ("explosionSound.wav") 
missleSound = pygame.mixer.Sound ("missleSound.wav")
winSound = pygame.mixer.Sound ("winSound.wav")
loseSound = pygame.mixer.Sound ("loseSound.wav")
#sounds
maxRadius = 40 #maximum radius of the explosions
allObjects = [] #defining all objects for the game loop
delay = 15   # number of milliseconds delay before generating a USEREVENT
missileSize = 10 #the thickness of the missle trail
silos = [[80, 700], [420, 700], [760, 700]] #the position of the silos
ammo_per_silo = 5 #maximum ammo per silo
gun_length = 90 #the length of the gun
gun_height = 25 #the height of the gun
gun_list = [] #gun array
city_list = [] #citiy array
city_length =  90 #length of the city
city_height =  25 #height of the city
attack_number = 5 #number of missles to be spawned
rate_of_attack = 400 #the chance for the enemy missles to be spawned


def sqr (x): #defining square root 
    return x*x # x times x (x power two)

class gun:
    def __init__ (self, pos): #constructor
        global screen
        self._ammo = ammo_per_silo #sets individual gun's ammo to the maximum ammo per silo
        self._pos = pos #the position of the silo
        self._epicenter = [pos[0] + gun_length/2, pos[1]-gun_height] #the epicenter of the silo
        self._exploding = False #setting default value to the exploding boolean
        self._explosion = None
        self.draw_gun () #calls the draw function after initializeing 
    def draw_gun (self): #the drawing method
        global screen
        print ("rect", self._pos, gun_length, gun_height)
        pygame.draw.rect (screen, dark_blue, (self._pos[0], self._pos[1], gun_length, gun_height), 0) #draws a dark blue rectangle in the desired position/length/height
    def fire (self): #firing missles method
        if self._ammo > 0 and (not self._exploding): #if the ammo count is more then 0 
            self._ammo -= 1 #decrement the ammo count by 1
            createMissile (self._epicenter, pygame.mouse.get_pos ()) #and create a missle from the epicenter of the silo towards the mouse position
    def update (self): #update funciton
        pass
    def ignite (self, p): #ignite function that returns if the silo is exploding
        return self._exploding
    def erase (self): #erase function
        pygame.draw.rect (screen, black, (self._pos[0], self._pos[1], gun_length, gun_height), 0)#paints the rectangle black "erasing" it
    def check (self, p, radius): 
        if (not self._exploding) and sqr (radius) > sqr (p[0]- self._epicenter[0]) + sqr (p[1]- self._epicenter[1]): 
            self._exploding = True 
            createExplosion (p, grey) 
            createExplosion (self._epicenter, light_grey)
            globalRemove (self)
class missile:
    def __init__ (self, start_pos, end_pos):              #constructor
        self.route = bres.bres (start_pos, end_pos)       #calculates the route with Bresenham's algorithm
        self.erase_route = bres.bres (start_pos, end_pos) #calculates the erase route with Bresenham's algorithm
    def update (self): #update function
        if self.route.finished ():                                  #if the route has finished
            globalRemove (self)                                     #delete the object
            createExplosion (self.route.get_current_pos (), white)  #creates explosion at the end of the route
        elif ignites (self.route.get_current_pos ()):               #erases the surrounding area
            createExplosion (self.route.get_current_pos (), grey)   #creates explosion at the end of the route
        drawTrail (self.route.get_current_pos ())                   #calls the draw missle trail function at the current pos
        drawMissile (self.route.get_next ())                        #calls the draw missle function at the next position
    def erase (self):                                               
        while not self.erase_route.finished ():                     #while the route is not finished
            eraseBlock (self.erase_route.get_next ())               #erases the block behind
    def ignite (self, p):
        return False #missle class
class city:
    def __init__ (self, pos): 
        self._pos = pos                                                    #init pos
        self._epicenter = [pos[0] + city_length/2, pos[1]-city_height]     #init epicenter of the city
        self._exploding = False                                            #init the exploding boolean
        self._explosion = None                                             #sets the base value of explosion 
        self.draw_city ()                                                  #calls the draw function after initializeing
    def draw_city (self):                                                  #draw function
        pygame.draw.rect (screen, wood_light, (self._pos[0], self._pos[1], city_length, city_height), 0) #draws a rectangle with the desired color/length/height/position
    def update (self):                                                     #update function
        pass
    def ignite (self, p):                                                  #ignite function
        return self._exploding                                             #explodes self
    def erase (self):                                                      #erases object to black color
        pygame.draw.rect (screen, black, (self._pos[0], self._pos[1], city_length, city_height), 0)
    def check (self, p, radius):
        if (not self._exploding) and sqr (radius) > sqr (p[0]- self._epicenter[0]) + sqr (p[1]- self._epicenter[1]):  #this function creates explosion if it has been hit
            self._exploding = True                                                                                    #and not already exploding
            createExplosion (p, grey)
            createExplosion (self._epicenter, light_grey)
            globalRemove (self) #city class
class explosion:
    def __init__ (self, pos, colour):
        self._radius = 1            #init starting explosion value
        self._maxRadius = maxRadius #init max value to global max radius
        self._increasing = True     #default boolean value to increasing so the explosion actually starts increasing
        self._pos = pos             #init default value of pos
        self._colour = colour       #init default value of colour
    def update (self):              #update function
        if self._increasing:        #if the explosion is increasing
            pygame.draw.circle (screen, self._colour, self._pos, self._radius, 0)   #draws a circle
            self._radius += 1   #increases the radius of the circle
            if self._radius == self._maxRadius:     #if radius is equals max radius
                self._increasing = False            #sets increasing boolean to false
        else:
            pygame.draw.circle (screen, black, self._pos, self._radius, 0) #draw a circle
            self._radius -= 1                                              #decreases the circle's radius
            if self._radius > 0:                                           #if radius is greater than 0 
                pygame.draw.circle (screen, self._colour, self._pos, self._radius, 0)#draw circle
            else:                                                          #else play sound and remove gameobject
                explosionSound.play()
                globalRemove (self)
    def erase (self):
        pygame.draw.circle (screen, black, self._pos, self._radius, 0)
    def ignite (self, p):
        return sqr (self._pos[0]-p[0]) + sqr (self._pos[1]-p[1]) < sqr (self._radius) #explosion class

def drawTrail (p):
    pygame.draw.rect (screen, white, (p[0], p[1], missileSize, missileSize), 0) #this function draws the trail of the missle to the screen in the desired color and size

def drawMissile (p):
    pygame.draw.rect (screen, yellow, (p[0], p[1], missileSize, missileSize), 0) #this function draws the actual missle to the screen in the desired color and size

def eraseBlock (p):
    pygame.draw.rect (screen, black, (p[0], p[1], missileSize, missileSize), 0) #this function draws a black rectangles "erasing" surrounding objects when the missle explodes

def make_cities (): #function that makes cities
    global city_list #the global city array list


    for p in [[100, 768-city_height], [200, 768-city_height], [300, 768-city_height],
              [600, 768-city_height], [700, 768-city_height], [800, 768-city_height]]:
        c = city (p)     #makes a new city object for every p
        city_list += [c] #adds the new object to the city array list

def make_guns():
    global gun_list
    for p in silos:
        g=gun(p)        #makes a new gun object for every p
        gun_list += [g] #adds the new object to the gun array list
        
def check_cities_guns (pos, radius):
    for c in city_list:         #check every object's position and radius in city array list
        c.check (pos, radius)
    for g in gun_list:
        g.check (pos, radius)   #check every object's position and radius in gun array list

def createMissile (start_pos, end_pos): #creates a missle from the starting position leading to the end position
    global allObjects
    allObjects += [missile (start_pos, end_pos)]    #adds a missle to the allobjects array list
    pygame.time.set_timer (USEREVENT+1, delay)


def spawn_attack ():#spawns an enemy missile
    global attack_number
    if attack_number > 0:                                   #if attack number is greater than 0
        if random.randint (1, rate_of_attack) == 1:         #get a random number between 1 and rate of attack, if its 1 spawn an enemy missile
            attack_number -= 1                              #decreases attack count by 1
            c = city_list [random.randint (0, 5)]           #sets c to a random city between 1 and 6 
            createMissile ([random.randint (1, 1000), 0],   #sets the target from a random location to the previously set 'c' city's epicenter
                           c._epicenter)
        if random.randint (1, rate_of_attack) == 1:         #get a random number between 1 and rate of attack, if its 1 spawn an enemy missile
            attack_number -= 1                              #decreases attack count by 1
            g = gun_list [random.randint (0, 2)]            #sets c to a random gun between 1 and 3
            createMissile ([random.randint (1, 1000), 0],   #sets the target from a random location to the previously set 'c' gun's epicenter
                          g._epicenter)

def no_of_cities ():
    n = 0                       #this function checks for the number of the cities 
    for c in city_list:         #checks every member of the city array list with a for loop
        if not c._exploding:    #if the city is not exploding
            n += 1              #increments the value of n
    return n                    #returns n, the number of the remaining cities

def check_finished ():
    if attack_number == 0 and len (allObjects) == 0:            #this function checks the state of the game at the end
        n = no_of_cities ()                                     
        if n == 0:                                              #if there are no cities remaining it prints out:
            print ("you lost!")                                 #"you lost"
            loseSound.Play()                                    #plays the losing sound
        elif n == 1:                                            #if there's only one city remaining it prints out 
            print ("you survived with 1 city left")             #"you survived with 1 city left"
            winSound.play()                                     #plays the winning sound
        else:                                                   #any other case it just prints out the number of cities that has survived
            print ("you survived with", n, "cities left")
            winSound.play()                                     #play the winning sound 
        sys.exit (0)                                            #exits the game

def ignites (p):
    for o in allObjects:     #this function runs trough every object in the game, if there's ignite at their position it returns true 
        if o.ignite (p):
            return True
    return False

def createMissile (start_pos, end_pos):
    global allObjects                                           #this function adds a missle object to the allObjects array list
    allObjects += [missile (start_pos, end_pos)]                #the missle goes towards the 'end' position from the 'start' position
    pygame.time.set_timer (USEREVENT+1, delay)                  #repeatedly create an event on the event queue

def createExplosion (pos, colour):
    global allObjects                                           #this function adds an explosion object to the allObjects array list
    allObjects += [explosion (pos, colour)]                     #the explosion happens at the desired position in the desired colour
    pygame.time.set_timer (USEREVENT+1, delay)                  #repeatedly create an event on the event queue

def globalRemove (e):
    global allObjects                                           #this function removes all objects
    e.erase ()                                                  #by calling the object's erase function
    allObjects.remove (e)                                       #then actually removing it from the scene
    pygame.display.flip ()                                      #update the full display surface to the screen

def updateAll ():
    if allObjects != []:                                        #if there's any object active in the scene
        for e in allObjects:
            e.update ()                                         #this function call's the object's update function
    if allObjects != []:
        pygame.display.flip ()                                  #update the full display surface to the screen
        pygame.time.set_timer (USEREVENT+1, delay)              #repeatedly create an event on the event queue
    spawn_attack()                                              #calls the spawn_attack() method so enemy missiles spawns during the game

def wait_for_event ():
    global screen
    while True:
        event = pygame.event.wait ()                                            #pause the program for an amount of time
        if event.type == pygame.QUIT:                                           #exits the game when event type is QUIT
            sys.exit(0)                                                         #exit
        if event.type == KEYDOWN and event.key == K_ESCAPE:                     #exits the game when the escape button is pressed down
            sys.exit (0)                                                        #exit
        if event.type == pygame.MOUSEBUTTONDOWN:                                #if a mouse button is pressed(in order: left mouse button, right mouse button or middle mouse button)
            if event.button >= 1 and event.button <= 3:                         #left mouse button -> first silo | right mouse button -> last silo | middle mouse button -> second silo
                createMissile (silos[event.button-1], pygame.mouse.get_pos ())  #spawns a missile from the chose silo towards the mouse position
        if event.type == USEREVENT+1:                                           #if any event occurs, calls the update function
            updateAll ()

def main ():
    global screen
    pygame.mixer.pre_init(44100, 16, 2, 4096)               #frequency, size, channels, buffersize
    pygame.mixer.init()                                     #init pygame sound mixer
    pygame.init ()                                          #init pygame
    screen = pygame.display.set_mode ([width, height])      #open a new window with the set size
    make_cities()                                           #call make_city function to draw the cities
    make_guns()                                             #call make_guns function to draw the silos
    wait_for_event ()                                       #call wait_for_event function to Update every gameobject



main ()  #game loop                                           

