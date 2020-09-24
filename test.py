from classes.tumsa import Tumsa
from PydoNovosoft.utils import Utils
from PydoNovosoft.scope import MZone
from datetime import datetime, timedelta
import pandas as pd

def main():
    tumsa = Tumsa(dbhost="", dbuser="postgres", dbpass="", dbname="tumsa")
    viaje = tumsa.get_viaje("4cb3fa26-cbea-4f59-a5f0-8e825a4aeed4")[0]
    print(viaje["start_date"])
    print(viaje["end_date"])
    start_date = Utils.format_date(Utils.string_to_date(viaje["start_date"], "%Y-%m-%d %H:%M:%S") - timedelta(hours=5) - timedelta(minutes=40) , "%Y-%m-%dT%H:%M:%S")+"Z"
    end_date = Utils.format_date(Utils.string_to_date(viaje["end_date"], "%Y-%m-%d %H:%M:%S") - timedelta(hours=5) + timedelta(minutes=40), "%Y-%m-%dT%H:%M:%S")+"Z"
    print(start_date)
    print(end_date)
    m = MZone()
    token = {}
    m.set_token(token)
    fences = m.get_geofences(extra="vehicle_Id eq " + viaje["vehicle"]["id"] + " and entryUtcTimestamp gt "+
                                   start_date +" and entryUtcTimestamp lt " + end_date, orderby="entryUtcTimestamp asc")
    df = pd.DataFrame(fences)
    for place in viaje["trip"]["trip"]:
        calc = {}
        calc["place_Id"] = place["id"]
        calc["description"] = place["description"]
        calc["estimated"] = place["hour"]
        calc["estimated_hour"] = Utils.format_date(Utils.string_to_date(place["hour"], "%Y-%m-%d %H:%M:%S"), "%H:%M")
        start_date = Utils.format_date(Utils.string_to_date(place["hour"], "%Y-%m-%d %H:%M:%S")
                                       + timedelta(hours=5) - timedelta(minutes=30), "%Y-%m-%dT%H:%M:%S") + "Z"
        end_date = Utils.format_date(Utils.string_to_date(place["hour"], "%Y-%m-%d %H:%M:%S")
                                     + timedelta(hours=5) + timedelta(minutes=30), "%Y-%m-%dT%H:%M:%S") + "Z"

        row = df[df["place_Id"] == calc["place_Id"]]
        row2 = row[row["entryUtcTimestamp"] >= start_date]
        fence = row2[row2["entryUtcTimestamp"] <= end_date].iloc[-1:].to_dict(orient='records')
        if len(fence) > 0:
            real = Utils.string_to_date(fence[0]["entryUtcTimestamp"], "%Y-%m-%dT%H:%M:%SZ") - timedelta(hours=5)
            estimated = Utils.string_to_date(calc["estimated"], "%Y-%m-%d %H:%M:%S")
            calc["real"] = Utils.format_date(real, "%Y-%m-%d %H:%M:%S")
            calc["real_hour"] = Utils.format_date(real, "%H:%M")
            calc["delay"] = int((estimated - real).total_seconds() / 60)
            if calc["delay"] < 0:
                calc["delay"] = calc["delay"] + 1
            calc["check"] = 1
        else:
            calc["real"] = ""
            calc["real_hour"] = ""
            calc["delay"] = 0
            calc["check"] = 0
        all[int(place["round"]) - 1].append(calc)

if __name__ == '__main__':
    main()