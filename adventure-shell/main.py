import os
from cmd import Cmd
from time import sleep
from enum import Enum

DISTANCE = Enum('DISTANCE','Self Held HeldContained Location Here HereContained Overthere NotHere UnknownObject')

class GameObject:
    def __init__(self, name,description,tag,location=None,condition=None,false_description=''):
        self.name = name
        self.__description = description
        self.tag = tag
        self.location = location
        self.__false_description = false_description
        if condition == None :
            self.__lambda = lambda self: True
        else:
            self.__lambda = condition
        
    def condition(self):
        return self.__lambda(self)
    
    #@property
    #def location(self):
    #    return self.__location
    
    @property
    def description(self):
        if self.condition() : return self.__description
        return self.__false_description

    def __repr__(self):
        return self.name

class Road(GameObject):
    def __init__(self, name, description, tag, location, destination,is_open='True',condition=None,false_description=''):
        super().__init__(name,description,tag,location,condition,false_description)
        self.__destination = destination
        self.is_open = is_open

    @property
    def destination(self):
        if self.condition() : return self.__destination
        return None



player = GameObject('Ego','Yep..this is what we look like',['player','self','me','us','ego'],1)

game_objects =[
        player,
        GameObject('Entrance to Guardroom','Abandoned guardroom, usually guarded by undead, constructs, or other creatures that do not need to eat or sleep',['guardroom','entrance to guard room'],None),
        GameObject('Old Chamber','Dripping chamber inscribed with runes',['chamber','old chamber'],None),
        GameObject('Gold Key','Very old key. Probably opens door or chest',['key','gold key','old key'],1),
        GameObject('Wooden Chest','Sturdy chest made of red wood. Unfortunately it is closed',['chest','wooden chest'],2),
        GameObject('Old Sword','Father\'s old rusty sword',['sword','old sword','father\'s sword'],0),
        GameObject('Storage','Storage, stocked with tools for maintaining the tomb and preparing the dead for burial',['storage'],None),
        GameObject('Workshop','Workshop for embalming the dead',['workshop'],None),
        GameObject('Skeleton','Good and cheap labor worker',['skeleton'],6),
        Road('Stone stairs', 'Old slippery stone stairs', ['north','stairs','stone stairs'],1,2),
        Road('Chamber exit', 'Exit portal  made of stone blocks', ['east','exit','chamber exit'],2,1),
        Road('Wooden doors', 'Old crooked doors. Open',['west','doors','wooden doors'],2,6,False,lambda self : self.is_open,'Closed crooked doors'),
        Road('Chamber entrance', 'Exit back to chamber',['east','entrance','chamber entrance'],6,2)
        ]

def slowPrint(text,speed):
    for x in text:
        print(x, end='', flush=True)
        sleep(speed)

def lookAt(obj):
    print('You look at:')
    slowPrint('***'+obj.name+'***\n'+obj.description+'\n',0.01)

def render():
    screen=''
    screen+='You are in: \n'
    screen+='*** '+game_objects[player.location].name+' ***\n'
    screen+=game_objects[player.location].description+'\n'
    slowPrint(screen,0.01)
    print('You can see:')
    print('\033[33m',listObjectsAtLocation(player.location),'\033[0m')
    return None

def getDistance(obj_from, obj_to):
    if obj_to == None : return DISTANCE.UnknownObject
    if obj_from == None : return DISTANCE.UknownObject
    if obj_to == obj_from : return DISTANCE.Self
    if obj_to.location == game_objects.index(obj_from) : return DISTANCE.Held
    if game_objects.index(obj_to) == obj_from.location : return DISTANCE.Location
    if obj_to.location == obj_from.location : return DISTANCE.Here
    if getRoad(obj_from.location,game_objects.index(obj_to)) != None : return DISTANCE.Overthere
    if obj_to.location == None : return DISTANCE.NotHere
    if game_objects[obj_to.location].location == game_objects.index(obj_from) : return DISTANCE.HeldContained
    if game_objects[obj_to.location].location == obj_from.location : return DISTANCE.HereContained

    return DISTANCE.NotHere

def findGameObjectByTag(tag, obj_to, max_distance):
    for obj in game_objects:
        if tag.lower() in [el.lower() for el in obj.tag]  and getDistance(obj,obj_to).value <= max_distance.value: return obj
    else: 
            return None

