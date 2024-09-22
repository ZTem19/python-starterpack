import random

from game.base_strategy import BaseStrategy
from game.plane import Plane, PlaneType
from game.plane_data import Vector
import math

# The following is the heart of your bot. This controls what your bot does.
# Feel free to change the behavior to your heart's content.
# You can also add other files under the strategy/ folder and import them


turningRadius = {
    PlaneType.STANDARD: 15,
    PlaneType.FLYING_FORTRESS: 10,
    PlaneType.THUNDERBIRD: 15,
    PlaneType.SCRAPYARD_RESCUE: 10,
    PlaneType.PIGEON: 30
}

def clearLog(filepath: str):
    f = open(filepath, 'w')
    f.flush()
    f.close()


def print(text: str,filepath: str):
    f = open(filepath, 'a')
    for key, value in dict.items():
        f.write( '%s:%s\n' % (key, value))


def print(text: str, filepath: str):
    f = open(filepath, 'a')
    f.write(text + "\n")


def distance(o1, o):
    return ((o1.x - o.x) ** 2 + (o1.y - o.y) ** 2) ** .5


def dot(o1, o):
        return o1.x*o.x+o1.y*o.y


def getNextPos(plane):
    planePosition = plane.position
    currentAngle = plane.angle
    speed = plane.stats.speed
    differenceVector = Vector(0,0)
    differenceVector.y = speed * math.sin(currentAngle)
    differenceVector.x = speed * math.cos(currentAngle)
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
                response[id] = 0
                myplanes[id] = plane

        for id, plane in myplanes.items():
            closest = None
            currentDistance = 100000000000
            shorestDistance = 100000000000

            for enemyid, enemyPlane in enemies.items():
                #Find closet enemy
                currentDistance = distance(plane.position, enemyPlane.position)
                if currentDistance < shorestDistance:
                    closest = enemyPlane
                    shorestDistance = currentDistance

            # if self.my_counter < 5:
            #     response[id] = (random.random() * 2) - 1
            #     continue

            print(str(shorestDistance), self.fileLogPath)

            enemyNextPos = getNextPos(closest)
            targetAngle = getAngleToPos(plane, enemyNextPos)
            if shorestDistance < 5:
                if distance(plane.position, enemyNextPos) < shorestDistance:   #enemy getting closer
                    if targetAngle > 0:
                        targetAngle -= 180
                    else:
                        targetAngle += 180

            if abs(targetAngle) < .001:
                steer = 0
            else:
                steer = targetAngle / turningRadius[plane.type]

            response[id] = clamp(-1, 1, steer)

        # Increment counter to keep track of what turn we're on
        self.my_counter += 1

        # Return the steers
        #printdict(response, self.fileLogPath)
        print(str(self.my_counter), self.fileLogPath)

        return response

        # if dot(plane.position, shortest.position) > 0 or currentDistance < 10: #Evade
        #     targetPos = getNextPos(shortest)
        #     targetPos = -targetPos.x, -targetPos.y
        #     angle = getAngleToPos(plane, targetPos)
        #     if (abs(angle) < 0.01):
        #         response[id] = 0  # prevent division by 0
        #         continue
        #     steer = turningRadius[plane.type] / angle
        #     response[id] = clamp(-1, 1, steer)
        # else: #Attack
        #     #Get enemy planes next approximate position
        #
        #     targetPos = getNextPos(shortest)
        #     angle = getAngleToPos(plane, targetPos)
        #     if (abs(angle) < 0.01):
        #         response[id] = 0  #prevent division by 0
        #         continue
        #     steer = turningRadius[plane.type]/angle
        #     response[id] = clamp(-1, 1, steer)

