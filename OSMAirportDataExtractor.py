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
import math
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
        self.lstGates = []
        self.lstHangarRefs = []
        self.lstHangars = []
        self.lstBldgRefs = []
        self.lstBldgs = []
        self.lstFenceRefs = []
        self.lstFences = []
        self.lstServiceRoadRefs = []
        self.lstServiceRoads = []
        self.lstBeacons = []
        self.lstPapi = []
        self.file = file
        self.ExtractData()
        
    def coords(self, coords):
        for osm_id, lon, lat in coords:
            self.lstCoords.append((osm_id, lon, lat))
        
    def nodes(self, nodes):
        for osm_id, tags, position in nodes:
            if 'man_made' in tags:
                for subtags in tags:
                    if tags[subtags] == 'beacon':
                        (lon, lat) = position
                        self.lstBeacons.append((lon, lat))
            if 'aeroway' in tags:
                for subtags in tags:
                    if tags[subtags] == 'papi':
                        (lon, lat) = position
                        self.lstPapi.append((lon, lat))
                    if tags[subtags] == 'gate':
                        (lon, lat) = position
                        self.lstGates.append((lon, lat))

    def ways(self, ways):
        # callback method for ways
        for osmid, tags, refs in ways:
            if 'icao' in tags:
                if tags['icao'] != self.icao:
                    sys.exit("ICAO code in OSM data different from requested Airport!!!")
            if 'highway' in tags:
                for subtags in tags:
                    if (tags[subtags] == 'service') or (tags[subtags] == 'tertiary'):
                        if 'name' in tags:
                            name = tags['name']
                        else:
                            name = ''
                        self.lstServiceRoadRefs.append((osmid, name, refs))
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
                        if 'name' in tags:
                            runwayName = re.split('/', tags['name'])
                            runwayRefs = (runwayName[0], refs[0], runwayName[1], refs[-1])
                            self.lstRunwayRefs.append(runwayRefs)
                    if tags[subtags] == 'taxiway':
                        if 'ref' in tags:
                           name = tags['ref']
                        elif 'name' in tags:
                            name = tags['name']
                        else:
                            name = ''
                        self.lstTaxiwayRefs.append((osmid, name, refs))
                    if tags[subtags] == 'apron':
                        if 'name' in tags:
                            name = tags['name']
                        else:
                            name = ''
                        self.lstApronRefs.append((osmid, name, refs))
                    if tags[subtags] == 'terminal':
                        if 'name' in tags:
                            name = tags['name']
                        else:
                            name = ''
                        self.lstTerminalRefs.append((osmid, name, refs))
                    if tags[subtags] == 'hangar':
                        self.lstHangarRefs.append(refs)
                        
    def CoordsFromRef(self, ref):
        return [(lon, lat) for osmid, lon, lat in self.lstCoords if osmid == ref][0]
        
        
    def GetRunwayPos(self, runwayNumber):
        lon, lat = (0, 0)
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
                lon, lat = self.CoordsFromRef(ref)
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
                    lon, lat = self.CoordsFromRef(ref1)
                    found = 1
                    break
        if found != 1:
            sys.exit("Did not find runway %s in OSM or OurAirports Data!  \
                        Either or both of them may be incorrect/outdated. Correct the problem to proceed further" % runwayNumber)
        return(float(lon), float(lat))
        
    def GetLeRunwayPosTuple(self, runwayNumber):
        lon, lat = (0, 0)
        runwaySuffix = ''
        for tup in self.lstRunwayRefs:
            lenum, ref, henum, ref1 = tup
            if lenum.endswith('L') or lenum.endswith('C') or lenum.endswith('R'):
                runwayNum = int(lenum[:-1])
                runwaySuffix = lenum[-1]
            strRunway = "%02d%s" % (runwayNum, runwaySuffix)
            print "GetLeRunwayPosTuple", strRunway, runwayNumber
            if strRunway == runwayNumber:
                lon, lat = self.CoordsFromRef(ref)
                break
        return(float(lon), float(lat))
        
    def GetLeRunwayPos(self, runwayNumber):
        lon, lat = (0, 0)
        runwaySuffix = ''
        for tup in self.lstRunwayRefs:
            lenum, ref, henum, ref1 = tup
            if lenum.endswith('L') or lenum.endswith('C') or lenum.endswith('R'):
                runwayNum = int(lenum[:-1])
                runwaySuffix = lenum[-1]
            strRunway = "%02d%s" % (runwayNum, runwaySuffix)
            if strRunway == runwayNumber:
                lon, lat = self.CoordsFromRef(ref)
                break
        return("%.8f %013.8f" % (float(lon), float(lat)))
        
    def GetHeRunwayPosTuple(self, runwayNumber):
        lon, lat = (0, 0)
        runwaySuffix = ''
        for tup in self.lstRunwayRefs:
            lenum, ref, henum, ref1 = tup
            if henum.endswith('L') or henum.endswith('C') or henum.endswith('R'):
                runwayNum = int(henum[:-1])
                runwaySuffix = henum[-1]
            else:
                runwayNum = int(henum)
                runwaySuffix = ''
            strRunway = "%02d%s" % (runwayNum, runwaySuffix)
            print strRunway, runwayNumber
            if strRunway == runwayNumber:
                lon, lat = self.CoordsFromRef(ref1)
                break
        return(float(lon), float(lat))
        
    def GetHeRunwayPos(self, runwayNumber):
        lon, lat = (0, 0)
        runwaySuffix = ''
        for tup in self.lstRunwayRefs:
            lenum, ref, henum, ref1 = tup
            if henum.endswith('L') or henum.endswith('C') or henum.endswith('R'):
                runwayNum = int(henum[:-1])
                runwaySuffix = henum[-1]
            strRunway = "%02d%s" % (runwayNum, runwaySuffix)
            print "GetHeRunwayPos", strRunway, runwayNumber
            if strRunway == runwayNumber:
                lon, lat = self.CoordsFromRef(ref1)
                break
        return("%.8f %013.8f" % (float(lon), float(lat)))
        
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
        lsttmp = []
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
        print "Done.\nExtracting Aprons and paved surfaces..."
        for refs in self.lstApronRefs:
            lsttmp = []
            osmid, name, aprons = refs
            for apron in aprons:
                lsttmp.append(self.CoordsFromRef(apron))
            self.lstAprons.append((osmid, name, copy.deepcopy(lsttmp)))
        print "Done.\nExtracting Taxiway segments..."
        for refs in self.lstTaxiwayRefs:
            lsttmp = []
            osmid, name, taxiways = refs
            for taxiway in taxiways:
                lsttmp.append(self.CoordsFromRef(taxiway))
            self.lstTaxiways.append((osmid, name, copy.deepcopy(lsttmp)))
        print "Done.\nExtracting Airport Terminals..."
        for refs in self.lstTerminalRefs:
            lsttmp = []
            osmid, name, terminals = refs
            for terminal in terminals:
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
            osmid, name, roads = refs
            for road in roads:
                coord = self.CoordsFromRef(road)
                lsttmp.append(coord)
            self.lstServiceRoads.append((osmid, name, copy.deepcopy(lsttmp)))
        print "Number of Runways: %d" % len(self.lstRunwayRefs)
        print "Number of Aprons: %d" % len(self.lstApronRefs)
        print "Number of Terminals: %d" % len(self.lstTerminalRefs)
        print "Number of Gates: %d" % len(self.lstGates)
        print "Number of Taxiway Segments: %d" % len(self.lstTaxiwayRefs)
        print "Number of Hangars: %d" % len(self.lstHangarRefs)
        print "Number of Buildings: %d" % len(self.lstBldgRefs)
        print "Number of Fence Segments: %d" % len(self.lstFenceRefs)
        print "Number of Service Road Segments: %d" % len(self.lstServiceRoadRefs)

