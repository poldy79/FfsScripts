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
    return (0,0)
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

def getSegmentCached(plz):
    (lat,lon) = getCenterOfPlzCached(plz)
    try:
        with open("plz_segments.json","rb") as fp:
            plz_segments = json.load(fp)
    except:
        plz_segments = {}
    if str(plz) not in plz_segments:
        print "Not in segment cache found"
        region = georeference.getRegion(lat,lon)
        plz_segments[plz] = region[1]
        segment = region[1]
        with open("plz_segments.json","wb") as fp:
            json.dump(plz_segments,fp)
    else:
        segment = plz_segments[str(plz)]
    return segment

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Calculate Segment based on PLZ')
    parser.add_argument('--plz', dest='plz', action='store',type=int, required=True, help='Input file')
    parser.add_argument('--count', dest='count', action='store',type=int, required=False, help='Count this many up')
    args = parser.parse_args()

    if args.count != None:
        count = args.count
    else:
        count = 1
    plz = args.plz
    for plz in range(plz,plz+count):
        (lat,lon) = getCenterOfPlzCached(plz)
        #print "%i is @ %f %f"%(plz,lat,lon)
        #region = georeference.getRegion(lat,lon)
        segment = getSegmentCached(plz)
        #print "PLZ %i is in Region %s which belongs to Segment %s"%(plz,region[0],region[1])
        print "PLZ %i is in Segment %s"%(plz,segment)

