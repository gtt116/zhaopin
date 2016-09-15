import influxdb


class InfluxDB(object):

    def __init__(self, dbname):

        host = 'localhost'
        port = 8086
        user = 'root'
        password = 'root'

        self.dbname = dbname
        self.db = influxdb.InfluxDBClient(host, port, user, password, dbname)
        self.db.create_database(dbname)

    def write_point(self, site, position, number, time=None):
        datapoint = {
            "measurement": "number",
            "tags": {
                "from": site,
                "position": position,
            },
            "fields": {
                "value": int(number),
            }
        }
        if time:
            datapoint['time'] = time
        assert self.db.write_points([datapoint])
