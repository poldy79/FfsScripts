#!/usr/bin/python
#pip install overpy
import overpy
import georeference
import argparse
import json

def getCenterOfPlz(plz):
    api = overpy.Overpass()
    query = 'rel[postal_code="%i"];out center;'%(plz)
    result = api.query(query)
    for relation in result.relations:
        return (relation.center_lat,relation.center_lon)

def getCenterOfPlzCached(plz):
    try:
        with open("plz.json","rb") as fp:
            cache = json.load(fp)
    except:
        print "JSON could not be decoded"
        cache = {}
    if str(plz) not in cache:
        print "Not found in cache"
        (lat,lon) = getCenterOfPlz(plz)
        cache[plz] = (str(lat),str(lon))
        with open("plz.json","wb") as fp:
            json.dump(cache,fp)
    else:
        (lat_f,lon_f) = cache[str(plz)]
        lat = float(lat_f)
        lon = float(lon_f)
    return (lat,lon)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Calculate Segment based on PLZ')
    parser.add_argument('--plz', dest='plz', action='store',type=int, required=True, help='Input file')
    args = parser.parse_args()


    plz = args.plz
    (lat,lon) = getCenterOfPlzCached(plz)
    #print "%i is @ %f %f"%(plz,lat,lon)
    region = georeference.getRegion(lat,lon)
    print "PLZ %i is in Region %s which belongs to Segment %s"%(plz,region[0],region[1])

