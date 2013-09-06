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
from shapely.geometry import LinearRing, LineString

class XPAPTDataCreator(object):

    def __init__(self, icao='', osmfile='', centerlines=False, centerlights=False, taxiway_width=32, taxiway_type="ASPHALT", ourairportsdata=None, osmdata=None):
        self.icao=icao
        self.osmfile=osmfile
        self.centerlines=centerlines
        self.centerlights=centerlights
        self.taxiway_width = taxiway_width
        self.taxiway_type = taxiway_type
        self.lepos = 0
        self.hepos = 0
        print 'Initializing the XPSceneryCreator...'
        self.OurAirportsData = ourairportsdata
        self.OSMAirportsData = osmdata
        self.hndApt = open("apt.dat", "wb")
        self.path = os.path.join('.', icao)
        self.mkdir(self.path)
        self.path = os.path.join(self.path, 'Earth Nav Data')
        self.mkdir(self.path)
        
        
    def GetSurfaceCode(self, OSMSurface, optionSurface):
        if OSMSurface == '':
            if optionSurface == "ASPHALT":
                surfaceCode = 1
            elif optionSurface == "CONCRETE":
                surfaceCode = 2
            elif optionSurface == "GRASS":
                surfaceCode = 3
            elif optionSurface == "DIRT":
                surfaceCode = 4
            elif optionSurface == "GRAVEL":
                surfaceCode = 5
            else:
                surfaceCode = 1
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
        surface, leRunwayPosOSM = self.OSMAirportsData.GetRunwayPos(leRunwayNumber)
        heRunwayNumber = self.OurAirportsData.GetHeRunwayNumber(runway)
        heRunwayPos = self.OurAirportsData.GetHeRunwayPosTuple(runway)
        surface, heRunwayPosOSM = self.OSMAirportsData.GetRunwayPos(heRunwayNumber)
        (x1, y1) = leRunwayPos
        (x2, y2) = leRunwayPosOSM
        lePosDistance = math.sqrt((x2-x1)**2+(y2-y1)**2)
        (x2, y2) = heRunwayPosOSM
        hePosDistance = math.sqrt((x2-x1)**2+(y2-y1)**2)
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
            surface, leRunwayPosOSM = self.OSMAirportsData.GetRunwayPos(leRunwayNumber)
            leDisplacedThresholdFt = self.OurAirportsData.GetLeDisplacementThresholdFt(runway)
            heRunwayNumber = self.OurAirportsData.GetHeRunwayNumber(runway)
            surface, heRunwayPosOSM = self.OSMAirportsData.GetRunwayPos(heRunwayNumber)
            heDisplacedThresholdFt = self.OurAirportsData.GetHeDisplacementThresholdFt(runway)
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
            str = "100   %s   %s   2 0.25 %s 0 0 %s   %.8f %013.8f    %s    0.00 1  0 0 0 %s   %.8f %013.8f    %s    0.00 3  12 0 1\n" % \
                  (runwayWidthFt, surfaceCode, lighted, leRunwayNumber, lelat, lelon, leDisplacedThresholdFt, heRunwayNumber, \
                   helat, helon, heDisplacedThresholdFt)
            self.hndApt.write(str)
            
    def WriteBeaconDefs(self):
        for lon, lat in self.OSMAirportsData.lstBeacons:
            self.hndApt.write("18   %.8f %013.8f 1 BCN\n" % (lat, lon))
            
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
            surfaceCode = self.GetSurfaceCode(surface, self.taxiway_type)
            self.hndApt.write("\n110   %d 0.25  0.00 Apron: %s, OSMID: %s\n" % (surfaceCode, name, osmid))
            lstArea = coords
            area = copy.deepcopy(LinearRing(lstArea))
            if not area.is_ccw:
                tmparea = list(area.coords)[::-1]
            else:
                tmparea = list(area.coords)
            for lon, lat in tmparea[:-2]:
                self.hndApt.write("111  %.8f %013.8f\n" % (float(lat), float(lon)))
            lon, lat = tmparea[-2]
            self.hndApt.write("113  %.8f %013.8f\n" % (float(lat), float(lon)))
		
    def CalcTaxiArea(self, taxiway, width):
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
     
    def WriteTaxiwaySurfaceDefs(self):
        for taxiways in self.OSMAirportsData.lstTaxiways:
            osmid, name, surface, coords = taxiways
            lstArea = self.CalcTaxiArea(coords, self.taxiway_width)
            surfaceCode = self.GetSurfaceCode(surface, self.taxiway_type)
            self.hndApt.write('\n110   %d 0.25  0.00 Taxiway: %s, OSM ID: %s\n' % (surfaceCode, name, osmid))
            for lon, lat in lstArea[:-1]:
                   self.hndApt.write("111  %.8f %013.8f\n" % (float(lat), float(lon)))
            (lon, lat) = lstArea[-1]
            self.hndApt.write("113  %.8f %013.8f\n" % (float(lat), float(lon)))
            
    def WriteServiceRoadDefs(self):
        for roads in self.OSMAirportsData.lstServiceRoads:
            osmid, name, coords = roads
            lstArea = self.CalcTaxiArea(coords, 8)
            self.hndApt.write('\n110   %d 0.25  0.00 Service Road: %s, OSM ID: %s\n' % (1, name, osmid))
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
            osmid, name, surface, coords = taxiways
            self.hndApt.write('\n120 Taxiway Center-Line: %s, OSMID: %s\n' % (name, osmid))
            for lon, lat in coords[:-1]:
                self.hndApt.write("111  %.8f %013.8f 1 %d\n" % (float(lat), float(lon), lightcode))
            (lon, lat) = coords[-1]
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
        
        
    def WriteAptDat(self):
        self.WriteFileHeader()
        self.WriteAPTHeader()
        self.WriteRunwayDefs()
        self.WritePapiDefs()
        self.WriteTaxiwaySurfaceDefs()
        self.WriteTaxiwayCenterLineDefs()
        self.WriteServiceRoadDefs()
        self.WritePavedSurfaceDefs()
        self.WriteAirportBoundaryDefs()
        self.WriteBeaconDefs()
        self.WriteFreqDefs()
        self.close()