from classes.tumsa import Tumsa
from PydoNovosoft.utils import Utils
import json

def main():
    tumsa = Tumsa(dbhost="127.0.0.1", dbuser="postgres", dbpass="admin1234", dbname="tumsadev")
    viaje = tumsa.get_viaje("0b1c20dd-0108-410c-9040-cd8580f07c65")[0]
    for place in viaje["trip"]["trip"]:
        print(place)



if __name__ == '__main__':
    main()
