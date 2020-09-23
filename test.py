from classes.tumsa import Tumsa
from PydoNovosoft.utils import Utils


def main():
    #tumsa = Tumsa(dbhost="127.0.0.1", dbuser="postgres", dbpass="admin1234", dbname="tumsadev")
    #viajes = tumsa.get_todays_trips()
    #for viaje in viajes:
    #    print(viaje["trip"])
    print(Utils.string_to_date(str("2020-09-22T10:24:00.520Z").split('.')[0], "%Y-%m-%dT%H:%M:%S"))

if __name__ == '__main__':
    main()
