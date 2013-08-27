#Copyright (c) 2011-2012, Shankar Giri V All rights reserved.
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
from imposm.parser import OSMParser

class OSMAirportDataExtractor(object):
    def __init__(self, icao='', file=''):
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
        self.lstHangarRefs = []
        self.lstHangars = []
        self.lstBldgRefs = []
        self.lstBldgs = []
        self.lstFenceRefs = []
        self.lstFences = []
        self.lstBeacons = []
        self.lstPapi = []
        self.file = file
        self.ExtractData()
        
    def coords(self, coords):
        for osm_id, lat, lon in coords:
            self.lstCoords.append((osm_id, lat, lon))
        
    def nodes(self, nodes):
        for osm_id, tags, position in nodes:
            if 'man_made' in tags:
                for subtags in tags:
                    if tags[subtags] == 'beacon':
                        (lon, lat) = position
                        self.lstBeacons.append((lat, lon))
            if 'aeroway' in tags:
                for subtags in tags:
                    if tags[subtags] == 'papi':
                        (lon, lat) = position
                        self.lstPapi.append((lat, lon))
            #print '%s %.4f %.4f' % (osm_id, lon, lat)
            #self.coords_list.append(Coords(osm_id, lon, lat))

    def ways(self, ways):
        # callback method for ways
        for osmid, tags, refs in ways:
            if 'icao' in tags:
                if tags['icao'] != self.icao:
                    sys.exit("ICAO code in OSM data different from requested Airport!!!")
            if 'building' in tags:
                if 'aeroway' not in tags or ((tags['aeroway'] != 'terminal') and (tags['aeroway'] != 'hangar')):
                    self.lstBldgRefs.append(refs)
            if 'barrier' in tags:
                for subtags in tags:
                    if tags[subtags] == 'fence':
                        self.lstFenceRefs.append(refs)
            if 'aeroway' in tags:
                for subtags in tags:
                    if tags[subtags] == 'aerodrome':
                        self.lstBoundaryRefs.append(refs)
                    if tags[subtags] == 'runway':
                        runwayName = re.split('/', tags['name'])
                        runwayRefs = (runwayName[0], refs[0], runwayName[1], refs[-1])
                        self.lstRunwayRefs.append(runwayRefs)
                    if tags[subtags] == 'taxiway':
                        self.lstTaxiwayRefs.append((osmid, refs))
                    if tags[subtags] == 'apron':
                        self.lstApronRefs.append(refs)
                    if tags[subtags] == 'terminal':
                        self.lstTerminalRefs.append(refs)
                    if tags[subtags] == 'hangar':
                        self.lstHangarRefs.append(refs)
                        
    def CoordsFromRef(self, ref):
        return [(lon, lat) for osmid, lat, lon in self.lstCoords if osmid == ref][0]
        
        
    def GetRunwayPos(self, runwayNumber, tuple = 0):
        lat, lon = (0, 0)
        runwaySuffix = ''
        found = 0
        for tup in self.lstRunwayRefs:
            lenum, ref, henum, ref1 = tup
            if lenum.endswith('L') or lenum.endswith('C') or lenum.endswith('R'):
                runwayNum = int(lenum[:-1])
                runwaySuffix = lenum[-1]
            else:
                runwayNum = int(lenum)
            strRunway = "%02d%s" % (runwayNum, runwaySuffix)
            if strRunway == runwayNumber:
                lat, lon = self.CoordsFromRef(ref)
                found = 1
                break
        if found != 1:
            for tup in self.lstRunwayRefs:
                lenum, ref, henum, ref1 = tup
                if henum.endswith('L') or henum.endswith('C') or henum.endswith('R'):
                    runwayNum = int(henum[:-1])
                    runwaySuffix = henum[-1]
                else:
                    runwayNum = int(henum)
                strRunway1 = "%02d%s" % (runwayNum, runwaySuffix)
                if strRunway1 == runwayNumber:
                    lat, lon = self.CoordsFromRef(ref1)
                    break
        if tuple == 1:
            return(float(lat), float(lon))
        else:
            return("%.8f %013.8f" % (float(lat), float(lon)))
        
    def GetLeRunwayPosTuple(self, runwayNumber):
        lat, lon = (0, 0)
        runwaySuffix = ''
        for tup in self.lstRunwayRefs:
            lenum, ref, henum, ref1 = tup
            if lenum.endswith('L') or lenum.endswith('C') or lenum.endswith('R'):
                runwayNum = int(lenum[:-1])
                runwaySuffix = lenum[-1]
            strRunway = "%02d%s" % (runwayNum, runwaySuffix)
            print "GetLeRunwayPosTuple", strRunway, runwayNumber
            if strRunway == runwayNumber:
                lat, lon = self.CoordsFromRef(ref)
                break
        return(float(lat), float(lon))
        
    def GetLeRunwayPos(self, runwayNumber):
        lat, lon = (0, 0)
        runwaySuffix = ''
        for tup in self.lstRunwayRefs:
            lenum, ref, henum, ref1 = tup
            if lenum.endswith('L') or lenum.endswith('C') or lenum.endswith('R'):
                runwayNum = int(lenum[:-1])
                runwaySuffix = lenum[-1]
            strRunway = "%02d%s" % (runwayNum, runwaySuffix)
            if strRunway == runwayNumber:
                lat, lon = self.CoordsFromRef(ref)
                break
        return("%.8f %013.8f" % (float(lat), float(lon)))
        
    def GetHeRunwayPosTuple(self, runwayNumber):
        lat, lon = (0, 0)
        runwaySuffix = ''
        for tup in self.lstRunwayRefs:
            lenum, ref, henum, ref1 = tup
            if henum.endswith('L') or henum.endswith('C') or henum.endswith('R'):
                runwayNum = int(henum[:-1])
                runwaySuffix = henum[-1]
            strRunway = "%02d%s" % (runwayNum, runwaySuffix)
            if strRunway == runwayNumber:
                lat, lon = self.CoordsFromRef(ref1)
                break
        return(float(lat), float(lon))
        
    def GetHeRunwayPos(self, runwayNumber):
        lat, lon = (0, 0)
        runwaySuffix = ''
        for tup in self.lstRunwayRefs:
            lenum, ref, henum, ref1 = tup
            if henum.endswith('L') or henum.endswith('C') or henum.endswith('R'):
                runwayNum = int(henum[:-1])
                runwaySuffix = henum[-1]
            strRunway = "%02d%s" % (runwayNum, runwaySuffix)
            print "GetHeRunwayPos", strRunway, runwayNumber
            if strRunway == runwayNumber:
                lat, lon = self.CoordsFromRef(ref1)
                break
        return("%.8f %013.8f" % (float(lat), float(lon)))
        
    def ExtractData(self):
        runway = dict()
        p = OSMParser(concurrency=4, coords_callback=self.coords, ways_callback=self.ways,  nodes_callback=self.nodes)
        print "Attempting to read %s..." % self.file
        try:
            p.parse(self.file)
        except IOError:
            print("Failed!!! File not found.")
            sys.exit(0)
        print "Done.\nExtracting Boundary co-ordinates..."
        for ref in self.lstBoundaryRefs[0]:
            self.lstBoundaries.append(self.CoordsFromRef(ref))
        print "Done. \nExtracting Runways..."
        for ref in self.lstRunwayRefs:
            (name, pos, name1, pos1) = ref
            runway['le_ident'] = name
            runway['le_pos'] = self.CoordsFromRef(pos)
            runway['he_ident'] = name1
            runway['he_pos'] = self.CoordsFromRef(pos1)
            self.lstRunways.append(copy.deepcopy(runway))
        print "Done.\nExtracting Aprons and paved surfaces"
        for aprons in self.lstApronRefs:
            lsttmp = []
            for apron in aprons:
                lsttmp.append(self.CoordsFromRef(apron))
            self.lstAprons.append(copy.deepcopy(lsttmp))
        for taxiways in self.lstTaxiwayRefs:
            lsttmp = []
            id, refs = taxiways
            for taxiway in refs:
                if taxiway == None: continue
                coord = self.CoordsFromRef(taxiway)
                lsttmp.append((id, coord))
            self.lstTaxiways.append(copy.deepcopy(lsttmp))
        for terminal in self.lstTerminalRefs:
            lsttmp = []
            for ref in terminal:
                coord = self.CoordsFromRef(ref)
                lsttmp.append(coord)
            self.lstTerminals.append(copy.deepcopy(lsttmp))
        for hangar in self.lstHangarRefs:
            lsttmp = []
            for ref in hangar:
                coord = self.CoordsFromRef(ref)
                lsttmp.append(coord)
            self.lstHangars.append(copy.deepcopy(lsttmp))
        for bldg in self.lstBldgRefs:
            lsttmp = []
            for ref in bldg:
                coord = self.CoordsFromRef(ref)
                lsttmp.append(coord)
            self.lstBldgs.append(copy.deepcopy(lsttmp))
        for fence in self.lstFenceRefs:
            lsttmp = []
            for ref in fence:
                coord = self.CoordsFromRef(ref)
                lsttmp.append(coord)
            self.lstFences.append(copy.deepcopy(lsttmp))

