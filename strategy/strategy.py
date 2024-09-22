from game.base_strategy import BaseStrategy
from game.plane import Plane, PlaneType
from game.plane_data import Vector
import math

# The following is the heart of your bot. This controls what your bot does.
# Feel free to change the behavior to your heart's content.
# You can also add other files under the strategy/ folder and import them


# Dictionary for quickly looking up radi
turningRadius = {
    PlaneType.STANDARD: 15,
    PlaneType.FLYING_FORTRESS: 10,
    PlaneType.THUNDERBIRD: 15,
    PlaneType.SCRAPYARD_RESCUE: 10,
    PlaneType.PIGEON: 30
}

# Dictionary for quickly looking up speeds
planeSpeed = {
    PlaneType.STANDARD: 2,
    PlaneType.FLYING_FORTRESS: 1,
    PlaneType.THUNDERBIRD: 2.5,
    PlaneType.SCRAPYARD_RESCUE: 1.5,
    PlaneType.PIGEON: .5,
}


def print_dict(dictionary: dict, filepath: str):
    f = open(filepath, 'a')
    # noinspection PyArgumentList
    for key, value in dictionary.items():
        f.write('%s:%s\n' % (key, value))


def printf(text: str, filepath: str):
    f = open(filepath, 'a')
    f.write(text)


def distance(o: Vector, o1: Vector):
    return ((o.x - o1.x) ** 2 + (o.y - o1.y) ** 2) ** .5


def dot(o1, o):
    return o1.x*o.x+o1.y*o.y


def get_next_pos(plane):
    plane_position = plane.position
    current_angle = plane.angle
    speed = plane.stats.speed
    difference_vector = Vector(0, 0)
    difference_vector.y = speed * math.sin(current_angle)
    difference_vector.x = speed * math.cos(current_angle)
    return Vector(plane_position.x + difference_vector.x, plane_position.y + difference_vector.y)


def get_last_pos(plane):
    plane_position = plane.position
    current_angle = plane.angle
    speed = plane.stats.speed * 2
    difference_vector = Vector(0, 0)
    difference_vector.y = speed * math.sin(current_angle)
    difference_vector.x = speed * math.cos(current_angle)
    return Vector(plane_position.x - difference_vector.x, plane_position.y - difference_vector.y)


# Returns angle in degrees between -90 and 90
def get_angle_to_pos(plane: Plane, target_position: Vector):
    plane_pos = plane.position
    dx = target_position.x - plane_pos.x
    dy = target_position.y - plane_pos.y
    global_angle = math.degrees(math.atan2(dy, dx))

    if global_angle < 0:
        global_angle += 360

    angle = plane.angle - global_angle
    return angle


def validate_final(angle):
    if angle > 180:
        angle -= 360
    elif angle < -180:
        angle += 360

    #printf("Final angle: " + str(angle), "log.txt")

    return angle


def clamp(bot, top, value):
    if value < bot:
        return bot

    if value > top:
        return top
    
    return value


def planes_facing_each_other(angle, enemy_angle):
    cone_width = 60
    if (180 - cone_width / 2) <= abs(angle - enemy_angle) <= (180 + cone_width / 2):
        return True


def in_bounds(minimum, maximum, value):
    if minimum < value < maximum:
        return True

    return False


def determine_best_move(plane, enemy_pos, current_distance, angle):
    next_distance = distance(plane.position, enemy_pos)
    target_angle = get_angle_to_pos(plane, enemy_pos)

    printf(str(current_distance - next_distance) + '\n', "log.txt")

    if (current_distance - next_distance) > 1.5 and current_distance < 20:
        if planes_facing_each_other(plane.angle, angle):
            if target_angle > 0:
                target_angle -= 110
            else:
                target_angle += 110
        else:
            if target_angle > 0:
                target_angle -= 180
            else:
                target_angle += 180

    return target_angle


class Strategy(BaseStrategy):
    # BaseStrategy provides self.team, so you use self.team to see what team you are on
    # You can define whatever variables you want here

    fileLogPath = "log.txt"
    my_counter = 0
    global_positions = dict()
    
    def select_planes(self) -> dict[PlaneType, int]:
        # Select which planes you want, and what number
        return {
            PlaneType.STANDARD: 2,
            PlaneType.FLYING_FORTRESS: 0,
            PlaneType.THUNDERBIRD: 2,
            PlaneType.SCRAPYARD_RESCUE: 1,
            PlaneType.PIGEON: 10,
        }
    
    def steer_input(self, planes: dict[str, Plane]) -> dict[str, float]:
        
        for id, plane in planes.items():
            if self.my_counter == 0:
                self.global_positions[id] = []
            self.global_positions[id].append(plane.position)

        # Define a dictionary to hold our response
        response = dict()
        enemies = dict()
        my_planes = dict()

        # #Sort planes
        for id, plane in planes.items():
            # id is the unique id of the plane, plane is a Plane object
            # We can only control our own planes
            if plane.team != self.team:
                # Ignore any planes that aren't our own - continue
                enemies[id] = plane
            else:
                response[id] = 0
                my_planes[id] = plane

        for id, plane in my_planes.items():

            closest = None
            current_distance = 0
            shortest_distance = 100000000000
            average_distance = 0
            search_radius = 5

            enemies_in_area = []

            for enemy_id, enemy_plane in enemies.items():
                current_distance = distance(plane.position, enemy_plane.position)

                # Find next enemy
                if current_distance < shortest_distance:
                    shortest_distance = current_distance
                    closest = enemy_plane
                    if current_distance < search_radius:
                        average_distance += current_distance
                        enemies_in_area.append(enemy_plane)

            target_angle = float
            next_distance = float
            average_enemy_next_pos = Vector(0, 0)
            if len(enemies_in_area) != 0:
                total_vector = Vector(0, 0)
                for enemy_plane in enemies_in_area:
                    total_vector + get_next_pos(enemy_plane)

                average_enemy_next_pos.x = total_vector.x / len(enemies_in_area)
                average_enemy_next_pos.x = total_vector.y / len(enemies_in_area)
                average_distance /= len(enemies_in_area)

                target_angle = determine_best_move(plane, average_enemy_next_pos, average_distance, closest.angle)
            else:
                target_angle = determine_best_move(plane, get_next_pos(closest), shortest_distance, closest.angle)

            #printf(str(target_angle), self.fileLogPath)
            # Validate angle
            if abs(target_angle) < .001:
                steer = 0
            else:
                steer = -validate_final(target_angle) / turningRadius[plane.type]

            # Bounds check
            relative_distance = 4.5 * planeSpeed[plane.type]
            x_max = 50 - relative_distance
            y_max = 50 - relative_distance
            x_min = -50 + relative_distance
            y_min = -50 + relative_distance
            if not in_bounds(x_min, x_max, plane.position.x):
                if plane.angle <= 180:
                    steer = -1
                else:
                    steer = 1

                if plane.position.x > 0:
                    steer *= -1

            if not in_bounds(y_min, y_max, plane.position.y):
                if 90 <= plane.angle <= 270:
                    steer = -1
                else:
                    steer = 1

                if plane.position.y > 0:
                    steer *= -1
            # End of bounds check

            # Beginning maneuver
            if self.my_counter < 5:
                if plane.position.x > 0:
                    steer = -1
                else:
                    steer = 1
            elif self.my_counter < 10:
                steer = 0
            # End of maneuver

            # Submit response
            response[id] = clamp(-1, 1, steer)
        # End of main for loop

        # Increment counter to keep track of what turn we're on
        self.my_counter += 1

        # Return the steers
        #printf(str(self.my_counter), self.fileLogPath)
        return response
