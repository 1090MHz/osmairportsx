#Copyright (c) 2013, Shankar Giri V All rights reserved.
#
#Redistribution and use in source and binary forms, with or without
#modification, are permitted provided that the following conditions are met:
#
#Redistributions of source code must retain the above copyright notice, this
#list of conditions and the following disclaimer. Redistributions in binary form
#must reproduce the above copyright notice, this list of conditions and the
#following disclaimer in the documentation and/or other materials provided with
#the distribution. THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
#CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
#PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
#CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
#EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT
#OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
#INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
#CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
#IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY
#OF SUCH DAMAGE.

#!/usr/bin/env python
import copy
import re
import sys
import math
from lxml import etree
import utm as UTM
import re
from shapely import affinity
from shapely.geometry import Polygon, LineString

class OSMAirportDataExtractor(object):
    def __init__(self, icao='', file='', ourairportsdata = None):
        print "Initializing OSMAirportDataExtractor..."
        self.icao = icao
        self.lstBoundaryRefs = []
        self.lstBoundaries = []
        self.lstCoords = []
        self.lstRunwayRefs = []
        self.lstRunways = []
        self.lstTaxiwayRefs = []
        self.lstTaxiways = []
        self.lstApronRefs = []
        self.lstAprons = []
        self.lstTerminalRefs = []
        self.lstTerminals = []
        self.lstGates = []
        self.lstHangarRefs = []
        self.lstHangars = []
        self.lstHoldingRefs = []
        self.lstHoldings = []
        self.lstBldgRefs = []
        self.lstBldgs = []
        self.lstFenceRefs = []
        self.lstFences = []
        self.lstTowerRefs = []
        self.lstTowers = []
        self.lstParkingRefs = []
        self.lstParkings = []
        self.lstServiceRoadRefs = []
        self.lstServiceRoads = []
        self.lstBeacons = []
        self.lstPapi = []
        self.lstWindsocks = []
        self.use_itm = True
        self.lstZones = []
        self.file = file
        self.OurAirportsData = ourairportsdata

    def coords(self, osmfile):
        context = etree.iterparse(osmfile, events=('end',), tag='node')
        for event, elem in context:
            osm_id=elem.attrib['id']
            lat=float(elem.attrib['lat'])
            lon=float(elem.attrib['lon'])

            if self.use_itm:
              utm = UTM.from_latlon(lat,lon)
              self.lstZones.append(utm[2:])
              self.lstCoords.append((osm_id, utm[0], utm[1]))
            else:
              self.lstCoords.append((osm_id, lon, lat))

    def nodes(self, osmfile):
        context = etree.iterparse(osmfile, events=('end',), tag='node')
        for event, elem in context:
            osm_id=elem.attrib['id']
            lat=float(elem.attrib['lat'])
            lon=float(elem.attrib['lon'])

            if self.use_itm:
              utm = UTM.from_latlon(lat,lon)
              self.lstZones.append(utm[2:])
              lon = utm[0]
              lat = utm[1]

            for c in elem:
                if c.tag == 'tag':
                    if c.attrib['k'] == 'aeroway':
                        if c.attrib['v'] == 'gate':
                            ref = ''
                            for nodes in c.getparent():
                                if nodes.tag == 'tag':
                                    if nodes.attrib['k'] == 'ref':
                                        ref = nodes.attrib['v'] 
                            self.lstGates.append((ref, (lon, lat)))
                        elif c.attrib['v'] == 'papi':
                            self.lstPapi.append((lon, lat))
                        elif c.attrib['v'] == 'windsock':
                            self.lstWindsocks.append((lon, lat))
                    elif c.attrib['k'] == 'man_made':
                        if c.attrib['v'] == 'beacon':
                            self.lstBeacons.append((lon, lat))
                        elif c.attrib['v'] == 'tower':
                            self.lstTowers.append((lon, lat))

    def ways(self, osmfile):
        retVal = 0
        context = etree.iterparse(osmfile, events=('end',), tag='way', encoding='utf-8')
        for event, elem in context:
            osmid=elem.attrib['id']    
            for c in elem:
                if c.tag == 'tag':
                    ref = ''
                    type = ''
                    name = ''
                    surface = ''
                    aeroway = 0
                    refs=[]
                    if c.attrib['k'] == 'icao':
                        if c.attrib['v'] != self.icao:
                            sys.exit("ICAO code in OSM data different from requested Airport!!!")
                    elif (c.attrib['k'] == 'highway') and ((c.attrib['v'] == 'service') or (c.attrib['v'] == 'tertiary')):
                        refs = []
                        for nodes in c.getparent():
                            if nodes.tag == 'tag':
                                if nodes.attrib['k'] == 'name':
                                    name = nodes.attrib['v']
                                elif nodes.attrib['k'] == 'surface':
                                    surface = nodes.attrib['v']
                            if nodes.tag == 'nd':
                                refs.append(nodes.attrib['ref'])
                        self.lstServiceRoadRefs.append((osmid, name, surface, refs))
                    elif c.attrib['k'] == 'aeroway':
                        aeroway = 1
                        type = c.attrib['v']
                        refs = []
                        area = ''
                        for nodes in c.getparent():
                            if nodes.tag == 'tag':
                                if nodes.attrib['k'] == 'ref':
                                    ref = nodes.attrib['v']
                                if nodes.attrib['k'] == 'name':
                                    name = nodes.attrib['v']
                                if nodes.attrib['k'] == 'surface':
                                    surface = nodes.attrib['v']
                                if nodes.attrib['k'] == 'area':
                                    area = nodes.attrib['v']
                            if nodes.tag == 'nd':
                                refs.append(nodes.attrib['ref'])
                        if type == 'aerodrome': self.lstBoundaryRefs.append(refs)
                        elif type == 'runway':
                            result = re.match('([0-3]*[0-9][lrLR]?).*?([0-3]*[0-9][lrLR]?).*', ref)
                            if result:
                                runwayName = [result.group(1).upper(), result.group(2).upper()]
                            else:
                                result = re.match('([0-3]*[0-9][lrLR]?).*?([0-3]*[0-9][lrLR]?).*', name)
                                if result:
                                    runwayName = [result.group(1).upper(), result.group(2).upper()]
                            if not result:
                                if refs:
                                    runwayName = self.FindRunwayName((refs[0], refs[-1]))
                                else:
                                    retVal = -1
                            if refs:
                                if area == 'yes':
                                    minarea = 0
                                    coords = []
                                    for ref in refs:
                                        coords.append(self.CoordsFromRef(ref))
                                    runwayP = Polygon(coords)
                                    final_rect = None
                                    for angle in range(0, 180):
                                        envel = affinity.rotate(runwayP, angle)
                                        envel = runwayP.envelope
                                        if minarea == 0: 
                                            minarea = envel.area
                                            final_rect = envel
                                            ang = angle
                                        elif minarea > envel.area: 
                                            minarea = envel.area 
                                            final_rect = envel
                                            ang = angle
                                    final_rect = affinity.rotate(runwayP, -ang)
                                    if not final_rect.exterior.is_ccw:
                                        coords = final_rect.exterior.coords[::-1]
                                    else:
                                        coords = final_rect.exterior.coords[:]
                                    ls = LineString([coords[0], coords[1]])
                                    ls1 = LineString([coords[0], coords[-1]])
                                    if ls.length > ls1.length:
                                        x1, y1 = coords[0]
                                        x2, y2 = coords[-1]
                                        p1 = ((x1+x2)/2, (y1+y2)/2)
                                        x1, y1 = coords[1]
                                        x2, y2 = coords[2]
                                        p2 = ((x1+x2)/2, (y1+y2)/2)
                                    else:
                                        x1, y1 = coords[0]
                                        x2, y2 = coords[1]
                                        p1 = ((x1+x2)/2, (y1+y2)/2)
                                        x1, y1 = coords[2]
                                        x2, y2 = coords[3]
                                        p2 = ((x1+x2)/2, (y1+y2)/2)
                                    print p1, p2
                                runwayRefs = (runwayName[0].strip(), refs[0], runwayName[1].strip(), refs[-1])
                                self.lstRunwayRefs.append((surface, runwayRefs))
                        elif type == 'taxiway': self.lstTaxiwayRefs.append((osmid, ref, name, surface, refs))
                        elif type == 'apron': self.lstApronRefs.append((osmid, ref, name, surface, refs))
                        elif type == 'terminal': self.lstTerminalRefs.append(refs)
                        elif type == 'hangar': self.lstHangarRefs.append(refs)
                        elif type == 'holding_position': self.lstHoldingRefs.append(refs)
                    elif (c.attrib['k'] == 'building') and (aeroway == 0):
                        refs = []
                        for nodes in c.getparent():
                            if nodes.tag == 'nd':
                                refs.append(nodes.attrib['ref'])
                        self.lstBldgRefs.append(refs)
                    elif (c.attrib['k'] == 'barrier') and (c.attrib['v'] == 'fence'):
                        refs = []
                        for nodes in c.getparent():
                            if nodes.tag == 'nd':
                                refs.append(nodes.attrib['ref'])
                        self.lstFenceRefs.append(refs)
                    elif (c.attrib['k'] == 'amenity') and (c.attrib['v'] == 'parking'):
                        refs = []
                        for nodes in c.getparent():
                            if nodes.tag == 'nd':
                                refs.append(nodes.attrib['ref'])
                        self.lstParkingRefs.append(refs)
            elem.clear()

        while elem.getprevious() is not None:
                del elem.getparent()[0]
        return retVal

    def CoordsFromRef(self, ref):
        return [(lon, lat) for osmid, lon, lat in self.lstCoords if osmid == ref][0]
        
    def GetSurfaceCode(self, surface):
        surfaceCode = 1
        if surface == 'asphalt': surfaceCode = 1
        elif surface == 'concrete': surfaceCode = 2
        elif surface == 'grass': surfaceCode = 3
        elif surface == 'dirt': surfaceCode = 4
        elif surface == 'gravel': surfaceCode = 5
        elif surface == 'fine_gravel': surfaceCode = 5
        elif surface == 'sand': surfaceCode = 12 #"""Mapping Sand to Dry lakebed in x-plane"""
        elif surface == 'water': surfaceCode = 13
        elif surface == 'ice': surfaceCode = 14
        elif surface == 'snow': surfaceCode = 14
        return (surfaceCode)
        
    def FindDistance(self, x1, y1, x2, y2):
        return math.sqrt((x2-x1)**2+(y2-y1)**2)
        
    def FindRunwayName(self, refs):
        min = 0
        name = ''
        for runway in self.OurAirportsData.lstRunways:
            (le, he) = refs
            reflon, reflat = self.OurAirportsData.GetLeRunwayPosTuple(runway)
            lelon, lelat = self.CoordsFromRef(le)
            helon, helat = self.CoordsFromRef(he)
            dist = self.FindDistance(lelon, lelat, reflon, reflat)
            dist1 = self.FindDistance(helon, helat, reflon, reflat)
            if dist1 < dist: dist = dist1
            if min == 0:
                min = dist
                name = [self.OurAirportsData.GetLeRunwayNumber(runway), self.OurAirportsData.GetHeRunwayNumber(runway)]
            elif min > dist: 
                min = dist
                name = [self.OurAirportsData.GetLeRunwayNumber(runway), self.OurAirportsData.GetHeRunwayNumber(runway)]
        return name

    def GetRunwayPos(self, runwayNumber):
        found = 0
        lon, lat = (0, 0)
        for surface, tup in self.lstRunwayRefs:
            lenum, ref, henum, ref1 = tup
            if lenum.endswith('L') or lenum.endswith('C') or lenum.endswith('R') or lenum.endswith('W'):
                runwayNum = int(lenum[:-1])
                runwaySuffix = lenum[-1]
            else:
                runwayNum = int(lenum)
                runwaySuffix = ''
            strRunway = "%02d%s" % (runwayNum, runwaySuffix)
            if strRunway == runwayNumber:
                lon, lat = self.CoordsFromRef(ref)
                found = 1
                break
        if found != 1:
            for surface, tup in self.lstRunwayRefs:
                lenum, ref, henum, ref1 = tup
                if henum.endswith('L') or henum.endswith('C') or henum.endswith('R') or henum.endswith('W'):
                    runwayNum = int(henum[:-1])
                    runwaySuffix = henum[-1]
                else:
                    runwayNum = int(henum)
                    runwaySuffix = ''
                strRunway1 = "%02d%s" % (runwayNum, runwaySuffix)
                if strRunway1 == runwayNumber:
                    lon, lat = self.CoordsFromRef(ref1)
                    found = 1
                    break
        if found != 1:
            print "Runway %s not found in OSM data!" % (runwayNumber)
        return((found, surface, (float(lon), float(lat))))

    def GetLeRunwayPosTuple(self, runwayNumber):
        lon, lat = (0, 0)
        runwaySuffix = ''
        for tup in self.lstRunwayRefs:
            lenum, ref, henum, ref1 = tup
            if lenum.endswith('L') or lenum.endswith('C') or lenum.endswith('R') or lenum.endswith('W'):
                runwayNum = int(lenum[:-1])
                runwaySuffix = lenum[-1]
            strRunway = "%02d%s" % (runwayNum, runwaySuffix)
            if strRunway == runwayNumber:
                lon, lat = self.CoordsFromRef(ref)
                break
        return(float(lon), float(lat))
        
    def GetHeRunwayPosTuple(self, runwayNumber):
        lon, lat = (0, 0)
        runwaySuffix = ''
        for tup in self.lstRunwayRefs:
            lenum, ref, henum, ref1 = tup
            if henum.endswith('L') or henum.endswith('C') or henum.endswith('R') or henum.endswith('W'):
                runwayNum = int(henum[:-1])
                runwaySuffix = henum[-1]
            else:
                runwayNum = int(henum)
                runwaySuffix = ''
            strRunway = "%02d%s" % (runwayNum, runwaySuffix)
            if strRunway == runwayNumber:
                lon, lat = self.CoordsFromRef(ref1)
                break
        return(float(lon), float(lat))

    def GetUseItm(self):
      return self.use_itm

    def GetZones(self):
      return self.lstZones

    def ExtractData(self):
        runway = dict()
        print "Attempting to read %s..." % self.file
        try:
            self.coords(self.file)
            self.nodes(self.file)
            retval = self.ways(self.file)
            if retval == -1:
                return -1
        except IOError:
            sys.exit("Failed!!! File not found.")
        print "Done.\nExtracting Boundary co-ordinates..."
        lsttmp = []
        if self.lstBoundaryRefs:
            for ref in self.lstBoundaryRefs[0]:
                self.lstBoundaries.append(self.CoordsFromRef(ref))
            print "Done."
        else:
            print "No boundaries found...moving on. Please consider adding airport boundaries in OSM"
        print "Extracting Runways..."
        for surface, ref in self.lstRunwayRefs:
            (name, pos, name1, pos1) = ref
            runway['le_ident'] = name
            runway['le_pos'] = self.CoordsFromRef(pos)
            runway['he_ident'] = name1
            runway['he_pos'] = self.CoordsFromRef(pos1)
            self.lstRunways.append((surface, copy.deepcopy(runway)))
        print "Done.\nExtracting Aprons and paved surfaces..."
        for refs in self.lstApronRefs:
            lsttmp = []
            osmid, ref, name, surface, aprons = refs
            for apron in aprons:
                lsttmp.append(self.CoordsFromRef(apron))
            self.lstAprons.append((osmid, name, surface, copy.deepcopy(lsttmp)))
        print "Done.\nExtracting Taxiway segments..."
        for refs in self.lstTaxiwayRefs:
            lsttmp = []
            osmid, ref, name, surface, taxiways = refs
            for taxiway in taxiways:
                lsttmp.append(self.CoordsFromRef(taxiway))
            if lsttmp:
              x1, y1 = lsttmp[0]
              x2, y2 = lsttmp[-1]
              dist = self.FindDistance(x1, y1, x2, y2)
              self.lstTaxiways.append((osmid, name, surface, dist, copy.deepcopy(lsttmp)))
        print "Done.\nExtracting Airport Terminals..."
        for refs in self.lstTerminalRefs:
            lsttmp = []
            for terminal in refs:
                lsttmp.append(self.CoordsFromRef(terminal))
            self.lstTerminals.append(copy.deepcopy(lsttmp))
        print "Done.\nExtracting Hangars..."
        for hangar in self.lstHangarRefs:
            lsttmp = []
            for ref in hangar:
                coord = self.CoordsFromRef(ref)
                lsttmp.append(coord)
            self.lstHangars.append(copy.deepcopy(lsttmp))
        print "Done.\nExtracting Buildings..."
        for bldg in self.lstBldgRefs:
            lsttmp = []
            for ref in bldg:
                coord = self.CoordsFromRef(ref)
                lsttmp.append(coord)
            self.lstBldgs.append(copy.deepcopy(lsttmp))
