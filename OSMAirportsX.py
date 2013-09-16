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
from optparse import OptionParser
import os, sys
from OurAirportsDataExtractor import OurAirportsDataExtractor
from OSMAirportDataExtractor import OSMAirportDataExtractor
from XPAPTDataCreator import XPAPTDataCreator
from DSFDataCreator import DSFDataCreator

from GUI import Window, CheckBox, Button, Label, TextField, rgb, application, FileDialogs, Grid, ListButton
from GUI.Files import FileType, DirRef, FileRef

class OSMAirportsX(object):
    
    def __init__(self):
        self.osmfileref = ''
        self.genpath = None
        self.OurAirportsData = None
        self.last_dir = DirRef(path = os.path.abspath(os.path.dirname(sys.argv[0])))
        """Labels"""
        label = Label(text = "Airport ICAO: ", color = rgb(0.5, 0, 0))
        label1 = Label(text = "Taxiway Settings:", color = rgb(0, 0.5, 0))
        label2 = Label(text = "Width(m): ", width = 150, height = 20)
        label3 = Label(text = "Fallback values:", color = rgb(0, 0.5, 0))
        label4 = Label(text = "Taxiway Surface")
        label5 = Label(text = "Apron Surface")
        label6 = Label(text = "Runway Settings:", color = rgb(0, 0.5, 0))
        label7 = Label(text = "Runway Number")
        label8 = Label(text = "Shoulder Surface")
        label9 = Label(text = "Runway Marking")
        label10 = Label(text = "Approach Lighting")
        label11 = Label(text = "REIL")
        label12 = Label(text = "DSF Settings:", color = rgb(0, 0.5, 0))
        label13 = Label(text = "Building Heights")
        label14 = Label(text = "Terminal Heights")
        self.lblgenpath = Label(text = "Generation Path: ", width=400)
        self.filename = Label(text = "Filename: ", width = 150) 
        self.lbl_le_rm = Label(width=100, text = "")
        self.lbl_he_rm = Label(width=100, text = "")
        """Text Fields"""
        self.icao = TextField(width = 100)
        self.taxi_width = TextField(width = 100, value = 32)
        self.bldg_height_min = TextField(width = 100, value = 20)
        self.bldg_height_max = TextField(width = 100, value = 50)
        self.terminal_height_min = TextField(width = 100, value = 50)
        self.terminal_height_max = TextField(width = 100, value = 100)
        """Check Boxes"""
        self.taxi_centerlines = CheckBox(title = "Centerlines", on = 1, width=150)
        self.taxi_centerlights = CheckBox(title = "Centerlights",  on = 1, width=150)
        self.taxi_edgelines = CheckBox(title = "Edgelines", on = 1, width=150)
        self.taxi_edgelights = CheckBox(title = "Edgelights", on = 1, width=150)
        self.centerlights = CheckBox(title = "Centerlights",  on = 1, action=self.update_fields, width=150)
        self.edgelights = CheckBox(title = "Edgelights",  on = 1, action=self.update_fields, width=150)
        self.drs = CheckBox(title = "Distance signs",  on = 1, action=self.update_fields, width=150)
        self.le_tdz = CheckBox(title = "TDZ", on = 1, action=self.update_fields, width=150)
        self.he_tdz = CheckBox(title = "TDZ", on = 1, action=self.update_fields, width=150)
        """List Buttons"""
        self.taxisurface = ListButton(titles = ["ASPHALT", "CONCRETE", "GRASS", "DIRT", "GRAVEL"], values = [1, 2, 3, 4, 5])
        self.apronsurface = ListButton(titles = ["ASPHALT", "CONCRETE", "GRASS", "DIRT", "GRAVEL"], values = [1, 2, 3, 4, 5])
        self.runwaylist = ListButton(width=100, titles = [], values = [], action=self.update_rwylist)
        self.shouldersurface = ListButton(titles = ["NONE", "ASPHALT", "CONCRETE"], values = [0, 1, 2], action=self.update_fields)
        self.le_rm = ListButton(width=150, titles = ["NONE", "VISUAL", "NON-PRECISION", 
                                "PRECISION", "NON-PRECISION(UK)", "PRECISION(UK)"], values = [0, 1, 2, 3, 4, 5], action=self.update_fields)
        self.he_rm = ListButton(width=150, titles = ["NONE", "VISUAL", "NON-PRECISION", 
                                "PRECISION", "NON-PRECISION(UK)", "PRECISION(UK)"], values = [0, 1, 2, 3, 4, 5], action=self.update_fields)
        self.le_appr_lighting = ListButton(width=150, titles = ["NONE", "ALSF-I", "ALSF-II", 
                                "Calvert", "Calvert ILS Cat II", "SSALR", "SSALF", "SALS", "MALSR",
                                "MALSF", "MALS", "ODALS", "RAIL"], 
                                values = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], action=self.update_fields)
        self.he_appr_lighting = ListButton(width=150, titles = ["NONE", "ALSF-I", "ALSF-II", 
                                "Calvert", "Calvert ILS Cat II", "SSALR", "SSALF", "SALS", "MALSR",
                                "MALSF", "MALS", "ODALS", "RAIL"], 
                                values = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], action=self.update_fields)
        self.le_reil = ListButton(width = 150, titles = ["NONE", "OMNI-DIRECTIONAL", "UNIDIRECTIONAL"],
                        values = [0, 1, 2], action=self.update_fields)
        self.he_reil = ListButton(width = 150, titles = ["NONE", "OMNI-DIRECTIONAL", "UNIDIRECTIONAL"],
                        values = [0, 1, 2], action=self.update_fields)
        """List Button default values"""
        self.taxisurface.value = 1
        self.apronsurface.value = 2
        self.shouldersurface.value = 1
        self.le_rm.value = 3
        self.he_rm.value = 3
        self.le_appr_lighting.value = 12
        self.he_appr_lighting.value = 12
        self.le_reil.value = 0
        self.he_reil.value = 0
        """Command Buttons"""
        osmfile = Button(width = 150, title = 'Open OSM File', color = rgb(0.5, 0, 0), action = self.open_file)
        identify = Button(width = 150, title = 'Identify Runways', color = rgb(0.5, 0, 0), action = self.identify_runways)
        generate = Button(width = 150, title = 'Generate', color = rgb(0.5, 0, 0), action = self.generate)
        dirpath = Button(width = 150, title = 'Set Path', color = rgb(0.5, 0, 0), action = self.set_genpath)
        items = [[label, self.icao, osmfile],
                [label1, None, self.filename],
                [self.taxi_centerlines, self.taxi_centerlights], [self.taxi_edgelines, self.taxi_edgelights],
                [label2, self.taxi_width], [label6, identify], [label7, label8], 
                [self.runwaylist, self.shouldersurface], 
                [self.centerlights, self.edgelights, self.drs], 
                [None, label9, label10, label11], 
                [self.lbl_le_rm, self.le_rm, self.le_appr_lighting, self.le_reil, self.le_tdz], 
                [self.lbl_he_rm, self.he_rm, self.he_appr_lighting, self.he_reil, self.he_tdz],
                [label3], [label4, self.taxisurface], [label5, self.apronsurface], [label12], 
                [label13, self.bldg_height_min, Label(text="-"), self.bldg_height_max],
                [label14, self.terminal_height_min, Label(text="-"), self.terminal_height_max],
                [generate, dirpath]]
        grid = Grid(items, top = 20, left = 20, width = 780, height = 580)
        win = Window(width = 800, height =  600, title = "OSMAirportsX")
        win.add(grid)
        win.add(self.lblgenpath)
        win.show()   
        application().run()
    
    def open_file(self):
        file_type = FileType(name = "OSM XML File", suffix = "osm")
        file_type1 = FileType(name = "OSM XML File", suffix = "xml")
        self.osmfileref = FileDialogs.request_old_file("Open OSM File:",
                default_dir = self.last_dir, file_types = [file_type, file_type1])
        self.filename.text = self.osmfileref.name
        self.last_dir = self.osmfileref.dir
        
    def set_genpath(self):
        self.genpath = FileDialogs.request_old_directory("Set Path:", default_dir = self.last_dir)
        self.lblgenpath.text = self.genpath.path
    
    def update_rwylist(self):
        self.lbl_le_rm.text = self.OurAirportsData.GetLeRunwayNumber(self.runwaylist.value)
        self.lbl_he_rm.text = self.OurAirportsData.GetHeRunwayNumber(self.runwaylist.value)
        self.shouldersurface.value = self.OurAirportsData.GetRunwayShoulderSurface(self.runwaylist.value)
        self.le_rm.value = self.OurAirportsData.GetLeRunwayMarkingCode(self.runwaylist.value)
        self.he_rm.value = self.OurAirportsData.GetHeRunwayMarkingCode(self.runwaylist.value)
        self.le_appr_lighting.value = self.OurAirportsData.GetLeApproachLightingCode(self.runwaylist.value)
        self.he_appr_lighting.value = self.OurAirportsData.GetHeApproachLightingCode(self.runwaylist.value)
        self.le_reil.value = self.OurAirportsData.GetLeREILCode(self.runwaylist.value)
        self.he_reil.value = self.OurAirportsData.GetHeREILCode(self.runwaylist.value)
        self.le_tdz.on = self.OurAirportsData.GetLeTDZCode(self.runwaylist.value)
        self.he_tdz.on = self.OurAirportsData.GetHeTDZCode(self.runwaylist.value)
        self.centerlights.on = self.OurAirportsData.GetRunwayCenterLighting(self.runwaylist.value)
        self.edgelights.on = self.OurAirportsData.GetRunwayEdgeLighting(self.runwaylist.value)
        self.drs.on = self.OurAirportsData.GetRunwayDRS(self.runwaylist.value)
        
    def update_fields(self):
        self.OurAirportsData.SetRunwayShoulderSurface(self.runwaylist.value, self.shouldersurface.value)
        self.OurAirportsData.SetLeRunwayMarkingCode(self.runwaylist.value, self.le_rm.value)
        self.OurAirportsData.SetHeRunwayMarkingCode(self.runwaylist.value, self.he_rm.value)
        self.OurAirportsData.SetLeApproachLightingCode(self.runwaylist.value, self.le_appr_lighting.value)
        self.OurAirportsData.SetHeApproachLightingCode(self.runwaylist.value, self.he_appr_lighting.value)
        self.OurAirportsData.SetLeREILCode(self.runwaylist.value, self.le_reil.value)
        self.OurAirportsData.SetHeREILCode(self.runwaylist.value, self.he_reil.value)
        self.OurAirportsData.SetLeTDZCode(self.runwaylist.value, self.le_tdz.on)
        self.OurAirportsData.SetHeTDZCode(self.runwaylist.value, self.he_tdz.on)
        self.OurAirportsData.SetRunwayCenterLighting(self.runwaylist.value, self.centerlights.on)
        self.OurAirportsData.SetRunwayEdgeLighting(self.runwaylist.value, self.edgelights.on)
        self.OurAirportsData.SetRunwayDRS(self.runwaylist.value, self.drs.on)
        
    def identify_runways(self):
        lst = []
        lst1 = []
        self.OurAirportsData = OurAirportsDataExtractor(self.icao.value)
        for runway in self.OurAirportsData.lstRunways:
            lenum = self.OurAirportsData.GetLeRunwayNumber(runway)
            henum = self.OurAirportsData.GetHeRunwayNumber(runway)
            strrunway = str(lenum) + '/' + str(henum)
            lst.append(strrunway)
            lst1.append(runway)
        self.runwaylist.set_titles(lst)
        self.runwaylist.set_values(lst1)
        self.runwaylist.set_value(lst1[0])
        self.update_rwylist()
        
    def generate(self):
        #p = Process(target=self.execute)
        #p.start()
        self.execute()
        
    def execute(self):
        if not self.genpath:
            path = '.'
        else:
            path = self.genpath.path
        OSMAirportsData = OSMAirportDataExtractor(self.icao.value, file=self.osmfileref.path)
        OXpsc = XPAPTDataCreator(self.icao.value, self.osmfileref, centerlines=self.taxi_centerlines.on, 
                                centerlights=self.taxi_centerlights.on, 
                                edgelines=self.taxi_edgelines.on, 
                                edgelights=self.taxi_edgelights.on, 
                                taxiway_width=int(self.taxi_width.value), 
                                taxiway_type=self.taxisurface.value,
                                apron_type=self.apronsurface.value,
                                ourairportsdata = self.OurAirportsData, 
                                osmdata = OSMAirportsData, genpath = path)
        OXpsc.WriteAptDat()
        DSFObject = DSFDataCreator(self.icao.value, osmdata=OXpsc.OSMAirportsData,
                                    bldg_height=(int(self.bldg_height_min.value), int(self.bldg_height_max.value)), 
                                    terminal_height=(int(self.terminal_height_min.value), 
                                    int(self.terminal_height_max.value)), genpath=path)
        DSFObject.WriteDSF()

if __name__ == "__main__":
    OSMAirportsX()

    


    
