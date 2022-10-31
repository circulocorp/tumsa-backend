import psycopg2 as pg
from PydoNovosoft.utils import Utils
from PydoNovosoft.scope import MZone
from datetime import datetime, timedelta
from classes.pdfreport import HTML2PDF
import pandas as pd
import datetime
import json


class Tumsa(object):

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def delete_viaje(self, viaje):
        try:
            conn = pg.connect(host=self.dbhost, user=self.dbuser, password=self.dbpass, port="5432", database=self.dbname)
            sql = "DELETE FROM departures where nid='"+viaje+"'"
            cursor = conn.cursor()
            cursor.execute(sql, ())
            conn.commit()
            return True
        except (Exception, pg.Error) as error:
            print(error)
            return False

    def insert_viaje(self, viaje):
        try:
            conn = pg.connect(host=self.dbhost, user=self.dbuser, password=self.dbpass, port="5432", database=self.dbname)
            sql = "INSERT INTO departures(nid,trip,vehicle,created,start_date,end_date,rounds,start_point,end_point," \
                  "total_time,route,comments,delay,priority) values(uuid_generate_v4(),%s,%s,NOW(),%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            cursor = conn.cursor()
            cursor.execute(sql, (json.dumps(viaje["trip"]), viaje["vehicle"], viaje["start_date"], viaje["end_date"], viaje["rounds"],
                                 viaje["start_point"], viaje["end_point"], viaje["total_time"], viaje["route"],
                                 viaje["comments"], viaje["delay"], viaje["priority"]))
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
                viaje["start_point"] = str(row[9])
                viaje["end_point"] = str(row[10])
                viaje["comments"] = str(row[11])
                viaje["delay"] = int(row[12])
                viajes.append(viaje)
        except (Exception, pg.Error) as error:
            print(error)
        finally:
            return viajes


    def get_trips(self):
        viajes = []
        try:
            conn = pg.connect(host=self.dbhost, user=self.dbuser, password=self.dbpass, port="5432",
                              database=self.dbname)
            sql = "select * from departures"
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
                viaje["start_point"] = str(row[9])
                viaje["end_point"] = str(row[10])
                viaje["comments"] = str(row[11])
                viaje["delay"] = int(row[12])
                viajes.append(viaje)
        except (Exception, pg.Error) as error:
            print(error)
        finally:
            return viajes


    def get_todays_trips(self, route=None):
        viajes = []
        try:
            base = Utils.format_date(Utils.datetime_zone(datetime.datetime.now(), "America/Mexico_City"), '%Y-%m-%d')
            start = base+" 00:00:00"
            end = base+" 23:59:59"
            conn = pg.connect(host=self.dbhost, user=self.dbuser, password=self.dbpass, port="5432",
                              database=self.dbname)
            sql = "select * from departures where start_date>=%s and start_date<=%s "

            if route:
                sql = sql+" and route->>'nid' = '"+route+"'"
            sql = sql + " order by priority asc"
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
                viaje["start_point"] = str(row[9])
                viaje["end_point"] = str(row[10])
                viaje["comments"] = str(row[11])
                viaje["delay"] = int(row[12])
                viaje["priority"] = int(row[13])
                viajes.append(viaje)
        except (Exception, pg.Error) as error:
            print(error)
        finally:
            return viajes

    def get_day_trips(self, day, route=None):
        viajes = []
        try:
            start = day + " 00:00:00"
            end = day + " 23:59:59"
            conn = pg.connect(host=self.dbhost, user=self.dbuser, password=self.dbpass, port="5432",
                              database=self.dbname)
            sql = "select * from departures where start_date>=%s and start_date<=%s "
            print(sql)
            print(start)
            if route:
                sql = sql+" and route->>'nid' = '"+route+"'"
            sql = sql+" order by priority asc"
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
                viaje["start_point"] = str(row[9])
                viaje["end_point"] = str(row[10])
                viaje["comments"] = str(row[11])
                viaje["delay"] = int(row[12])
                viaje["priority"] = int(row[13])
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
            sql = "select nid,hour,rounds,route,start_point,end_point,comments,priority from roles where route='"+ruta+"' order by priority asc"
            cursor = conn.cursor()
            cursor.execute(sql)
            data = cursor.fetchall()
            for row in data:
                role = {}
                role["nid"] = row[0]
                role["hour"] = row[1]
                role["rounds"] = int(row[2])
                role["route"] = row[3]
                role["start_point"] = row[4]
                role["end_point"] = row[5]
                role["comments"] = str(row[6])
                role["priority"] = int(row[7])
                roles.append(role)
        except (Exception, pg.Error) as error:
            print(error)
        finally:
            return roles

    def calc_trip(self, route, day, role):
        calc = {}
        calc["start_date"] = Utils.string_to_date(day+" "+role["hour"], "%Y-%m-%d %H:%M:%S")
        calc["start_point"] = role["start_point"]
        calc["end_point"] = role["end_point"]
        calc["trip"] = []
        calc["total_time"] = 0
        time = 0
        started = 0
        for i in range(int(role["rounds"])):
            for place in route["points"]["places"]:
                place2 = {}
                place2["id"] = place["id"]
                place2["description"] = place["description"]
                start = calc["start_date"]
                if calc["start_point"] != place2["id"] and started == 0:
                    place2["time"] = 0
                    place2["hour"] = ""
                else:
                    if "lastComment" in place and len(json.loads(place["lastComment"])) > 0:
                        found = 0
                        for cond in json.loads(place["lastComment"]):
                            dt2 = Utils.format_date(start + timedelta(minutes=(time + int(place["time"]))), "%H:%M")
                            if cond["k"] == route["name"] and (i+1) == int(cond["v"]) and dt2 == cond["t1"]:
                                place2["condition"] = cond
                                oldtime = start + timedelta(minutes=(time + int(place["time"])))
                                ntime = Utils.string_to_date(Utils.format_date(start, "%Y-%m-%d")+" "+cond["t2"]+":00", "%Y-%m-%d %H:%M:%S")
                                ftime = (ntime-oldtime).seconds
                                if oldtime > ntime:
                                    ftime = (oldtime-ntime).seconds
                                    time = time - int(ftime / 60) + int(place["time"])
                                else:
                                    time = time + int(ftime / 60) + int(place["time"])
                                found = 1
                                break
                        if found == 0:
                            time = time + int(place["time"])
                    else:
                        time = time + int(place["time"])
                    if started == 0:
                        time = 0
                    started = 1
                    place2["time"] = time
                    place2["hour"] = Utils.format_date(start + timedelta(minutes=time), "%Y-%m-%d %H:%M:%S")
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

    def get_pdf_report(self, pdf=None, viaje=None, token=None, pages=1):

        if pdf == None:
            pdf = HTML2PDF()

        m = MZone()
        #m = MZone(user=account["user"], password=account["password"], secret=mzone_secret, client="mz-a3tek", url="https://live.mzoneweb.net/mzone62.api/")
        start_date = Utils.format_date(Utils.string_to_date(viaje["start_date"], "%Y-%m-%d %H:%M:%S")
                                       - timedelta(hours=self.UTC) - timedelta(minutes=40), "%Y-%m-%dT%H:%M:%S") + "Z"
        end_date = Utils.format_date(Utils.string_to_date(viaje["end_date"], "%Y-%m-%d %H:%M:%S")
                                     + timedelta(hours=self.UTC) + timedelta(minutes=40), "%Y-%m-%dT%H:%M:%S") + "Z"

        m.set_token(token)
        delay = int(viaje["delay"])
        pdf.set_data(route=viaje["route"]["name"], vehicle=viaje["vehicle"]["description"],
                     start_date=viaje["start_date"],
                     tolerancia=delay, total_pages=pages)
        pdf.add_page(orientation='L')
        epw = pdf.w - 2 * pdf.l_margin


        fences = m.get_geofences(
            extra="vehicle_Id eq " + viaje["vehicle"]["id"] + " and entryUtcTimestamp gt " + start_date +
                  " and entryUtcTimestamp lt " + end_date, orderby="entryUtcTimestamp asc")

        df = pd.DataFrame(fences)
        all = [[] for i in range(0, viaje["rounds"])]
        head = []

        for he in viaje["route"]["points"]["places"]:
            head.append(he["description"])

        trips = []
        if "trip" in viaje["trip"]:
            trips = viaje["trip"]["trip"]
        else:
            trips = viaje["trip"]

        for place in trips:
            calc = {}
            calc["place_Id"] = place["id"]
            calc["description"] = place["description"]
            calc["estimated"] = place["hour"]
            calc["real"] = ""
            calc["real_hour"] = ""
            calc["delay"] = 0
            calc["check"] = 0
            calc["estimated_hour"] = ""
            calc["color"] = "black"
            if place["hour"] != "":
                fence = []
                calc["estimated_hour"] = Utils.format_date(Utils.string_to_date(place["hour"], "%Y-%m-%d %H:%M:%S"),
                                                           "%H:%M")
                start_date = Utils.format_date(Utils.string_to_date(place["hour"], "%Y-%m-%d %H:%M:%S")
                                               + timedelta(hours=self.UTC) - timedelta(minutes=15),
                                               "%Y-%m-%dT%H:%M:%S") + "Z"
                end_date = Utils.format_date(Utils.string_to_date(place["hour"], "%Y-%m-%d %H:%M:%S")
                                             + timedelta(hours=self.UTC) + timedelta(minutes=15), "%Y-%m-%dT%H:%M:%S") + "Z"

                if "place_Id" in df:
                    row = df[df["place_Id"] == calc["place_Id"]]
                    row2 = row[row["entryUtcTimestamp"] >= start_date]
                    fence = row2[row2["entryUtcTimestamp"] <= end_date].to_dict(orient='records')

                if len(fence) > 0:
                    real = Utils.string_to_date(fence[0]["entryUtcTimestamp"], "%Y-%m-%dT%H:%M:%SZ") - timedelta(
                        hours=self.UTC)
                    estimated = Utils.string_to_date(calc["estimated"], "%Y-%m-%d %H:%M:%S")
                    calc["real"] = Utils.format_date(real, "%Y-%m-%d %H:%M:%S")
                    calc["real_hour"] = Utils.format_date(real, "%H:%M")
                    real_hour = Utils.string_to_date(Utils.format_date(real, "%Y-%m-%d %H:%M") + ":00",
                                                     "%Y-%m-%d %H:%M:%S")

                    diff = int((estimated - real_hour).total_seconds() / 60)

                    if real_hour < (estimated - timedelta(minutes=delay)):
                        calc["delay"] = abs(diff - delay)
                        calc["color"] = "blue"
                    else:
                        if real_hour > (estimated + timedelta(minutes=delay)):
                            calc["delay"] = abs(diff + delay)
                            calc["color"] = "red"
                        else:
                            calc["delay"] = diff
                            calc["color"] = "black"

                    calc["check"] = 1
            all[int(place["round"]) - 1].append(calc)

        col_width = epw / (len(head) + 2)
        pdf.set_font('Arial', 'B', 8)

        th = pdf.font_size
        pdf.set_fill_color(234, 230, 230)
        for data in head:
            pdf.cell(col_width, 2 * th, data, border=1, fill=True, align='C')

        head.append("ADNTO")
        head.append("RTRSO")
        col_width_f = 12
        pdf.cell(col_width_f, 2 * th, "ADNTO", border=1, fill=True, align='C')
        pdf.cell(col_width_f, 2 * th, "RTRSO", border=1, fill=True, align='C')

        pdf.set_font('Arial', '', 9)
        pdf.ln(2 * th)
        th = pdf.font_size

        total_adelanto = 0
        total_retraso = 0

        for vuelta in all:
            atraso = 0
            adelanto = 0
            pos = -1
            for point in vuelta:
                pdf.cell(col_width, 2 * th, point["estimated_hour"], border='LRT', align='C')

            pdf.cell(col_width_f, 2 * th, '', border='R', align='C')
            pdf.cell(col_width_f, 2 * th, '', border='R', align='C')
            pdf.ln(2 * th)
            for point in vuelta:
                pos += 1
                if point["color"] == "red":
                    if pos != len(vuelta) - 1:
                        atraso = atraso + int(point["delay"])
                elif point["color"] == "blue":
                    pdf.set_text_color(0, 0, 255)
                    if pos != len(vuelta) - 1:
                        adelanto = adelanto + int(point["delay"])
                else:
                    pdf.set_text_color(0, 0, 0)

                if point["check"] == 1:
                    pdf.set_text_color(0, 0, 0)
                    if point["color"] == "red":
                        pdf.set_text_color(255, 0, 0)
                    elif point["color"] == "blue":
                        pdf.set_text_color(0, 0, 255)
                    pdf.cell(col_width, 2 * th, ""+point["real_hour"] + "(" + str(point["delay"]) + ")", border='LRB', align='C')
                else:
                    pdf.set_text_color(0, 0, 0)
                    pdf.cell(col_width, 2 * th, "S/CHK", border='LRB', align='C')

            total_adelanto = total_adelanto + adelanto
            total_retraso = total_retraso + atraso
            pdf.set_text_color(0, 0, 255)
            pdf.cell(col_width_f, 2 * th, str(adelanto), border='BR', align='C')
            pdf.set_text_color(255, 0, 0)
            pdf.cell(col_width_f, 2 * th, str(atraso), border='BR', align='C')
            pdf.set_text_color(0, 0, 0)
            pdf.ln(2 * th)

        pdf.set_text_color(0, 0, 0)
        for i in head[:-2]:
            pdf.cell(col_width, 2 * th, " - ", border=1, fill=True, align='C')
        pdf.set_text_color(0, 0, 255)
        pdf.cell(col_width_f, 2 * th, str(total_adelanto), border=1, fill=True, align='C')
        pdf.set_text_color(255, 0, 0)
        pdf.cell(col_width_f, 2 * th, str(total_retraso), border=1, fill=True, align='C')

        pdf.ln(10)
        pdf.ln(10)
        pdf.set_text_color(0, 0, 0)
        # pdf.cell(50, 10, 'COMENTARIOS: ', 0, 0, 'L')
        pdf.ln(10)
        pdf.set_font('Arial', '', 15)
        if not viaje["comments"] or len(viaje["comments"]) < 1 or viaje["comments"] == "None":
            viaje["comments"] = ""
        pdf.cell(200, 10, viaje["comments"], 0, 0, 'L')
        return pdf