#         print "Done.\nExtracting Towers..."
#         for tower in self.lstTowerRefs:
#             lsttmp = []
#             for ref in tower:
#                 coord = self.CoordsFromRef(ref)
#                 lsttmp.append(coord)
#             self.Towers.append(copy.deepcopy(lsttmp))
        print "Done.\nExtracting Holding positions..."
        for holding in self.lstHoldingRefs:
            lsttmp = []
            for ref in holding:
                coord = self.CoordsFromRef(ref)
                lsttmp.append(coord)
            self.lstHoldings.append(copy.deepcopy(lsttmp))
        print "Done.\nExtracting Parking..."
        for bldg in self.lstParkingRefs:
            lsttmp = []
            for ref in bldg:
                coord = self.CoordsFromRef(ref)
                lsttmp.append(coord)
            self.lstParkings.append(copy.deepcopy(lsttmp))
        print "Done.\nExtracting Fence segments..."
        for fence in self.lstFenceRefs:
            lsttmp = []
            for ref in fence:
                coord = self.CoordsFromRef(ref)
                lsttmp.append(coord)
            self.lstFences.append(copy.deepcopy(lsttmp))
        print "Done.\nExtracting Service Road segments..."
        for refs in self.lstServiceRoadRefs:
            lsttmp = []
            osmid, name, surface, roads = refs
            for road in roads:
                coord = self.CoordsFromRef(road)
                lsttmp.append(coord)
            self.lstServiceRoads.append((osmid, name, surface, copy.deepcopy(lsttmp)))
        print "Number of Runways: %d" % len(self.lstRunwayRefs)
        print "Number of Aprons: %d" % len(self.lstApronRefs)
        print "Number of Terminals: %d" % len(self.lstTerminalRefs)
        print "Number of Gates: %d" % len(self.lstGates)
        print "Number of Taxiway Segments: %d" % len(self.lstTaxiwayRefs)
        print "Number of Hangars: %d" % len(self.lstHangarRefs)
        print "Number of Buildings: %d" % len(self.lstBldgRefs)
        print "Number of Towers: %d" % len(self.lstTowers)
        print "Number of Parking Areas: %d" % len(self.lstParkingRefs)
        print "Number of Fence Segments: %d" % len(self.lstFenceRefs)
        print "Number of Service Road Segments: %d" % len(self.lstServiceRoadRefs)
        print "Number of UTM zones: %d " % len(list(set(self.lstZones)))
        return 0

