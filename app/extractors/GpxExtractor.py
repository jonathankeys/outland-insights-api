import xml.etree.ElementTree as ET
from datetime import datetime
import time

class GpxExtractor:
    def __init__(self):
        pass

    @staticmethod
    def parse_iso_time(time_str):
        dt = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%SZ")
        return time.mktime(dt.timetuple())

    def extract(self, gpx_string):
        root = ET.fromstring(gpx_string)
        namespace = {'gpx': 'http://www.topografix.com/GPX/1/1'}
        points = []
        for segment in root.findall('.//gpx:trkseg', namespace):
            for point in segment.findall('gpx:trkpt', namespace):
                lon = point.get('lon')
                lat = point.get('lat')
                elev = point.find('gpx:ele', namespace).text
                time_str = point.find('gpx:time', namespace).text

                timestamp = self.parse_iso_time(time_str)
                points.append((lon, lat, elev, timestamp))
        return points