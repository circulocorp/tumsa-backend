from classes.tumsa import Tumsa


def main():
    tumsa = Tumsa(dbhost="127.0.0.1", dbuser="postgres", dbpass="admin1234", dbname="tumsadev")
    viajes = tumsa.get_todays_trips()
    for viaje in viajes:
        print(viaje["trip"])

if __name__ == '__main__':
    main()
