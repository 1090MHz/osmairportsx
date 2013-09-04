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
import shutil
import random
import math
import sys
import os
from shapely.geometry import LinearRing

class DSFDataCreator(object):

    def __init__(self, icao='', osmdata=None, bldg_height = (20, 30), 
                terminal_height = (30,40)):
        print 'Initializing DSFDataCreator...'
        self.icao = icao
        self.file = file
        self.OSMData = osmdata
        self.bldg_height = bldg_height
        self.terminal_height = terminal_height
        if self.OSMData.lstBoundaries:
            lon, lat = self.OSMData.lstBoundaries[0]
        else:
            osmid, lon, lat = self.OSMData.lstCoords[0]
        self.latmin=lat
        self.latmax=lat
        self.lonmin=lon
        self.lonmax=lon
        self.lstfacades = []
        if self.OSMData.lstBoundaries:
            for lon, lat in self.OSMData.lstBoundaries:
                if lat < self.latmin: self.latmin = lat
                if lat > self.latmax: self.latmax = lat
                if lon < self.lonmin: self.lonmin = lon
                if lon > self.lonmax: self.lonmax = lon
        else:
            for osmid, lon, lat in self.OSMData.lstCoords:
                if lat < self.latmin: self.latmin = lat
                if lat > self.latmax: self.latmax = lat
                if lon < self.lonmin: self.lonmin = lon
                if lon > self.lonmax: self.lonmax = lon
        self.lsthnddsf = [[0 for i in range(int(self.latmax)-int(self.latmin) + 2)] for i in range(int(self.lonmax)-int(self.lonmin) + 2)]
        self.path = os.path.join('.', icao)
        self.mkdir(self.path)
        self.path = os.path.join(self.path, 'Earth Nav Data')
        self.mkdir(self.path)
        for i in range(int(self.latmax)-int(self.latmin) + 1):
            for j in range(int(self.lonmax)-int(self.lonmin) + 1):
                self.dsffile = "%+3d%+04d.txt" % (math.floor(self.latmin)+i, math.floor(self.lonmin)+j)
                self.lsthnddsf[i][j]=open(self.dsffile, "wb")
                self.WriteFileHeader(self.lsthnddsf[i][j], i, j)
                self.WriteSceneryBoundaries(self.lsthnddsf[i][j], i, j)
                self.DefineFacadeObjects(self.lsthnddsf[i][j])
                print("Scenery File %s created..." % self.dsffile)
            
    def mkdir(self, path):
        print 'Creating %s folder' % path
        try: 
            os.makedirs(path)
        except OSError:
            if not os.path.isdir(path):
                raise
                print 'Failed!!!'
                sys.exit(0)
                
    def WritePolygon(self, arg1, arg2, arg3, lst1):
        lst = self.IdentifyWinding(lst1)
        lon, lat = lst[0]
        latindex = int(lat) - int(self.latmin)
        lonindex = int(lon) - int(self.lonmin)
        self.lsthnddsf[latindex][lonindex].write('BEGIN_POLYGON %s %s %s\n' % (arg1, arg2, arg3))
        self.lsthnddsf[latindex][lonindex].write('BEGIN_WINDING\n')
        for lon, lat in lst[:-1]:
            self.lsthnddsf[latindex][lonindex].write("POLYGON_POINT %f %f %f\n" % (lon, lat, 0.0))
        self.lsthnddsf[latindex][lonindex].write('END_WINDING\n')
        self.lsthnddsf[latindex][lonindex].write('END_POLYGON\n')
        
    def WriteFileHeader(self, hndl, i, j):
        if sys.platform == 'darwin':
            plm = 'A'
        else:
            plm = 'I'
        latmin = math.floor(self.latmin+i)
        lonmin = math.floor(self.lonmin+j)
        latmax = math.floor(self.latmin+i+1)
        lonmax = math.floor(self.lonmin+j+1)
        if latmin < self.latmin:
            latmin = self.latmin
        if lonmin < self.lonmin:
            lonmin = self.lonmin
        if latmax > self.latmax:
            latmax = self.latmax
        if lonmax > self.lonmax:
            lonmax = self.lonmax
        
        hndl.write("%s\n" % plm)
        hndl.write('800\n')
        hndl.write('DSF2TEXT\n')
        hndl.write('PROPERTY sim/planet earth\n')
        hndl.write('PROPERTY sim/overlay 1\n')
        hndl.write('PROPERTY sim/require_agpoint 1/0\n')
        hndl.write('PROPERTY sim/require_object 1/0\n')
        hndl.write('PROPERTY sim/require_facade 1/0\n')
        hndl.write('PROPERTY sim/creation_agent OSMAirportsX\n')
        hndl.write("PROPERTY sim/exclude_obj %.6f/%.6f/%.6f/%.6f\n" % (lonmin, latmin, lonmax, latmax))
        hndl.write("PROPERTY sim/exclude_fac %.6f/%.6f/%.6f/%.6f\n" % (lonmin, latmin, lonmax, latmax))
        hndl.write("PROPERTY sim/exclude_for %.6f/%.6f/%.6f/%.6f\n" % (lonmin, latmin, lonmax, latmax))
        
    def WriteSceneryBoundaries(self, hndl, i, j):
        hndl.write("PROPERTY sim/west %d\n" % math.floor(self.lonmin+j))
        hndl.write("PROPERTY sim/east %d\n" % math.floor(self.lonmin+j+1))
        hndl.write("PROPERTY sim/north %d\n" % math.floor(self.latmin+i+1))
        hndl.write("PROPERTY sim/south %d\n" % math.floor(self.latmin+i))
        
    def DefineFacadeObjects(self, hndl):
        self.lstfacades = [ 'lib/airport/Modern_Airports/Facades/modern1.fac',
                            'lib/airport/Modern_Airports/Facades/modern2.fac',
                            'lib/airport/Modern_Airports/Facades/modern3.fac',
                            'lib/airport/Common_Elements/Hangars/White_Hangar.fac',
                            'lib/airport/Common_Elements/Misc_Buildings/Cargo_Terminal.fac',
                            'lib/airport/Common_Elements/Fence_Facades/Fence.fac',
                            'lib/airport/Common_Elements/Misc_Buildings/White_Office.fac',
                            'lib/g10/autogen/point_building.fac',
                            'lib/g10/autogen/point_building_30x30_10.fac',
                            'lib/g10/autogen/point_building_30x30_16.fac'
                             ]
        self.lstobjects = ['lib/airport/Ramp_Equipment/Jetway_250cm.obj',
                            'lib/airport/Ramp_Equipment/Jetway_400cm.obj',
                            'lib/airport/Ramp_Equipment/Jetway_500cm.obj'
                            ]
        for object in self.lstobjects:
            hndl.write("OBJECT_DEF %s\n" % object)
        for facade in self.lstfacades:
            hndl.write("POLYGON_DEF %s\n" % facade)
            
    """DSFs are required to have counter-clockwise windings for its polygons.
    A simple check to identify if it is indeed so; if not, the caller should reverse the list of polygon nodes"""
    def IdentifyWinding(self, lst):
        if len(lst)<3:
            return lst
        area = LinearRing(lst)
        if not area.is_ccw:
            retVal = list(area.coords)[::-1]
        else:
            retVal = list(area.coords)
        return retVal
    
    def CreateTerminals(self):
        for terminal in self.OSMData.lstTerminals:
            (min, max) = self.terminal_height
            terminal_index = random.randint(0, 2)
            bldg_height = random.randint(min, max)
            self.WritePolygon(terminal_index, bldg_height, 3, terminal)           
            
    def ShortestDistLineAndPt(self, Pt1, Pt2, Pt3):
        x1, y1 = Pt1
        x2, y2 = Pt2
        x3, y3 = Pt3
        dx = float(x2-x1)
        dy = float(y2-y1)
        length = dx*dx + dy*dy
        unit_vector = ((x3 - x1) * dx + (y3 - y1) * dy) / length
        if unit_vector > 1:
            unit_vector = 1
        elif unit_vector < 0:
            unit_vector = 0
        x = x1 + unit_vector * dx
        y = y1 + unit_vector * dy
        distx = x - x3
        disty = y - y3
        dist = math.sqrt(distx*distx + disty*disty)
        return (dist, (x, y))
        
    def Bearing(self, P1,P2):
        lon1, lat1 = P1
        lon2, lat2 = P2
        lat1 = math.radians(lat1)
        lon1 = math.radians(lon1)
        lat2 = math.radians(lat2)
        lon2 = math.radians(lon2)
        dlat = lat2-lat1
        dlon = lon2-lon1
        bearing = math.atan2( (math.sin(dlon)*math.cos(lat2)) , (math.cos(lat1)*math.sin(lat2) - math.sin(lat1)*math.cos(lat2)*math.cos(dlon)) )
        bearing = math.degrees(bearing)
        if bearing < 0: bearing = bearing + 360
        return (bearing)

    def CreateGates(self):
        for gatepos in self.OSMData.lstGates:
            distmin = 0
            for terminal in self.OSMData.lstTerminals:
                i = 0
                while i+1<len(terminal):
                    x1, y1 = terminal[i]
                    x2, y2 = terminal[i+1]
                    dist, pos = self.ShortestDistLineAndPt(terminal[i], terminal[i+1], gatepos)
                    if distmin == 0: 
                        distmin = dist
                        posmin = pos
                    elif distmin > dist: 
                        distmin = dist
                        posmin = pos
                    i = i + 1
            gatelon, gatelat = gatepos
            termlon, termlat = posmin
            brng = self.Bearing(posmin, gatepos)
            latindex = int(gatelat) - int(self.latmin)
            lonindex = int(gatelon) - int(self.lonmin)
            self.lsthnddsf[latindex][lonindex].write("OBJECT 0 %f %f %f\n" % (termlon, termlat, brng))
        
  
    def CreateHangars(self):
        for hangar in self.OSMData.lstHangars:
            self.WritePolygon(3, 19, 3, hangar)
            
    def CreateBldgs(self):
        for bldg in self.OSMData.lstBldgs:
            bldg_index = random.randint(6, 9)
            (min, max) = self.bldg_height
            bldg_height = random.randint(min, max)
            self.WritePolygon(bldg_index, bldg_height, 3, bldg)

    def CreateFences(self):
        for fence in self.OSMData.lstFences:
            self.WritePolygon(5, 50, 3, fence)
        
    def close(self):
        for i in range(int(self.latmax)-int(self.latmin) + 1):
            for j in range(int(self.lonmax)-int(self.lonmin) + 1):
                self.lsthnddsf[i][j].close()
                dsffile = "%+3d%+04d.txt" % (math.floor(self.latmin)+i, math.floor(self.lonmin)+j)
                newdir = "%+3d%+04d" % ((self.latmin+i) - ((self.latmin+i)%10), (self.lonmin+j)-((self.lonmin+j)%10))
                self.scenery_path = os.path.join(self.path, newdir)
                self.mkdir(self.scenery_path)
                shutil.copy(dsffile, self.scenery_path)
        
    def WriteDSF(self):
        self.CreateTerminals()
        self.CreateGates()
        self.CreateHangars()
        self.CreateBldgs()
        self.CreateFences()
        self.close()
