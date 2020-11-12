from flask import Flask, redirect, url_for, request, Response
from flask import send_file
from PydoNovosoft.scope import MZone
from PydoNovosoft.utils import Utils
from jinja2 import Environment, FileSystemLoader
from classes.tumsa import Tumsa
import json
import pandas as pd
from pandas import ExcelFile
from fpdf import FPDF, HTMLMixin
import os
from io import StringIO
from datetime import datetime, timedelta
import math

app = Flask(__name__)
app.config["DEBUG"] = True
config = Utils.read_config("package.json")
env_cfg = {}
UTC = 6

if os.environ is None or "environment" not in os.environ:
    env_cfg = config["dev"]
else:
    env_cfg = config[os.environ["environment"]]

if env_cfg["secrets"]:
    db_user = Utils.get_secret("tumsa_dbuser")
    db_pass = Utils.get_secret("tumsa_dbpass")
else:
    db_user = env_cfg["dbuser"]
    db_pass = env_cfg["dbpass"]


class HTML2PDF(FPDF, HTMLMixin):

    def set_data(self, route=None, vehicle=None, start_date=None, tolerancia=1,total_pages=1):
        self._route = route
        self._vehicle = vehicle
        self._start_date = start_date
        self._tolerancia = str(tolerancia)+" min."
        self.total_pages = total_pages

    def header(self):
        self.set_font('Arial', 'B', 15)
        # Move to the right
        # Framed title
        self.cell(300, 10, 'MANZANILLO, COLIMA', 0, 0, 'C')
        # Line break
        self.ln(10)
        self.cell(300, 10, 'SISTEMA TUCA', 0, 0, 'C')
        self.ln(10)
        self.cell(300, 10, 'REPORTE DE CHECADAS', 0, 0, 'C')
        self.ln(20)
        self.cell(50, 10, "RUTA "+self._route, 0, 0, 'C')
        self.cell(155, 10, "No. Economico: "+self._vehicle, 0, 0, 'C')
        self.cell(100, 10, "Fecha: "+Utils.format_date(Utils.string_to_date(
            self._start_date, "%Y-%m-%d %H:%M:%S"), "%d/%m/%Y"), 0, 0, 'C')
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', '', 10)
        # Print centered page number
        self.cell(0, 10, 'Pagina '+str(self.page_no())+'/'+str(self.total_pages), 0, 0, 'C')



@app.route('/api/version', methods=['GET'])
def version():
    return config["version"]



@app.route('/api/viajes', methods=['POST'])
def viajes():
    m = MZone()
    viajes = []
    token = request.json["token"]
    day = request.json["date"]
    m.set_token(token)
    user = m.current_user()
    perfil = json.loads(user["phoneHome"])["perfil"]
    vehicles = [v['id'] for v in m.get_vehicles()]
    tumsa = Tumsa(dbhost=env_cfg["dbhost"], dbuser=db_user, dbpass=db_pass, dbname=env_cfg["dbname"])
    trips = tumsa.get_day_trips(day)
    if perfil != "admin":
        viajes = list(filter(lambda d: d['vehicle']["id"] in vehicles, trips))
    else:
        viajes = trips
    return json.dumps(viajes)

@app.route('/api/vehicles', methods=['POST'])
def vehicles():
    m = MZone()
    token = request.json["token"]
    m.set_token(token)
    search = request.json["search"]
    user = m.current_user()
    res = m.get_vehicles(extra="contains(registration,'"+search+"') or contains(unit_Description,'"+search+
                               "') or contains(description,'"+search+"')")
    return json.dumps(res)

@app.route('/api/lastposition', methods=['POST'])
def last_position():
    m = MZone()
    token = request.json["token"]
    m.set_token(token)
    vehicle = request.json["vehicle"]
    res = m.get_last_position(vehicle)
    return json.dumps(res)


