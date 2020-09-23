from classes.tumsa import Tumsa
from PydoNovosoft.utils import Utils


def main():
    tumsa = Tumsa(dbhost="127.0.0.1", dbuser="postgres", dbpass="admin1234", dbname="tumsadev")
    ruta = tumsa.get_ruta("9f1d445e-a92e-4f87-8cb7-178584854943")[0]
    role = tumsa.get_roles("9f1d445e-a92e-4f87-8cb7-178584854943")
    calcs = tumsa.calc_trip(ruta, "2020-09-23", role[0])
    print(calcs["trip"])



if __name__ == '__main__':
    main()
