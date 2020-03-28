import os
from cmd import Cmd
from time import sleep

class GameObject:
    def __init__(self, name,description,tag,location=None):
        self.name = name
        self.description = description
        self.tag = tag
        self.location = location
    
    def __repr__(self):
        return self.name

class Road(GameObject):
    def __init__(self, name, description, tag, location, destination):
        super().__init__(name,description,tag,location)
        self.destination = destination

player = GameObject('Ego','Yep..this is what we look like','player',1)

game_objects =[
        player,
        GameObject('Entrance to Guardroom','Abandoned guardroom, usually guarded by undead, constructs, or other creatures that do not need to eat or sleep','guardroom',None),
        GameObject('Old Chamber','Dripping chamber inscribed with runes','chamber',None),
        GameObject('Gold Key','Very old key. Probably opens door or chest','key',1),
        GameObject('Wooden Chest','Sturdy chest made of red wood. Unfortunately it is closed','chest',2),
        GameObject('Old Sword','Father\'s old rusty sword','sword',0),
        GameObject('Storage','Storage, stocked with tools for maintaining the tomb and preparing the dead for burial','storage',None),
        GameObject('Workshop','Workshop for embalming the dead','workshop',None),
        GameObject('Skeleton','Good and cheap labor worker','skeleton',7),
        Road('Stone stairs', 'Old slippery stone stairs', 'stairs',1,2),
        Road('Chamber exit', 'Exit portal  made of stone blocks', 'exit',2,1),
        Road('Wooden doors', 'Old crooked doors. Open','doors',2,6),
        Road('Chamber entrance', 'Exit back to chamber','entrance',6,2)
        ]

def slowPrint(text,speed):
    for x in text:
        print(x, end='', flush=True)
        sleep(speed)

def render():
    screen=''
    screen+='You are in: \n'
    screen+='*** '+game_objects[player.location].name+' ***\n'
    screen+=game_objects[player.location].description+'\n'
    slowPrint(screen,0.01)
    print('You can see:')
    print('\033[33m',listObjectsAtLocation(player.location),'\033[0m')
    return None

def findGameObjectByTag(tag):
    for obj in game_objects:
        if obj.tag.lower()==tag.lower(): return obj
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

def getAccessibleObject(intention,tag):
    obj = findGameObjectByTag(tag)
    if obj == None :
        print ('I think we do not know how to access',tag)
    elif not(obj == player or
             obj == game_objects[player.location] or
             obj.location == game_objects.index(player) or
             obj.location == player.location or
             getRoad(player.location,game_objects.index(obj)) != None or
             obj.location == None or
             game_objects[obj.location].location == game_objects.index(player) or
             game_objects[obj.location].location == player.location
            ):
        print('I am afraid we do not see',tag)
        obj = None
    return obj

def getPossession(source, tag):
    obj  = findGameObjectByTag(tag)
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

def executeGo(tag): # renamte target to tag ?
    go_target = getAccessibleObject('go',tag)
    if go_target == None: return False
    if player.location == game_objects.index(go_target):
        print('I think we are already in place called',tag)
        return False
    if isinstance(go_target,Road):
        player.location = go_target.destination
        return render
    if getRoad(player.location,game_objects.index(go_target)) != None:
        player.location = game_objects.index(go_target)
        return render
    if go_target.location != player.location:
        print('I think we do not see',tag)
    else:
        print('We can\'t')
    
    return False

def executeInventory():
    print('You have:')
    print('\033[33m',listObjectsAtLocation(game_objects.index(player)),'\033[0m')
    return None

def executeGet(tag):
    obj = getAccessibleObject('go',tag)
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

    def do_inv(self,line):
        self.game_state = executeInventory()

    def do_drop(self,line):
        self.game_state = executeDrop(line) #moveGameObject22(line,player,game_objects[player.location]) 

    def do_get(self,line):
        self.game_state = executeGet(line)

    def do_exit(self,line):
        return True

    def postcmd(self,stop,line):
        if (stop == False or stop == None) and self.game_state:
            self.game_state()
        return stop

os.system('clear')
AdventureShell().cmdloop()