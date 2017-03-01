#!/usr/bin/python
import ujson as json
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from glob import glob
import math
import matplotlib.patches as patches
import pylab
import os

#http://ra.osmsurround.org/searchRelation?name=Nordrhein-Westfalen&relationType=&route=&ref=&network=&operator=
#http://polygons.openstreetmap.fr/index.py

#http://polygons.openstreetmap.fr/get_geojson.py?id=2793104&params=0

#Relation Boundary finden:
#http://ra.osmsurround.org/searchRelation?name=Stuttgart&relationType=boundary&route=&ref=&network=&operator=

relations = { "Stuttgart": 2793104, "Boeblingen":  62721, "Esslingen": 2812851, "Rems-Murr-Kreis": 62412 , "Ludwigsburg": 62536 , "Goeppingen":  2812852, "Reutlingen": 2796980, "Heidenheim ": 2812850, "Heilbronn": 62750 ,"Ostalbkreis": 62708,"Pforzheim": 3146849, "Tuebingen": 2797036, "Schwaebisch-Hall": 62582, "Ortenaukreis": 62624, "Zollernalbkreis": 2797573, "Neckar-Odenwald-Kreis": 62626, "Calw": 62601, "Rheinland-Pfalz": 62341, "Saarland": 62372, "Alb-Donau-Kreis": 2804078 , "Bayern": 2145268 , "Bodenseekreis": 2806623, "Rottweil": 62344, "Schwarzwald-Baar-Kreis": 62690 , "Hohenlohekreis": 62394, "Nordrhein-Westfalen": 62761, "Hessen": 3997055, "Biberach": 2804156}

relations["Stuttgart-Mitte"] = 1107850
relations["Stuttgart-Nord"] = 1107840 
relations["Stuttgart-Ost"] = 1107908
relations["Stuttgart-Sued"] = 1107879
relations["Stuttgart-West"] = 1107770
relations["Stuttgart-BadCannstatt"] = 1107864
relations["Stuttgart-Birkach"] = 1107931
relations["Stuttgart-Botnang"] = 1107904
relations["Stuttgart-Degerloch"] = 1107796
relations["Stuttgart-Feuerbach"] = 1107785
relations["Stuttgart-Hedelfingen"] = 1107853
relations["Stuttgart-Moehringen"] = 1107824
relations["Stuttgart-Muehlhausen"] = 1107892
relations["Stuttgart-Muenster"] = 1107846
relations["Stuttgart-Obertuerkheim"] = 1107914
relations["Stuttgart-Plieningen"] = 1107885
relations["Stuttgart-Sillenbuch"] = 1107777
relations["Stuttgart-Stammheim"] = 1107941
relations["Stuttgart-Untertuerkheim"] = 1107836
relations["Stuttgart-Vaihingen"] = 1107807
relations["Stuttgart-Wangen"] = 1107844
relations["Stuttgart-Weilimdorf"] = 1107829
relations["Stuttgart-Zuffenhausen"] = 1107897

for r in relations:
    if False:
        print "curl \"http://polygons.openstreetmap.fr/index.py?id=%i\" > /dev/null"%(relations[r])
	print "curl \"http://polygons.openstreetmap.fr/get_geojson.py?id=%i&params=0\" > %s.json"%(relations[r],r)
	
def displayPoly(pp):
    cent=(sum([p[0] for p in pp])/len(pp),sum([p[1] for p in pp])/len(pp))
    # sort by polar angle
    #pp.sort(key=lambda p: math.atan2(p[1]-cent[1],p[0]-cent[0]))
    # plot points
    pylab.scatter([p[0] for p in pp],[p[1] for p in pp])
    # plot polyline
    pylab.gca().add_patch(patches.Polygon(pp,closed=False,fill=False))
    pylab.grid()
    pylab.show()


polygons = {}
regions = {}



files = glob(os.path.dirname(os.path.realpath(__file__))+"/segments/*/*.json")
for filename in files:
    region = os.path.basename(filename.split(".")[0])
    segment = os.path.dirname(filename).split("/")[-1]
    with open(filename,"rb") as fp:
        geojson = json.load(fp)
    if "geometries" in geojson:
        trk = geojson["geometries"][0]["coordinates"][0][0]
    elif "coordinates" in geojson:
        trk = geojson["coordinates"][0][0]
    else:
        print "Problem parsing %s"%filename
        continue
    array = []
    for t in trk:
        array.append( (t[1],t[0]))
    polygon = Polygon(array)
    polygons[region] = polygon
    regions[region] = segment

def getRegions():
	return polygons.keys()
	
def getRegion(lat,lon):
        point= Point(lat,lon)
        result = "Outside"
        segment = "undefined"
        polygons_sorted = polygons.keys()
        polygons_sorted.sort()
        for polygon in polygons_sorted:
                if polygons[polygon].contains(point):
                    result =  polygon
                    break
        if result in regions:
            segment = regions[result]
        return (result,segment)

#print getRegion(48.78679199385324,9.189022779464722)
