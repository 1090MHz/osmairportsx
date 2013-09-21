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
import sys
import math
import os
import shutil
import copy
import codecs
from shapely.geometry import LinearRing, LineString, Point

class XPAPTDataCreator(object):

    def __init__(self, icao='', osmfile='', centerlines=False, centerlights=False, 
                edgelines=False, edgelights=False, taxiway_width=32, taxiway_type="ASPHALT", 
                apron_type="CONCRETE", apron_perimeterlights=0, apron_floodlights=0,
                ourairportsdata=None, osmdata=None, genpath='.'):
        self.icao=icao
        self.osmfile=osmfile
        self.centerlines=centerlines
        self.centerlights=centerlights
        self.edgelines=edgelines
        self.edgelights=edgelights
        self.taxiway_width = taxiway_width
        self.taxiway_type = taxiway_type
        self.apron_type = apron_type
        self.apron_perimeterlights = apron_perimeterlights
        self.apron_floodlights = apron_floodlights
        self.lepos = 0
        self.hepos = 0
        self.lstEdgeLines = []
        print 'Initializing the XPAPTDataCreator...'
        self.OurAirportsData = ourairportsdata
        self.OSMAirportsData = osmdata
        self.hndApt = codecs.open("apt.dat", "wb", "utf-8")
        self.path = os.path.join(genpath, icao)
        self.mkdir(self.path)
        self.path = os.path.join(self.path, 'Earth Nav Data')
        self.mkdir(self.path)
        
        
    def GetSurfaceCode(self, OSMSurface, optionSurface):
        if OSMSurface == '':
            surfaceCode = optionSurface
        else:
            surfaceCode = self.OSMAirportsData.GetSurfaceCode(OSMSurface)
        return surfaceCode
        
    def WriteFileHeader(self):
        if sys.platform == 'darwin':
            plm = 'A'
        else:
            plm = 'I'
        self.hndApt.write("%s\n" % plm)
        self.hndApt.write('1000 - Generated by OSMAirports\n\n')
        
    def WriteAPTHeader(self):
        """Always assumes Land airport, for now. No support for seaplane / helipads yet"""
        elevation_ft = self.OurAirportsData.GetAirportElevationFt()
        icao = self.OurAirportsData.GetAirportICAO()
        name = self.OurAirportsData.GetAirportName()
        str = "1     %s 0 0 %s %s\n" % (elevation_ft, icao, name)
        self.hndApt.write(str)
        
    def FindAccuratePos(self, runway):
        leRunwayNumber = self.OurAirportsData.GetLeRunwayNumber(runway)
        leRunwayPos = self.OurAirportsData.GetLeRunwayPosTuple(runway)
        found, surface, leRunwayPosOSM = self.OSMAirportsData.GetRunwayPos(leRunwayNumber)
        heRunwayNumber = self.OurAirportsData.GetHeRunwayNumber(runway)
        heRunwayPos = self.OurAirportsData.GetHeRunwayPosTuple(runway)
        found, surface, heRunwayPosOSM = self.OSMAirportsData.GetRunwayPos(heRunwayNumber)
        (x1, y1) = leRunwayPos
        (x2, y2) = leRunwayPosOSM
        lePosDistance = self.FindDistance(x1, y1, x2, y2)
        (x2, y2) = heRunwayPosOSM
        hePosDistance = self.FindDistance(x1, y1, x2, y2)
        if lePosDistance > hePosDistance:
            print "OSM Co-ordinates for the runway %s/%s are swapped!\nI will swap them back in apt.dat correctly." % (leRunwayNumber, heRunwayNumber)
            print "Please consider correcting the OSM data."
            return 1
        return 0
        
    def WriteRunwayDefs(self):
        for runway in self.OurAirportsData.lstRunways:
            edgeLighting = self.OurAirportsData.GetEdgeLightingCode(runway)
            runwayWidthFt = self.OurAirportsData.GetRunwayWidthFt(runway)
            lighted = self.OurAirportsData.IsRunwayLighted(runway)
            leRunwayNumber = self.OurAirportsData.GetLeRunwayNumber(runway)
            found, surface, leRunwayPosOSM = self.OSMAirportsData.GetRunwayPos(leRunwayNumber)
            if found != 1:
                return -1
            leDisplacedThresholdFt = self.OurAirportsData.GetLeDisplacementThresholdFt(runway)
            heRunwayNumber = self.OurAirportsData.GetHeRunwayNumber(runway)
            found, surface, heRunwayPosOSM = self.OSMAirportsData.GetRunwayPos(heRunwayNumber)
            if found != 1:
                return -1
            heDisplacedThresholdFt = self.OurAirportsData.GetHeDisplacementThresholdFt(runway)
            shoulderSurface = self.OurAirportsData.GetRunwayShoulderSurface(runway)
            le_rm = self.OurAirportsData.GetLeRunwayMarkingCode(runway)
            he_rm = self.OurAirportsData.GetHeRunwayMarkingCode(runway)
            le_appr_lighting = self.OurAirportsData.GetLeApproachLightingCode(runway)
            he_appr_lighting = self.OurAirportsData.GetHeApproachLightingCode(runway)
            le_reil = self.OurAirportsData.GetLeREILCode(runway)
            he_reil = self.OurAirportsData.GetHeREILCode(runway)
            le_tdz = int(self.OurAirportsData.GetLeTDZCode(runway))
            he_tdz = int(self.OurAirportsData.GetHeTDZCode(runway))
            centerlights = int(self.OurAirportsData.GetRunwayCenterLighting(runway))
            edgelights = int(self.OurAirportsData.GetRunwayEdgeLighting(runway))
            if edgelights == 1: edgelights = 2
            drs = int(self.OurAirportsData.GetRunwayDRS(runway))
            retVal = self.FindAccuratePos(runway)
            if retVal == 1:
                tmp = leRunwayPosOSM
                leRunwayPosOSM = heRunwayPosOSM
                heRunwayPosOSM = tmp
            lelon, lelat = leRunwayPosOSM
            helon, helat = heRunwayPosOSM
            if surface == '':
               surfaceCode = self.OurAirportsData.GetSurfaceCode(runway)
            else:
                surfaceCode = self.OSMAirportsData.GetSurfaceCode(surface) 
            if surfaceCode == 13: #Water runway
                str = "101   %s   1   %s   %.8f %013.8f %s   %.8f %013.8f\n" % \
                      (runwayWidthFt, leRunwayNumber, lelat, lelon, heRunwayNumber, helat, helon)

            else:
                str = "100   %s   %s   %s 0.25 %s %s %s %s   %.8f %013.8f    %s    0.00 %s  %s %s %s %s   %.8f %013.8f    %s    0.00 %s  %s %s %s\n" % \
                      (runwayWidthFt, surfaceCode, shoulderSurface, centerlights, edgelights, \
                      drs, leRunwayNumber, lelat, lelon, leDisplacedThresholdFt, le_rm, \
                      le_appr_lighting, le_tdz, le_reil, heRunwayNumber, helat, helon, \
                      heDisplacedThresholdFt, he_rm, he_appr_lighting, he_tdz, he_reil)
            self.hndApt.write(str)
            return 0
            
    def WriteBeaconDefs(self):
        for lon, lat in self.OSMAirportsData.lstBeacons:
            self.hndApt.write("18   %.8f %013.8f 1 BCN\n" % (lat, lon))
            
    def WriteWindsockDefs(self):
        for lon, lat in self.OSMAirportsData.lstWindsocks:
            self.hndApt.write("19   %.8f %013.8f 1 WS\n" % (lat, lon))
            
    def FindLength(self, lst):
        length = 0
        if lst:
            x1, y1 = lst[0]
            x2, y2 = lst[-1]
            length = self.FindDistance(x1, y1, x2, y2)
        return length
        
    def FindDistance(self, x1, y1, x2, y2):
        return math.sqrt((x2-x1)**2+(y2-y1)**2)
            
    def FindClosestRunway(self, lon, lat):
        min = 0
        minrunway = None
        he = 0
        for runway in self.OurAirportsData.lstRunways:
            lelon, lelat = self.OurAirportsData.GetLeRunwayPosTuple(runway)
            helon, helat = self.OurAirportsData.GetHeRunwayPosTuple(runway)
            dist = self.FindDistance(lon, lat, lelon, lelat)
            if min == 0:
                min = dist
                minrunway = runway
            if min > dist:
                min = dist
                he = 0
                minrunway = runway
            dist = self.FindDistance(lon, lat, helon, helat)
            if min > dist:
                min = dist
                he = 1
                minrunway = runway
        if he == 1:
            runwayNumber = self.OurAirportsData.GetHeRunwayNumber(minrunway)
            runwayHeading = self.OurAirportsData.GetHeRunwayHeading(minrunway)
        else:
            runwayNumber = self.OurAirportsData.GetLeRunwayNumber(minrunway)
            runwayHeading = self.OurAirportsData.GetLeRunwayHeading(minrunway)
            
        return (runwayNumber, runwayHeading)        
            
    def WritePapiDefs(self):
        for lon, lat in self.OSMAirportsData.lstPapi:
            (runwayNumber, runwayHeading) = self.FindClosestRunway(lon, lat)
            self.hndApt.write("21   %.8f %013.8f  2 %.2f   3.00 %s  PAPI\n" % (float(lat), float(lon), float(runwayHeading), runwayNumber))
            
    def OptimizePolygon(self, area):
        i = 0
        lstArea = []
        lstArea.append(area[0])
        while i+1 < len(area):
            x1, y1 = area[i]
            x2, y2 = area[i+1]
            if self.FindDistance(x1, y1, x2, y2) > 1e-6:
                lstArea.append(area[i+1])
            i = i + 1
        return lstArea
                        
    def WritePavedSurfaceDefs(self):
        for pavement in self.OSMAirportsData.lstAprons:
            osmid, name, surface, coords = pavement
            surfaceCode = self.GetSurfaceCode(surface, self.apron_type)
            self.hndApt.write("\n110   %d 0.25  0.00 Apron: %s, OSMID: %s\n" % (surfaceCode, name, osmid))
            lstArea = coords
            area = copy.deepcopy(LinearRing(lstArea))
            if not area.is_ccw:
                tmparea = list(area.coords)[::-1]
            else:
                tmparea = list(area.coords)
            if self.apron_perimeterlights == True:
                lightcode = 102
            else:
                lightcode = 0
            for lon, lat in tmparea[:-2]:
                self.hndApt.write("111  %.8f %013.8f %d\n" % (float(lat), float(lon), lightcode))
            lon, lat = tmparea[-2]
            self.hndApt.write("113  %.8f %013.8f %d\n" % (float(lat), float(lon), lightcode))
		
    def CalcTaxiArea(self, osmid, taxiway, width):
        lstlPos = []
        lstrPos = []
        centerline = LineString(taxiway)
        offset = abs(width/2/111132.92)
        tmp = centerline.parallel_offset(offset, 'left')
        if tmp.type == 'MultiLineString':
            for line in tmp.geoms:
                lstlPos = lstlPos + copy.deepcopy(list(line.coords[:]))
        else:
            lstlPos = copy.deepcopy(list(tmp.coords[:]))
        tmp = centerline.parallel_offset(offset, 'right')
        if tmp.type == 'MultiLineString':
            for line in tmp.geoms:
                lstrPos = lstrPos + copy.deepcopy(list(line.coords[:]))
        else:
            lstrPos = copy.deepcopy(list(tmp.coords[:]))
        lstlPos = self.SnapToApron(lstlPos)
        lstrPos = self.SnapToApron(lstrPos)
        area = copy.deepcopy(LinearRing(lstrPos + lstlPos))
        if not area.is_ccw:
            retVal = list(area.coords)[::-1]
            index = len(lstlPos)
        else:
            retVal = list(area.coords)
            index = len(lstrPos)
        self.lstEdgeLines.append(lstlPos)
        self.lstEdgeLines.append(lstrPos)
        return index, copy.deepcopy(retVal)
        
    def CalcServiceRoadArea(self, osmid, taxiway, width):
        lstlPos = []
        lstrPos = []
        centerline = LineString(taxiway)
        offset = abs(width/2/111132.92)
        tmp = centerline.parallel_offset(offset, 'left')
        if tmp.type == 'MultiLineString':
            for line in tmp.geoms:
                lstlPos = lstlPos + copy.deepcopy(list(line.coords[:]))
        else:
            lstlPos = copy.deepcopy(list(tmp.coords[:]))
        tmp = centerline.parallel_offset(offset, 'right')
        if tmp.type == 'MultiLineString':
            for line in tmp.geoms:
                lstrPos = lstrPos + copy.deepcopy(list(line.coords[:]))
        else:
            lstrPos = copy.deepcopy(list(tmp.coords[:]))
        area = copy.deepcopy(LinearRing(lstrPos + lstlPos))
        if not area.is_ccw:
            retVal = list(area.coords)[::-1]
        else:
            retVal = list(area.coords)
        return copy.deepcopy(retVal)
                    
    def SnapToRunway(self, lst):
        for pt in lst:
            for runway in self.OSMAirportsData.lstRunways:
                tmp, dRunway = runway
                pos1 = dRunway['le_pos']
                pos2 = dRunway['he_pos']
                lsCoords = LineString([pos1, pos2])
                dist = lsCoords.project(Point(pt))
                ptEndnode = lsCoords.interpolate(dist)
                x, y = pt
                x1, y1 = ptEndnode.x, ptEndnode.y
                dist1 = self.FindDistance(x,y,x1,y1)
                if dist1 < 2e-4:
                    if pt in lst:
                        lst[lst.index(pt)] = (x1, y1)
        return lst
        
    def SnapToApron(self, lst):
        if len(lst) < 2: return lst
        for pt in [lst[0], lst[-1]]:
            for aprons in self.OSMAirportsData.lstAprons:
                osmid, name, surface, coords = aprons
                lsCoords = LineString(coords)
                dist = lsCoords.project(Point(pt))
                ptEndnode = lsCoords.interpolate(dist)
                x, y = pt
                x1, y1 = ptEndnode.x, ptEndnode.y
                dist1 = self.FindDistance(x,y,x1,y1)
                if dist1 < 1e-4:
                    lst[lst.index(pt)] = (x1, y1)
                    pt = (x1, y1)
        return lst
            
    def FindLength(self, coords):
        x1, y1 = coords[0]
        x2, y2 = coords[-1]
        dist = self.FindDistance(x1, y1, x2, y2)
        return dist
     
    def WriteTaxiwaySurfaceDefs(self):
        lstAreaStore = []
        lstsorted = sorted(self.OSMAirportsData.lstTaxiways, key=lambda x: x[3], reverse=True)
        for taxiways in lstsorted:
            osmid, name, surface, dist, coords = taxiways
            index, lstArea = self.CalcTaxiArea(osmid, coords, self.taxiway_width)
            lstAreaStore.append(lstArea)
            surfaceCode = self.GetSurfaceCode(surface, self.taxiway_type)
            self.hndApt.write('\n110   %d 0.25  0.00 Taxiway: %s, OSM ID: %s\n' % (surfaceCode, name, osmid))
            i = 0
            if self.edgelights == True:
                lightcode = 102
            else:
                lightcode = 0
            for lon, lat in lstArea[:-1]:
                overlap = 0