def listObjectsAtLocation(location):
    return [obj for obj in game_objects if obj.location==location and obj!=player ]

def moveGameObject(what,where):
    if what == None : return False
    if where == None : print('We can\'t shift to nothingness')
    elif what.location == None: print ('We are not powerful to shape lands..yet')
    else:
        print('Succesful action with', what)
        what.location = game_objects.index(where)
    return False

def getAccessibleObject(tag):
    obj = findGameObjectByTag(tag, player,DISTANCE.Overthere)
    if obj == None :
        if findGameObjectByTag(tag, player,DISTANCE.NotHere) == None:    
            print('I am afraid we do not see',tag)
        else:
            print ('I think we do not know how to access',tag)
    return obj

def getPossession(source, tag):
    obj  = findGameObjectByTag(tag,player,DISTANCE.HeldContained)
    if source == None:
        print ('I think we do not understand')
    elif obj == None:
        print ('We can\'t access',tag)
    elif obj == source:
        print ('Impossible')
        obj = None
    elif obj.location !=  game_objects.index(source): 
        print('We can\'t find it here')
        obj = None
    return obj

def getRoad(location,destination):
    for road in game_objects:
        if isinstance(road,Road):
            if road.location == location and road.destination == destination :
                return road
    return None

def executeOpen(tag):
    obj = getAccessibleObject(tag)
    if obj != None:
        get_distance = getDistance(player,obj)
        if isinstance(obj,Road):
            obj.is_open = True
            print(tag,'is now open')

    return False

def executeGo(tag):
    go_target = getAccessibleObject(tag)
    get_distance = getDistance(player,go_target)
    if get_distance == DISTANCE.Overthere :
        player.location = game_objects.index(go_target)
        return render
    if get_distance == DISTANCE.NotHere :
        print('I think we do not see',tag)
        return False
    if get_distance == DISTANCE.UnknownObject :
        return False
    if get_distance == DISTANCE.Location :  
        print('I think we are already in place called',tag)
        return False
    if isinstance(go_target,Road):
        if go_target.destination == None : 
            print('This path is blocked')
            return False
        player.location = go_target.destination
        return render
    print('We can\'t')
    
    return False

def executeInventory():
    print('You have:')
    print('\033[33m',listObjectsAtLocation(game_objects.index(player)),'\033[0m')
    return None

def executeGet(tag):
    obj = getAccessibleObject(tag)
    if obj == None: return False
    if obj == player: 
        print ('We should not do that in game for teens')
        return False
    if obj.location == game_objects.index(player):
        print ('I think we have it already')
        return False
    if obj.location == None or isinstance(obj,Road):
        print ('We are not powerful to shape lands..yet')
        return False
    
    return moveGameObject(obj,player) 


def findNPC():
    for npc in game_objects: 
        if (npc.location == player.location and npc.tag == 'skeleton'): return npc
    else:
        return None
    
def executeLookAt(tag):
    obj = getAccessibleObject(tag)
    if obj == None : return
    lookAt(obj)

def executeDrop(tag):
    return moveGameObject(getPossession(player,tag),game_objects[player.location])

class AdventureShell(Cmd):
    intro = 'Welcome to the Adventure shell.   Type Start to begin or ? to list commands \n'  #help or ? to list commands.\n'
    prompt = ')==[::::> '
    file = None
    game_state = False

    def do_go(self,line):
        self.game_state = executeGo(line)

    def do_look(self,line):
        if line == 'around':
            self.game_state = render()
        elif len(line.split())>1:
            cmd = line.split()
            if cmd[0] == 'at' : 
                executeLookAt(" ".join(el for el in cmd[1:]))

    def do_inv(self,line):
        self.game_state = executeInventory()

    def do_drop(self,line):
        self.game_state = executeDrop(line) #moveGameObject22(line,player,game_objects[player.location]) 

    def do_get(self,line):
        self.game_state = executeGet(line)
    
    def do_open(self,line):
        self.game_state = executeOpen(line)

    def do_exit(self,line):
        return True

    def postcmd(self,stop,line):
        if (stop == False or stop == None) and self.game_state:
            self.game_state()
        return stop
os.system('clear')
AdventureShell().cmdloop()