@app.route('/api/createtrips', methods=['POST'])
def create_trips():
    m = MZone()
    tumsa = Tumsa(dbhost=env_cfg["dbhost"], dbuser=db_user, dbpass=db_pass, dbname=env_cfg["dbname"])
    token = request.json["token"]
    m.set_token(token)
    camiones = request.json["camiones"].split(',')
    route = tumsa.get_ruta(request.json["ruta"])
    roles = tumsa.get_roles(request.json["ruta"])
    delay = int(request.json["delay"])
    day = request.json["day"]
    j = 0
    if len(roles) == len(camiones):
        for camion in camiones:
            vehicle = m.get_vehicles(extra="description eq '" + camion + "'")
            if len(vehicle) > 0:
                viaje = {}
                calc = tumsa.calc_trip(route[0], day, roles[j])
                viaje["vehicle"] = json.dumps(vehicle[0])
                viaje["start_date"] = str(calc["start_date"])
                viaje["end_date"] = str(calc["end_date"])
                viaje["trip"] = {"trip": calc["trip"]}
                viaje["rounds"] = roles[j]["rounds"]
                viaje["start_point"] = calc["start_point"]
                viaje["total_time"] = int(calc["total_time"])
                viajes["priority"] = int(roles[j]["priority"])
                viaje["end_point"] = calc["end_point"]
                viaje["route"] = json.dumps(route[0])
                viaje["comments"] = ""
                viaje["delay"] = delay
                tumsa.insert_viaje(viaje)
                j = j + 1
        return json.dumps({"status": "ok"})
    else:
        return json.dumps({"status": "error"})


@app.route('/api/allvehicles', methods=['POST'])
def allvehicles():
    m = MZone()
    token = request.json["token"]
    m.set_token(token)
    res = m.get_vehicles()
    return json.dumps(res)


@app.route('/api/places', methods=['POST'])
def places():
    m = MZone()
    token = request.form
    print(token)
    m.set_token(token)
    res = m.get_points()
    return json.dumps(res)

#deprecated
@app.route('/api/users', methods=['POST'])
def create_user(user):
    m = MZone(config["dev"]["mzone_user"], config["dev"]["mzone_pass"], config["dev"]["mzone_secret"], "mz-a3tek")
    user["securityGroupIds"] = [""]
    user["roleIds"] = [""]
    m.gettoken()
    res = m.create_user(user)
    print(res)
    return json.dumps(res)

@app.route('/api/departure', methods=["DELETE"])
def delete_viaje():
    tumsa = Tumsa()
    viaje = request.json["viaje"]
    tumsa.delete_viaje(viaje)
    return json.dumps({})


