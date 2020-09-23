import psycopg2 as pg
from PydoNovosoft.utils import Utils
from datetime import datetime, timedelta
import datetime
import json


class Tumsa(object):

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def insert_viaje(self, viaje):
        try:
            conn = pg.connect(host=self.dbhost, user=self.dbuser, password=self.dbpass, port="5432", database=self.dbname)
            sql = "INSERT INTO departures(nid,trip,vehicle,created,start_date,end_date,rounds,start_point,end_point," \
                  "total_time,route) values(uuid_generate_v4(),%s,%s,NOW(),%s,%s,%s,%s,%s,%s,%s)"
            cursor = conn.cursor()
            cursor.execute(sql, (viaje["trip"], viaje["vehicle"], viaje["start_date"], viaje["end_date"], viaje["rounds"],
                                 viaje["start_point"], viaje["end_point"], viaje["total_time"], viaje["route"]))
            conn.commit()
            return True
        except (Exception, pg.Error) as error:
            print(error)
            return False

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

    def get_todays_trips(self):
        viajes = []
        try:
            base = Utils.format_date(datetime.datetime.now(), "%Y-%m-%d")
            start = base+" 00:00:00"
            end = base+" 23:59:59"
            conn = pg.connect(host=self.dbhost, user=self.dbuser, password=self.dbpass, port="5432",
                              database=self.dbname)
            sql = "select * from departures where start_date>=%s and end_date<=%s order by start_date asc"
            cursor = conn.cursor()
            cursor.execute(sql, (start, end))
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


    def get_roles(self, ruta):
        roles = []
        try:
            conn = pg.connect(host=self.dbhost, user=self.dbuser, password=self.dbpass, port="5432",
                              database=self.dbname)
            sql = "select * from roles where route='"+ruta+"' order by hour asc"
            cursor = conn.cursor()
            cursor.execute(sql)
            data = cursor.fetchall()
            for row in data:
                role = {}
                role["nid"] = row[0]
                role["hour"] = row[1]
                role["rounds"] = int(row[2])
                role["route"] = row[3]
                roles.append(role)
        except (Exception, pg.Error) as error:
            print(error)
        finally:
            return roles

    def calc_trip(self, route, day, role):
        calc = {}
        print(day)
        print(role["hour"])
        calc["start_date"] = Utils.string_to_date(day+" "+role["hour"], "%Y-%m-%d %H:%M:%S")
        calc["trip"] = []
        calc["total_time"] = 0
        time = 0
        started = 0
        for i in range(int(role["rounds"])) :
            for place in route["points"]["places"]:
                place2 = {}
                place2["id"] = place["id"]
                place2["description"] = place["description"]
                start = calc["start_date"]
                if "lastComment" in place and len(json.loads(place["lastComment"])) > 0:
                    for cond in json.loads(place["lastComment"]):
                        dt2 = Utils.format_date(start + timedelta(minutes=(time + int(place["time"]))), "%H:%M")
                        if cond["key"] == route["name"] and (i+1) == int(cond["vuelta"]) and dt2 == cond["time"]:
                            oldtime = start + timedelta(minutes=(time + int(place["time"])))
                            ntime = Utils.string_to_date(Utils.format_date(start, "%Y-%m-%d")+" "+cond["ntime"]+":00", "%Y-%m-%d %H:%M:%S")
                            time = time + int((ntime-oldtime).seconds / 60) + int(place["time"])
                            break
                        else:
                            time = time + int(place["time"])
                else:
                    time = time + int(place["time"])
                place2["hour"] = start + timedelta(minutes=time)
                place2["round"] = i + 1
                calc["trip"].append(place2)
            time = time + int(route["time_rounds"])

        calc["total_time"] = time
        calc["end_date"] = calc["start_date"] + timedelta(minutes=time)
        calc["start_point"] = route["points"]["places"][0]["id"]
        calc["end_point"] = route["points"]["places"][-1]["id"]
        return calc

    def get_ruta(self, id):
        routes = []
        try:
            conn = pg.connect(host=self.dbhost, user=self.dbuser, password=self.dbpass, port="5432",
                              database=self.dbname)
            sql = "select * from routes where nid='"+id+"'"
            cursor = conn.cursor()
            cursor.execute(sql)
            data = cursor.fetchall()
            for row in data:
                route = {}
                route["nid"] = row[0]
                route["name"] = row[1]
                route["time_rounds"] = int(row[2])
                route["created_by"] = row[3]
                route["created"] = str(row[4])
                route["status"] = int(row[5])
                route["points"] = row[6]
                routes.append(route)
        except (Exception, pg.Error) as error:
            print(error)
        finally:
            return routes
