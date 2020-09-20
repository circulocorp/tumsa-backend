import psycopg2 as pg


class Tumsa(object):

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def get_viaje(self, id):
        viajes = []
        try:
            conn = pg.connect(host=self.dbhost, user=self.dbuser, password=self.dbpass, port="5432",
                              database=self.dbname)
            sql = "select * from departures where nid='"+id+"'"
            cursor = conn.cursor()
            cursor.execute(sql)
            data = cursor.fetchall()
            for row in data:
                viaje = {}
                viaje["nid"] = row[0]
                viaje["trip"] = row[1]
                viaje["route"] = row[2]
                viaje["rounds"] = int(row[3])
                viaje["total_time"] = int(row[4])
                viaje["vehicle"] = row[5]
                viaje["created"] = str(row[6])
                viaje["start_date"] = str(row[7])
                viaje["end_date"] = str(row[8])
                viajes.append(viaje)
        except (Exception, pg.Error) as error:
            print(error)
        finally:
            return viajes
