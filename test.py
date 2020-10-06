from classes.tumsa import Tumsa
from PydoNovosoft.utils import Utils
import json
import re
from datetime import datetime, timedelta

def main():
    tumsa = Tumsa(dbhost="127.0.0.1", dbuser="postgres", dbpass="admin1234", dbname="tumsadev")
    #viaje = tumsa.get_viaje("d9cfd7d3-e95b-42eb-8a1c-b63e0181bff6")[0]
    #print(viaje["trip"])
    #tumsa.delete_viaje("d9cfd7d3-e95b-42eb-8a1c-b63e0181bff6")
    print(Utils.format_date(datetime.now(), "%Y-%m-%d"))




if __name__ == '__main__':
    main()
