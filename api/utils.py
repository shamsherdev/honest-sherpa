from math import radians, cos, sin, asin, sqrt
import re

user_type = ["homeowner", "vacationer", "propertymanager"]

def check_password(password):
    return bool(re.match('^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*\W).{8,16}$', password))==True


def get_distance(latitude1, longitude1, latitude2, longitude2):
    longitude1, latitude1, longitude2, latitude2 = map(
        radians,
        [float(longitude1), float(latitude1), float(longitude2), float(latitude2)],
    )
    dlon = float(longitude2) - float(longitude1)
    dlat = float(latitude2) - float(latitude1)
    a = (
        sin(dlat / 2) ** 2
        + cos(float(latitude1)) * cos(float(latitude2)) * sin(dlon / 2) ** 2
    )
    c = 2 * asin(sqrt(a))
    r = 3956
    return c * r
