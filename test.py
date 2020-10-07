from classes.tumsa import Tumsa
from PydoNovosoft.utils import Utils
import json
import re
from datetime import datetime, timedelta
from PydoNovosoft.scope import MZone

def main():
    tumsa = Tumsa(dbhost="127.0.0.1", dbuser="postgres", dbpass="admin1234", dbname="tumsadev")
    start_date = Utils.format_date(Utils.string_to_date("2020-10-04 06:33:00", "%Y-%m-%d %H:%M:%S")
                                   - timedelta(hours=5) - timedelta(minutes=40), "%Y-%m-%dT%H:%M:%S") + "Z"
    end_date = Utils.format_date(Utils.string_to_date("2020-10-04 18:21:00", "%Y-%m-%d %H:%M:%S")
                                 + timedelta(hours=5) + timedelta(minutes=40), "%Y-%m-%dT%H:%M:%S") + "Z"

    m = MZone()
    token = {
    "access_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6IkVGMUUxMkVFOTQ1NTdBNDg5MzlCMUJBNjJFQUUxQzFBN0ZDNTY2MkQiLCJ0eXAiOiJKV1QiLCJ4NXQiOiI3eDRTN3BSVmVraVRteHVtTHE0Y0duX0ZaaTAifQ.eyJuYmYiOjE2MDE5NDkxOTksImV4cCI6MTYwMTk1Mjc5OSwiaXNzIjoiaHR0cHM6Ly9sb2dpbi5tem9uZXdlYi5uZXQiLCJhdWQiOlsiaHR0cHM6Ly9sb2dpbi5tem9uZXdlYi5uZXQvcmVzb3VyY2VzIiwibXo2LWFwaSJdLCJjbGllbnRfaWQiOiJtei1hM3RlayIsInN1YiI6IjUzYTkwNjMwLTk4OTctNGNkNS05MjJiLTM1NTZhYjI5M2UzOSIsImF1dGhfdGltZSI6MTYwMTk0OTE5OSwiaWRwIjoibG9jYWwiLCJtel91c2VybmFtZSI6IlRVTVNBLUFQSSIsIm16X3VzZXJncm91cF9pZCI6IjAwMDAwMDAwLTAwMDAtMDAwMC0wMDAwLTAwMDAwMDAwMDAwMCIsIm16X3NoYXJkX2NvZGUiOiJBM1RFSyIsInNjb3BlIjpbIm16X3VzZXJuYW1lIiwib3BlbmlkIiwibXo2LWFwaS5hbGwiXSwiYW1yIjpbInB3ZCJdfQ.ZHTW-sLBNFmwqUz-eSFCvleQcoXpjbFCfGJ7Yw4-vYfUV9n4WsBootTKTDeD1usHfEQRy2SGAJPdeLVVYUP27zshmY66IirUxUHAdi7i1DAcHteMlzt4lXQ9NYbRktHOdDmAoNeZm6PE8dhfIws1_NA2YjFZOd9B8EeRi7yLcoi-4wglyZ8Z3INL7tMjruSvlqtXdWnElcGaNqkpaEGtR1AJHlUjPlUldXOKocX0KRK2ZscV22xYH94Vd0MuOWFkIei9uyHprTFP2C7Xsz9-2ZSYXC12OMbbUedhVAcJeo1I0DKO60u0fc6ZeT9w41iMH-oX0S7Ilg-dJCoKlaPxlIlumD4BzTqEvZDq_72WZFHAD_QAJn5WAI3s8ta0Y7u91V1QhOvOYA0GrVXSM0MVs8b3HHHMjXQCR74cH56tLbOwxhkFUVI5UPNGbqaTvm3HKq1CusoBlpgmVvNDJomkE6n6cFop78cmFHqETNjD-UpDLJBB0n_0mQf78pi1V2h32fz5Dr5N80qCjqBX6aa89PCeCQDCD59b_nOyadzDFppaBIlfhGViXqw_YMqllvAb84sopaRkk_7vMN1AOAfCZUI16wIB-O7p3NJLoFq-7R22xT9xs5PtGy0KsFVSzmTFCzdUyrPDlehz31FmpPImJ7TnmzISyhDgJo4e8Xvgod4",
    "expires_in": 3600,
    "token_type": "Bearer",
    "valid_until": "2020-10-05 21:53:19.472393"
    }
    m.set_token(token)
    v = m.get_vehicles()
    fences = m.get_geofences(extra="vehicle_Id eq b1772001-3173-467d-9b6c-5f97a05a4b9a and entryUtcTimestamp gt "+
                                   start_date +" and entryUtcTimestamp lt " + end_date, orderby="entryUtcTimestamp asc")
    for f in fences:
        print(f)


if __name__ == '__main__':
    main()