@app.route('/api/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    m = MZone(username, password, env_cfg["mzone_secret"], "mz-a3tek")
    m.gettoken()
    res = dict()
    if m.check_token():
        res = m.current_user()
        res["token"] = m.get_token()
        res["perfil"] = json.loads(res["phoneHome"])["perfil"]
    return res

#deprecated
@app.route('/api/users/<path:id>', methods=['PATCH'])
def update_user(user):
    m = MZone(config["dev"]["mzone_user"], config["dev"]["mzone_pass"], config["dev"]["mzone_secret"], "mz-a3tek")
    m.gettoken()
    res = m.update_user(user)
    return json.dumps(res)


#deprecated
@app.route('/api/uploadTrips', methods=["POST"])
def uploadTrips():
    file = request.files['file']
    file.save('file.xslx')
    print("ok")
    #excel_data = ExcelFile(StringIO(file.read()))
    #df = excel_data.parse(excel_data.sheet_names[-1])
    #print(df)


@app.route('/api/calc_trip', methods=['POST'])
def calc_trip():
    trip = request.json["viaje"]
    role = json.loads(request.json["role"])
    tumsa = Tumsa(dbhost=env_cfg["dbhost"], dbuser=db_user, dbpass=db_pass, dbname=env_cfg["dbname"])
    start_date = Utils.format_date(Utils.string_to_date(str(trip["start_date"]).split('.')[0], "%Y-%m-%dT%H:%M:%S"),"%Y-%m-%d")
    calcs = tumsa.calc_trip(trip["route"], start_date, role)
    return calcs


@app.route('/api/dailyreport', methods=['POST'])
def dailyreport():
    pdf = HTML2PDF()
    tumsa = Tumsa(dbhost=env_cfg["dbhost"], dbuser=db_user, dbpass=db_pass, dbname=env_cfg["dbname"])
    today = Utils.format_date(Utils.datetime_zone(datetime.datetime.now(), "America/Mexico_City"), '%Y-%m-%d')
    route = request.json["route"]
    token = request.json["token"]
    viajes = []
    m = MZone()

    delay = 1
    pages = 1
    m.set_token(token)

    user = m.current_user()
    perfil = json.loads(user["phoneHome"])["perfil"]
    vehicles = [v['id'] for v in m.get_vehicles()]
    trips = tumsa.get_day_trips(today, route)

    if perfil != "admin":
        viajes = list(filter(lambda d: d['vehicle']["id"] in vehicles, trips))
    else:
        viajes = trips

    if len(viajes) > 0:
        pages = len(viajes)
        for viaje in viajes:
            delay = int(viaje["delay"])
            start_date = Utils.format_date(Utils.string_to_date(viaje["start_date"], "%Y-%m-%d %H:%M:%S")
                                           - timedelta(hours=UTC) - timedelta(minutes=40), "%Y-%m-%dT%H:%M:%S") + "Z"
            end_date = Utils.format_date(Utils.string_to_date(viaje["end_date"], "%Y-%m-%d %H:%M:%S")
                                         + timedelta(hours=UTC) + timedelta(minutes=40), "%Y-%m-%dT%H:%M:%S") + "Z"

            m.set_token(token)
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
                    calc["estimated_hour"] = Utils.format_date(Utils.string_to_date(place["hour"], "%Y-%m-%d %H:%M:%S"),
                                                               "%H:%M")
                    start_date = Utils.format_date(Utils.string_to_date(place["hour"], "%Y-%m-%d %H:%M:%S")
                                                   + timedelta(hours=UTC) - timedelta(minutes=30),
                                                   "%Y-%m-%dT%H:%M:%S") + "Z"
                    end_date = Utils.format_date(Utils.string_to_date(place["hour"], "%Y-%m-%d %H:%M:%S")
                                                 + timedelta(hours=UTC) + timedelta(minutes=30),
                                                 "%Y-%m-%dT%H:%M:%S") + "Z"

                    row = df[df["place_Id"] == calc["place_Id"]]
                    row2 = row[row["entryUtcTimestamp"] >= start_date]
                    fence = row2[row2["entryUtcTimestamp"] <= end_date].iloc[-1:].to_dict(orient='records')
                    if len(fence) > 0:
                        real = Utils.string_to_date(fence[0]["entryUtcTimestamp"], "%Y-%m-%dT%H:%M:%SZ") - timedelta(
                            hours=UTC)
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

            col_width = epw / (len(head) + 1)
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

            pdf.set_font('Arial', '', 7)
            pdf.ln(2 * th)
            th = pdf.font_size

            total_adelanto = 0
            total_retraso = 0
            for vuelta in all:
                atraso = 0
                adelanto = 0
                pos = -1
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
                        pdf.cell(col_width / 2, 2 * th, point["estimated_hour"], border=1, align='C')
                        if point["color"] == "red":
                            pdf.set_text_color(255, 0, 0)
                        elif point["color"] == "blue":
                            pdf.set_text_color(0, 0, 255)
                        pdf.cell(col_width / 2, 2 * th, " " + point["real_hour"] + "(" + str(point["delay"]) + ")",
                                 border=1, align='C')
                    else:
                        pdf.cell(col_width / 2, 2 * th, point["estimated_hour"], border=1, align='C')
                        pdf.cell(col_width / 2, 2 * th, "S/CHK", border=1, align='C')
                total_adelanto = total_adelanto + adelanto
                total_retraso = total_retraso + atraso
                pdf.set_text_color(0, 0, 255)
                pdf.cell(col_width_f, 2 * th, str(adelanto), border=1, align='C')
                pdf.set_text_color(255, 0, 0)
                pdf.cell(col_width_f, 2 * th, str(atraso), border=1, align='C')
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

    else:
        today = Utils.format_date(datetime.now())
        pdf.set_data(route="NO HAY VIAJES HOY", vehicle="NO HAY UNIDADES", start_date=today, tolerancia=1)
        pdf.add_page(orientation='L')

    pdf.output('daily.pdf')
    pdf2 = open("daily.pdf")
    response = Response(pdf2.read(), mimetype="application/pdf", headers={"Content-disposition": "attachment; filename=ReporteDiario.pdf"})
    pdf2.close()
    os.remove("daily.pdf")
    return response


@app.route('/api/dayreport', methods=['POST'])
def dayreport():
    pdf = HTML2PDF()
    tumsa = Tumsa(dbhost=env_cfg["dbhost"], dbuser=db_user, dbpass=db_pass, dbname=env_cfg["dbname"])
    day = request.json["date"]
    route = request.json["route"]
    viajes = []
    m = MZone()
    token = request.json["token"]
    m.set_token(token)
    user = m.current_user()
    perfil = json.loads(user["phoneHome"])["perfil"]
    vehicles = [v['id'] for v in m.get_vehicles()]
    trips = tumsa.get_day_trips(day, route=route)
    if perfil != "admin":
        viajes = list(filter(lambda d: d['vehicle']["id"] in vehicles, trips))
    else:
        viajes = trips
        
    pages = len(viajes)
    for viaje in viajes:
        delay = int(viaje["delay"])
        start_date = Utils.format_date(Utils.string_to_date(viaje["start_date"], "%Y-%m-%d %H:%M:%S")
                                       - timedelta(hours=UTC) - timedelta(minutes=40), "%Y-%m-%dT%H:%M:%S") + "Z"
        end_date = Utils.format_date(Utils.string_to_date(viaje["end_date"], "%Y-%m-%d %H:%M:%S")
                                     + timedelta(hours=UTC) + timedelta(minutes=40), "%Y-%m-%dT%H:%M:%S") + "Z"

        m.set_token(token)
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
                calc["estimated_hour"] = Utils.format_date(Utils.string_to_date(place["hour"], "%Y-%m-%d %H:%M:%S"),
                                                           "%H:%M")
                start_date = Utils.format_date(Utils.string_to_date(place["hour"], "%Y-%m-%d %H:%M:%S")
                                               + timedelta(hours=UTC) - timedelta(minutes=30), "%Y-%m-%dT%H:%M:%S") + "Z"
                end_date = Utils.format_date(Utils.string_to_date(place["hour"], "%Y-%m-%d %H:%M:%S")
                                             + timedelta(hours=UTC) + timedelta(minutes=30), "%Y-%m-%dT%H:%M:%S") + "Z"

                row = df[df["place_Id"] == calc["place_Id"]]
                row2 = row[row["entryUtcTimestamp"] >= start_date]
                fence = row2[row2["entryUtcTimestamp"] <= end_date].iloc[-1:].to_dict(orient='records')
                if len(fence) > 0:
                    real = Utils.string_to_date(fence[0]["entryUtcTimestamp"], "%Y-%m-%dT%H:%M:%SZ") - timedelta(
                        hours=UTC)
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

        col_width = epw / (len(head) + 1)
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

        pdf.set_font('Arial', '', 7)
        pdf.ln(2 * th)
        th = pdf.font_size

        total_adelanto = 0
        total_retraso = 0
        for vuelta in all:
            atraso = 0
            adelanto = 0
            pos = -1
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
                    pdf.cell(col_width / 2, 2 * th, point["estimated_hour"], border=1, align='C')
                    if point["color"] == "red":
                        pdf.set_text_color(255, 0, 0)
                    elif point["color"] == "blue":
                        pdf.set_text_color(0, 0, 255)
                    pdf.cell(col_width / 2, 2 * th, " " + point["real_hour"] + "(" + str(point["delay"]) + ")",
                             border=1, align='C')
                else:
                    pdf.cell(col_width / 2, 2 * th, point["estimated_hour"], border=1, align='C')
                    pdf.cell(col_width / 2, 2 * th, "S/CHK", border=1, align='C')
            total_adelanto = total_adelanto + adelanto
            total_retraso = total_retraso + atraso
            pdf.set_text_color(0, 0, 255)
            pdf.cell(col_width_f, 2 * th, str(adelanto), border=1, align='C')
            pdf.set_text_color(255, 0, 0)
            pdf.cell(col_width_f, 2 * th, str(atraso), border=1, align='C')
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

    pdf.output(day+'.pdf')
    pdf2 = open(day+'.pdf')
    response = Response(pdf2.read(), mimetype="application/pdf", headers={"Content-disposition": "attachment; filename="+day+'.pdf'})
    pdf2.close()
    os.remove(day+'.pdf')
    return response


@app.route('/api/tripreport', methods=['POST'])
def trip_report():
    pdf = HTML2PDF()
    try:
        m = MZone()
        token = request.json["token"]
        tumsa = Tumsa(dbhost=env_cfg["dbhost"], dbuser=db_user, dbpass=db_pass, dbname=env_cfg["dbname"])
        viaje = tumsa.get_viaje(request.json["viaje"])[0]
        delay = int(viaje["delay"])
        start_date = Utils.format_date(Utils.string_to_date(viaje["start_date"], "%Y-%m-%d %H:%M:%S")
                                       - timedelta(hours=UTC) - timedelta(minutes=40) , "%Y-%m-%dT%H:%M:%S")+"Z"
        end_date = Utils.format_date(Utils.string_to_date(viaje["end_date"], "%Y-%m-%d %H:%M:%S")
                                     + timedelta(hours=UTC) + timedelta(minutes=40), "%Y-%m-%dT%H:%M:%S")+"Z"

        m.set_token(token)
        pdf.set_data(route=viaje["route"]["name"], vehicle=viaje["vehicle"]["description"], start_date=viaje["start_date"],
                     tolerancia=delay, total_pages=1)
        pdf.add_page(orientation='L')
        epw = pdf.w - 2 * pdf.l_margin

        print("vehicle_Id eq "+viaje["vehicle"]["id"]+" and entryUtcTimestamp gt "+
              start_date+" and entryUtcTimestamp lt "+end_date)

        fences = m.get_geofences(extra="vehicle_Id eq "+viaje["vehicle"]["id"]+" and entryUtcTimestamp gt "+start_date+
                                       " and entryUtcTimestamp lt "+end_date, orderby="entryUtcTimestamp asc")

        df = pd.DataFrame(fences)
        all = [[] for i in range(0, viaje["rounds"])]
        head = []

        for he in viaje["route"]["points"]["places"]:
            head.append(he["description"])

        trips = []
        print(viaje["nid"])
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
                calc["estimated_hour"] = Utils.format_date(Utils.string_to_date(place["hour"], "%Y-%m-%d %H:%M:%S"), "%H:%M")
                start_date = Utils.format_date(Utils.string_to_date(place["hour"], "%Y-%m-%d %H:%M:%S")
                                               + timedelta(hours=UTC) - timedelta(minutes=30), "%Y-%m-%dT%H:%M:%S") + "Z"
                end_date = Utils.format_date(Utils.string_to_date(place["hour"], "%Y-%m-%d %H:%M:%S")
                                             + timedelta(hours=UTC) + timedelta(minutes=30), "%Y-%m-%dT%H:%M:%S") + "Z"

                row = df[df["place_Id"] == calc["place_Id"]]
                row2 = row[row["entryUtcTimestamp"] >= start_date]
                fence = row2[row2["entryUtcTimestamp"] <= end_date].iloc[-1:].to_dict(orient='records')
                if len(fence) > 0:
                    real = Utils.string_to_date(fence[0]["entryUtcTimestamp"], "%Y-%m-%dT%H:%M:%SZ") - timedelta(hours=UTC)
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
            all[int(place["round"])-1].append(calc)


        col_width = epw / (len(head) + 1)
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

        pdf.set_font('Arial', '', 7)
        pdf.ln(2 * th)
        th = pdf.font_size

        total_adelanto = 0
        total_retraso = 0
        for vuelta in all:
            atraso = 0
            adelanto = 0
            pos = -1
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
                    pdf.cell(col_width/2, 2*th, point["estimated_hour"], border=1, align='C')
                    if point["color"] == "red":
                        pdf.set_text_color(255, 0, 0)
                    elif point["color"] == "blue":
                        pdf.set_text_color(0, 0, 255)
                    pdf.cell(col_width/2, 2*th, " "+point["real_hour"] + "(" + str(point["delay"]) + ")", border=1, align='C')
                else:
                    pdf.cell(col_width/2, 2 * th, point["estimated_hour"], border=1, align='C')
                    pdf.cell(col_width/2, 2 * th, "S/CHK", border=1, align='C')
            total_adelanto = total_adelanto + adelanto
            total_retraso = total_retraso + atraso
            pdf.set_text_color(0, 0, 255)
            pdf.cell(col_width_f, 2 * th, str(adelanto), border=1, align='C')
            pdf.set_text_color(255, 0, 0)
            pdf.cell(col_width_f, 2 * th, str(atraso), border=1, align='C')
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
        pdf.output('out.pdf')
    except Exception as e:
        print("Problem here creating the pdf")
        print(e)
        pdf.output('out.pdf')
    finally:
        pdf2 = open("out.pdf")
        response = Response(pdf2.read(), mimetype="application/pdf", headers={"Content-disposition": "attachment; filename=report.pdf"})
        pdf2.close()
        os.remove("out.pdf")
    return response


def convert_template(template, **kwargs):
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template(template)
    rend = template.render(**kwargs)
    return rend


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888)
