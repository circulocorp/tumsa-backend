from classes.tumsa import Tumsa
from PydoNovosoft.utils import Utils
import json

def main():
    tumsa = Tumsa(dbhost="127.0.0.1", dbuser="postgres", dbpass="admin1234", dbname="tumsadev")
    viaje = tumsa.get_viaje("0eb9e06e-d012-4168-b63b-0208937f24da")[0]
    for place in viaje["trip"]["trip"]:
        if place["hour"] == "":
            print("Empty")
        else:
            print(place["hour"])



if __name__ == '__main__':
    main()
