import random

from game.base_strategy import BaseStrategy
from game.plane import Plane, PlaneType
from game.plane_data import Vector
import math
# The following is the heart of your bot. This controls what your bot does.
# Feel free to change the behavior to your heart's content.
# You can also add other files under the strategy/ folder and import them


speeds = {
    PlaneType.STANDARD : 2,
    PlaneType.FLYING_FORTRESS: 1,
    PlaneType.THUNDERBIRD: 2.5,
    PlaneType.SCRAPYARD_RESCUE: 1.5,
    PlaneType.PIGEON: .5,
}

turningRadius = {
    PlaneType.STANDARD : 15,
    PlaneType.FLYING_FORTRESS: 10,
    PlaneType.THUNDERBIRD: 15,
    PlaneType.SCRAPYARD_RESCUE: 10,
    PlaneType.PIGEON: 30,
}

def clearLog(filepath: str):
    f = open(filepath, 'w')
    f.flush()
    f.close()


def print(text: str,filepath: str):
    f = open(filepath, 'a')
    f.write(text)
    f.close()

def distance(o1, o):
    return ((o1.x - o.x) ** 2 + (o1.y - o.y) ** 2) ** .5

def dot(o1, o):
        return o1.x*o.x+o1.y*o.y

def getNextPos(plane):
    planePosition = plane.position
    currentAngle = plane.angle
    speed = speeds[plane.type]
    differenceVector = Vector(0,0)
    differenceVector.x = speed * math.cos(currentAngle)
    differenceVector.y = speed * math.sin(currentAngle)
    return planePosition.__add__(differenceVector)

def getAngleToPos(plane, position: Vector):
    planePos = plane.position
    dx = position.x - planePos.x
    dy = position.y - planePos.y
    angle = math.degrees(math.atan(dx/dy))
    return angle #returns angle in degrees between -90 and 90


def clamp(bot, top, value):
    if value < bot:
        return bot

    if value > top:
        return top
    
    return value

def planes_facing_each_other(angle, enemy_angle):
    if 160 <= abs(angle - enemy_angle) <= 200:
        return True
    
def set_fleeing_amngle(angle, enemy_angle):
    fleeing_angle = enemy_angle + 180
    if fleeing_angle >= 360: fleeing_angle -= 360
    angle_to_travel = angle - fleeing_angle
    return angle_to_travel

class Strategy(BaseStrategy):
    # BaseStrategy provides self.team, so you use self.team to see what team you are on
    # You can define whatever variables you want here

    fileLogPath = "log.txt"
    my_counter = 0
    global_positions = dict()
    
    def select_planes(self) -> dict[PlaneType, int]:
        # Select which planes you want, and what number
        return {
            #PlaneType.STANDARD: 1,
            #PlaneType.FLYING_FORTRESS: 1,
            PlaneType.THUNDERBIRD: 5,
            #PlaneType.SCRAPYARD_RESCUE: 1,
            #PlaneType.PIGEON: 10,
        }
    
    def steer_input(self, planes: dict[str, Plane]) -> dict[str, float]:
        
        for id, plane in planes.items():
            if self.my_counter == 0:
                self.global_positions[id] = []
            self.global_positions[id].append(plane.position)

        # Define a dictionary to hold our response
        response = dict()
        enemies = dict()
        myplanes = dict()

        # #Sort planes
        for id, plane in planes.items():
            # id is the unique id of the plane, plane is a Plane object
            # We can only control our own planes
            if plane.team != self.team:
                # Ignore any planes that aren't our own - continue
                enemies[id] = plane
            else:
                response[id] = -1
                myplanes[id] = plane

        for id, plane in myplanes.items():
            shortest = None
            currentDistance = 0
            for id, planeE in enemies.items():
                #Find closet enemy
                if distance(plane.position, planeE.position) < currentDistance:
                    shortest = planeE

            if self.my_counter < 5:
                response[id] = random.randrange(2) - 1

            if plane is None or shortest is None:
                continue

            if planes_facing_each_other(plane.angle, shortest.angle): #Evade
                angle = set_fleeing_amngle(plane.angle, shortest.angle)
                steer = angle / turningRadius[plane.type]
                response[id] = clamp(-1, 1, steer)
            else: #Attack
                #Get enemy planes next approximate position
                targetPos = getNextPos(planeE)
                angle = getAngleToPos(plane, planeE.position)
                if (abs(angle) < 0.01):
                    response[id] = 0  #prevent division by 0
                    continue
                steer = angle / turningRadius()
                response[id] = clamp(-1, 1 , steer)

        # Increment counter to keep track of what turn we're on
        self.my_counter += 1

        # Return the steers
        #print(self.fileLogPath, response.values())
        return response


