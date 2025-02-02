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
import csv

class OurAirportsDataExtractor(object):

    def __init__(self, icao=''):
        print 'Initializing OurAirportsDataExtractor...'
        self.icao=icao
        self.lstRunways = []
        self.lstAirports = []
        self.lstAirportFreqs = []
        self.ExtractDataWithFilter(self.icao)
        
    def unicode_csv_reader(self, utf8_data, dialect=csv.excel, **kwargs):
        csv_reader = csv.reader(utf8_data, dialect=dialect, **kwargs)
        for row in csv_reader:
            yield [unicode(cell, 'utf-8') for cell in row]
        
    def ReturnListFromCSV(self, file='', list='', ident=0, filter='', ex_ident=-1, exclude='', hit_once=0):
        inp = open(file, "rb")
        reader = self.unicode_csv_reader(inp)
        hdrflag = 1
        for row in reader:
            # Save header row.
            if hdrflag == 1:
                header = row
                hdrflag = 0
            elif (ex_ident != -1) and (row[ex_ident] == exclude):
                continue
            elif (row[ident] == filter) or (filter == ''):
                i = -1
                try:
                    while 1:
                        i = row.index('', i+1)
                        row[i] = '0'
                except ValueError:
                    pass
                list.append(dict(zip(header, row)))
                if hit_once == 1: break
        inp.close()
        
    def GetAirportICAO(self):
        if self.icao == '0':
            print 'Error! No ICAO defined!'
            return 0
        else:
            return("%s" % self.lstAirports[0]['ident'])
            
    def GetAirportName(self):
        if self.icao == '0':
            print 'Error! No ICAO defined!'
            return 0
        else:
            return("%s" % self.lstAirports[0]['name'])
            
    def GetAirportPosDir(self):
        if self.icao == '0':
            print 'Error! No ICAO defined!'
            return 0
        else:
            num = float(self.lstAirports[0]['latitude_deg'])
            num1 = float(self.lstAirports[0]['longitude_deg'])
            newdir = "%+3d%+04d" % (num - (num%10), num1-(num1%10))
            return("%s" % newdir)
            
    def GetAirportElevationFt(self):
        if self.icao == '0':
            print 'Error! No ICAO defined!'
            return 0
        else:
            return("%s" % self.lstAirports[0]['elevation_ft'])
        
    def GetSurfaceCode(self, runway):
        surfaceCode = 1
        if runway['surface'] == 'ASPH-G': surfaceCode = 1
        elif runway['surface'] == 'ASP': surfaceCode = 1
        elif runway['surface'] == 'ASPH-E': surfaceCode = 1
        elif runway['surface'] == 'ASPH-TRTD-P': surfaceCode = 1
        elif runway['surface'] == 'ASPH-CONC-G': surfaceCode = 1
        elif runway['surface'] == 'PEM': surfaceCode = 2
        elif runway['surface'] == 'CON': surfaceCode = 2
        elif runway['surface'] == 'CONC': surfaceCode = 2
        elif runway['surface'] == 'CONC-G': surfaceCode = 2
        elif runway['surface'] == 'CONC-TURF': surfaceCode = 2
        elif runway['surface'].upper() == 'GRASS': surfaceCode = 3
        elif runway['surface'] == 'GRS': surfaceCode = 3
        elif runway['surface'] == 'TURF': surfaceCode = 3
        elif runway['surface'] == 'TURF-G': surfaceCode = 3
        elif runway['surface'] == 'TURF-F': surfaceCode = 3
        elif runway['surface'] == 'TURF-GRVL': surfaceCode = 3
        elif runway['surface'] == 'TURF-GRVL-F': surfaceCode = 3
        elif runway['surface'] == 'TURF-DIRT': surfaceCode = 3
        elif runway['surface'] == 'DIRT': surfaceCode = 4
        elif runway['surface'] == 'DIRT-TURF-G': surfaceCode = 4
        elif runway['surface'] == 'DIRT-P': surfaceCode = 4
        elif runway['surface'] == 'DIRT-G': surfaceCode = 4
        elif runway['surface'] == 'GRVL': surfaceCode = 5
        elif runway['surface'] == 'GRVL-E': surfaceCode = 5
        elif runway['surface'] == 'GRVL-F': surfaceCode = 5
        elif runway['surface'] == 'GRVL-G': surfaceCode = 5
        elif runway['surface'] == 'GRVL-DIRT': surfaceCode = 5
        elif runway['surface'] == 'GRVL-DIRT-F': surfaceCode = 5
        elif runway['surface'] == 'SAND': surfaceCode = 12 #"""Mapping Sand to Dry lakebed in x-plane"""
        elif runway['surface'] == 'WATER': surfaceCode = 13
        elif runway['surface'] == 'ICE': surfaceCode = 14
        elif runway['surface'] == 'SNO': surfaceCode = 14
        return ("%s" % surfaceCode)
        
    def GetEdgeLightingCode(self, runway):
        if runway['lighted'] == 1: edgeLighting = 2 
        else: edgeLighting = 0 #Provide edge lighting if center lighting is available
        
    def GetRunwayWidth(self, runway):
        return ("%.2f" % (0.3048 * float(runway['width_ft'])))
        
    def IsRunwayLighted(self, runway):
        return ("%s" % runway['lighted'])
        
    def GetLeRunwayNumber(self, runway):
        return("%s" % runway['le_ident'].upper())
        
    def GetLeRunwayPosTuple(self, runway):
        return(float(runway['le_longitude_deg']), float(runway['le_latitude_deg']))
        
    def GetHeRunwayNumber(self, runway):
        return("%s" % runway['he_ident'].upper())
        
    def GetHeRunwayPosTuple(self, runway):
        return(float(runway['he_longitude_deg']), float(runway['he_latitude_deg']))
        
    def GetLeDisplacementThresholdFt(self, runway):
        return("%.2f" % (0.3048 * float(runway['le_displaced_threshold_ft'])))
    
    def GetHeDisplacementThresholdFt(self, runway):
        return("%.2f" % (0.3048 * float(runway['he_displaced_threshold_ft'])))
        
    def GetLeRunwayHeading(self, runway):
        return runway['le_heading_degT']
        
    def GetHeRunwayHeading(self, runway):
        return runway['he_heading_degT']
        
    def GetRunwayCenterLighting(self, runway):
        if 'center_lighting' not in runway.keys():
            runway['center_lighting'] = 1
        return runway['center_lighting']
        
    def GetRunwayEdgeLighting(self, runway):
        if 'edge_lighting' not in runway.keys():
            runway['edge_lighting'] = 1
        return runway['edge_lighting']
        
    def GetRunwayDRS(self, runway):
        if 'drs' not in runway.keys():
            runway['drs'] = 1
        return runway['drs']
        
    def GetRunwayShoulderSurface(self, runway):
        if 'shoulder' not in runway.keys():
            runway['shoulder'] = 1
        return runway['shoulder']
        
    def GetLeRunwayMarkingCode(self, runway):
        if 'le_rm' not in runway.keys():
            runway['le_rm'] = 3
        return runway['le_rm']
    
    def GetLeApproachLightingCode(self, runway):
        if 'le_al' not in runway.keys():
            runway['le_al'] = 12
        return runway['le_al']
        
    def GetLeREILCode(self, runway):
        if 'le_reil' not in runway.keys():
            runway['le_reil'] = 0
        return runway['le_reil']
        
    def GetLeTDZCode(self, runway):
        if 'le_tdz' not in runway.keys():
            runway['le_tdz'] = 1
        return runway['le_tdz']
        
    def GetHeRunwayMarkingCode(self, runway):
        if 'he_rm' not in runway.keys():
            runway['he_rm'] = 3
        return runway['he_rm']
    
    def GetHeApproachLightingCode(self, runway):
        if 'he_al' not in runway.keys():
            runway['he_al'] = 12
        return runway['he_al']
        
    def GetHeREILCode(self, runway):
        if 'he_reil' not in runway.keys():
            runway['he_reil'] = 0
        return runway['he_reil']
        
    def GetHeTDZCode(self, runway):
        if 'he_tdz' not in runway.keys():
            runway['he_tdz'] = 1
        return runway['he_tdz']

    def SetRunwayCenterLighting(self, runway, cl):
        runway['center_lighting'] = cl
        
    def SetRunwayEdgeLighting(self, runway, el):
        runway['edge_lighting'] = el
        
    def SetRunwayDRS(self, runway, drs):
        runway['drs'] = drs
        
    def SetRunwayShoulderSurface(self, runway, shoulder):
        runway['shoulder'] = shoulder
        
    def SetLeRunwayMarkingCode(self, runway, rm):
        runway['le_rm'] = rm
    
    def SetLeApproachLightingCode(self, runway, al):
        runway['le_al'] = al
        
    def SetLeREILCode(self, runway, reil):
        runway['le_reil'] = reil
        
    def SetLeTDZCode(self, runway, tdz):
        runway['le_tdz'] = tdz
        
    def SetHeRunwayMarkingCode(self, runway, rm):
        runway['he_rm'] = rm
    
    def SetHeApproachLightingCode(self, runway, al):
        runway['he_al'] = al
        
    def SetHeREILCode(self, runway, reil):
        runway['he_reil'] = reil
        
    def SetHeTDZCode(self, runway, tdz):
        runway['he_tdz'] = tdz
        
    def ExtractData(self):
        self.ReturnListFromCSV(file='runways.csv', filter='', list=self.lstRunways)
        self.ReturnListFromCSV(file='airports.csv', filter='', list=self.lstAirports)
        self.ReturnListFromCSV(file='airport-frequencies.csv', filter='', list=self.lstAirportFreqs)
        
    def ExtractDataWithFilter(self, filter=''):
        print "Extracting data with filter %s..." % filter
        self.ReturnListFromCSV(file='runways.csv', list=self.lstRunways, ident=2, filter=filter, ex_ident=7, exclude = '1')
        self.ReturnListFromCSV(file='airports.csv', list=self.lstAirports, ident=1, filter=filter )
        self.ReturnListFromCSV(file='airport-frequencies.csv', list=self.lstAirportFreqs, ident=2, filter=filter)
    