#                 for prev in lstAreaStore:
#                     coords1 = prev
#                     if LinearRing(coords1).contains(Point(lon, lat)):
#                         overlap = 1
#                         break
                if (i == index) or (i == 0) or (overlap == 1):    
                    self.hndApt.write("111  %.8f %013.8f\n" % (float(lat), float(lon)))
                else:
                    self.hndApt.write("111  %.8f %013.8f 3 %d\n" % (float(lat), float(lon), lightcode))
                i = i + 1
            (lon, lat) = lstArea[-1]
            self.hndApt.write("113  %.8f %013.8f\n" % (float(lat), float(lon)))
            
    def WriteTransparentSurfaceDefs(self):
        lstTransparent = []
        for taxiways in self.lstEdgeLines:
            coords = taxiways
            dist = self.FindLength(coords)
            if dist < 5e-3:
                lstArea = self.CalcTaxiArea(None, coords, 8)
                surfaceCode = 15
                self.hndApt.write('\n110   15 0.25  0.00 Transparent: xxx\n')
                for lon, lat in lstArea[:-1]:
                       self.hndApt.write("111  %.8f %013.8f\n" % (float(lat), float(lon)))
                (lon, lat) = lstArea[-1]
                self.hndApt.write("113  %.8f %013.8f\n" % (float(lat), float(lon)))
                
            
    def WriteServiceRoadDefs(self):
        for roads in self.OSMAirportsData.lstServiceRoads:
            osmid, name, surface, coords = roads
            lstArea = self.CalcServiceRoadArea(osmid, coords, 8)
            surfaceCode = self.GetSurfaceCode(surface, self.taxiway_type)
            self.hndApt.write('\n110   %d 0.25  0.00 Service Road: %s, OSM ID: %s\n' % (surfaceCode, name, osmid))
            for lon, lat in lstArea[:-1]:
                   self.hndApt.write("111  %.8f %013.8f\n" % (float(lat), float(lon)))
            (lon, lat) = lstArea[-1]
            self.hndApt.write("113  %.8f %013.8f\n" % (float(lat), float(lon)))
            
    def WriteTaxiwayCenterLineDefs(self):
        if self.centerlights == True:
            lightcode = 101
        else:
            lightcode = 0
        for taxiways in self.OSMAirportsData.lstTaxiways: 
            osmid, name, surface, dist, coords = taxiways
            self.hndApt.write('\n120 Taxiway Center-Line: %s, OSMID: %s\n' % (name, osmid))
            for lon, lat in coords[:-1]:
                self.hndApt.write("111  %.8f %013.8f 1 %d\n" % (float(lat), float(lon), lightcode))
            (lon, lat) = coords[-1]
            self.hndApt.write("115  %.8f %013.8f\n" % (float(lat), float(lon)))
            
    def WriteTaxiwayEdgeLineDefs(self):
        if self.edgelights == True:
            lightcode = 102
        else:
            lightcode = 0
        for edgeline in self.lstEdgeLines:
            if edgeline:
                self.hndApt.write('\n120 Taxiway Edge-Line\n')
                for lon, lat in edgeline[:-1]:
                    self.hndApt.write("111  %.8f %013.8f 1 %d\n" % (float(lat), float(lon), lightcode))
                lon, lat = edgeline[-1]
                self.hndApt.write("115  %.8f %013.8f\n" % (float(lat), float(lon)))
            
    def WriteAirportBoundaryDefs(self):
        if self.OSMAirportsData.lstBoundaries:
            self.hndApt.write('\n130 Airport Boundary\n')
            for lon, lat in self.OSMAirportsData.lstBoundaries[:-2]:
               self.hndApt.write("111  %.8f %013.8f\n" % (float(lat), float(lon)))
            (lon, lat) = self.OSMAirportsData.lstBoundaries[-2]
            self.hndApt.write("113  %.8f %013.8f\n" % (float(lat), float(lon)))
        
    def WriteFreqDefs(self):
        for freq in self.OurAirportsData.lstAirportFreqs:
            if (freq['type'] == 'ASOS') or (freq['type'] == 'ATIS'):
                freq_code = 50
            elif (freq['type'] == 'CTAF') or (freq['type'] == 'UNIC'):
                freq_code = 51
            elif (freq['type'] == 'CLD') or (freq['type'] == 'GCCD'):
                freq_code = 52
            elif (freq['type'] == 'GND') or (freq['type'] == 'GCCD'):
                freq_code = 53
            elif freq['type'] == 'TWR':
                freq_code = 54
            elif (freq['type'] == 'APP') or (freq['type'] == 'A/D'):
                freq_code = 55
            elif (freq['type'] == 'DEP'):
                freq_code = 56
            else:
                freq_code = 51
         
            self.hndApt.write("%d %d %s\n" % (freq_code, int(float(freq['frequency_mhz'])*100), freq['description']))
        
    def mkdir(self, path):
        print 'Creating %s folder' % path
        try: 
            os.makedirs(path)
        except OSError:
            if not os.path.isdir(path):
                raise
                print 'Failed!!!'
                sys.exit(0)
                
    def close(self):
        self.hndApt.write('99\n')
        self.hndApt.close()
        shutil.copy('apt.dat', self.path)