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
import shutil
import random
import math
import sys
import os

class DSFDataCreator(object):

    def __init__(self, icao='', osmdata=None, bldg_height = (20, 30), 
                terminal_height = (30,40)):
        print 'Initializing DSFDataCreator...'
        self.icao = icao
        self.file = file
        self.OSMData = osmdata
        self.bldg_height = bldg_height
        self.terminal_height = terminal_height
        lat, lon = self.OSMData.lstBoundaries[0]
        self.latmin=lat
        self.latmax=lat
        self.lonmin=lon
        self.lonmax=lon
        self.lstfacades = []
        for lat, lon in self.OSMData.lstBoundaries:
            if lat < self.latmin: self.latmin = lat
            if lat > self.latmax: self.latmax = lat
            if lon < self.lonmin: self.lonmin = lon
            if lon > self.lonmax: self.lonmax = lon
        self.path = os.path.join('.', icao)
        self.mkdir(self.path)
        self.path = os.path.join(self.path, 'Earth Nav Data')
        self.mkdir(self.path)
        self.dsffile = "%+3d%+04d.txt" % (math.floor(self.latmin), math.floor(self.lonmin))
        self.hndDSF = open(self.dsffile, "wb")
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
        
    def WriteFileHeader(self):
        if sys.platform == 'darwin':
            plm = 'A'
        else:
            plm = 'I'
        self.hndDSF.write("%s\n" % plm)
        self.hndDSF.write('800\n')
        self.hndDSF.write('DSF2TEXT\n')
        self.hndDSF.write('PROPERTY sim/planet earth\n')
        self.hndDSF.write('PROPERTY sim/overlay 1\n')
        self.hndDSF.write('PROPERTY sim/require_agpoint 1/0\n')
        self.hndDSF.write('PROPERTY sim/require_object 1/0\n')
        self.hndDSF.write('PROPERTY sim/require_facade 1/0\n')
        self.hndDSF.write('PROPERTY sim/creation_agent OSMAirportsX\n')
        
    def WriteSceneryBoundaries(self):
        self.hndDSF.write("PROPERTY sim/west %d\n" % math.floor(self.lonmin))
        self.hndDSF.write("PROPERTY sim/east %d\n" % math.ceil(self.lonmax))
        self.hndDSF.write("PROPERTY sim/north %d\n" % math.ceil(self.latmax))
        self.hndDSF.write("PROPERTY sim/south %d\n" % math.floor(self.latmin))
        
    def DefineFacadeObjects(self):
        self.lstfacades = [ 'lib/airport/Classic_Airports/Facades/classic1.fac',
                            'lib/airport/Classic_Airports/Facades/classic2.fac',
                            'lib/airport/Classic_Airports/Facades/classic3.fac',
                            'lib/airport/Common_Elements/Hangars/White_Hangar.fac',
                            'lib/airport/Common_Elements/Misc_Buildings/Cargo_Terminal.fac',
                            'lib/airport/Common_Elements/Fence_Facades/Fence.fac',
                            'lib/airport/Common_Elements/Misc_Buildings/White_Office.fac',
                            'lib/g10/autogen/point_building.fac',
                            'lib/g10/autogen/point_building_30x30_10.fac',
                            'lib/g10/autogen/point_building_30x30_16.fac'
                             ]
        for facade in self.lstfacades:
            self.hndDSF.write("POLYGON_DEF %s\n" % facade)
            
    """DSFs are required to have counter-clockwise windings for its polygons.
    A simple check to identify if it is indeed so; if not, the caller should reverse the list of polygon nodes"""
    def IdentifyWinding(self, list):
        i = 0
        dir = 0
        while i+1<len(list):
            (x1, y1) = list[i]
            (x2, y2) = list[i+1]
            dir = dir + (x1+x2)*(y1-y2)
            i = i + 1
        return dir
    
    def CreateTerminals(self):
        for terminal in self.OSMData.lstTerminals:
            (min, max) = self.terminal_height
            bldg_height = random.randint(min, max)
            wind_dir = self.IdentifyWinding(terminal)
            if wind_dir < 0:
                terminal = terminal[::-1]
            self.hndDSF.write('BEGIN_POLYGON 0 %d 3\n' % bldg_height)
            self.hndDSF.write('BEGIN_WINDING\n')
            for lat, lon in terminal[:-1]:
                self.hndDSF.write("POLYGON_POINT %f %f %f\n" % (lon, lat, 0.0))
            self.hndDSF.write('END_WINDING\n')
            self.hndDSF.write('END_POLYGON\n')
    
    def CreateHangars(self):
        for hangar in self.OSMData.lstHangars:
            wind_dir = self.IdentifyWinding(hangar)
            if wind_dir < 0:
                hangar = hangar[::-1]
            self.hndDSF.write('BEGIN_POLYGON 3 19 3\n')
            self.hndDSF.write('BEGIN_WINDING\n')
            for lat, lon in hangar[:-1]:
                self.hndDSF.write("POLYGON_POINT %f %f %f\n" % (lon, lat, 0.0))
            self.hndDSF.write('END_WINDING\n')
            self.hndDSF.write('END_POLYGON\n')
            
    def CreateBldgs(self):
        for bldg in self.OSMData.lstBldgs:
            bldg_index = random.randint(6, 9)
            (min, max) = self.bldg_height
            bldg_height = random.randint(min, max)
            wind_dir = self.IdentifyWinding(bldg)
            if wind_dir < 0:
                bldg = bldg[::-1]
            self.hndDSF.write('BEGIN_POLYGON %d %d 3\n' % (bldg_index, bldg_height))
            self.hndDSF.write('BEGIN_WINDING\n')
            for lat, lon in bldg[:-1]:
                self.hndDSF.write("POLYGON_POINT %f %f %f\n" % (lon, lat, 0.0))
            self.hndDSF.write('END_WINDING\n')
            self.hndDSF.write('END_POLYGON\n')
            
    def CreateFences(self):
        for fence in self.OSMData.lstFences:
            wind_dir = self.IdentifyWinding(fence)
            if wind_dir < 0:
                fence = fence[::-1]
            self.hndDSF.write('BEGIN_POLYGON 5 50 3\n')
            self.hndDSF.write('BEGIN_WINDING\n')
            for lat, lon in fence:
                self.hndDSF.write("POLYGON_POINT %f %f %f\n" % (lon, lat, 0.0))
            self.hndDSF.write('END_WINDING\n')
            self.hndDSF.write('END_POLYGON\n')

    def GetFilename(self):
        return self.dsffile
        
    def close(self):
        self.hndDSF.close()
        newdir = "%+3d%+04d" % (self.latmin - (self.latmin%10), self.lonmin-(self.lonmin%10))
        self.scenery_path = os.path.join(self.path, newdir)
        self.mkdir(self.scenery_path)
        print 'Custom Scenery folders created...'
        shutil.copy(self.dsffile, self.scenery_path)
        
