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
import os.path, sys, time
from OurAirportsDataExtractor import OurAirportsDataExtractor
from OSMAirportDataExtractor import OSMAirportDataExtractor
from XPAPTDataCreator import XPAPTDataCreator
from DSFDataCreator import DSFDataCreator
from GUI import Window, CheckBox, Button, Label, TextField, rgb, application, FileDialogs, Grid, ListButton, Dialog, ModalDialog, Task
from GUI.Files import FileType, DirRef, FileRef
from GUI.Alerts import stop_alert, note_alert
from GUI.StdMenus import basic_menus, file_cmds, help_cmds, edit_cmds, print_cmds
from multiprocessing import Process, Queue

def execute(q, genpath, icao, osmfileref, OurAirportsData, 
    centerlines, centerlights, edgelines, edgelights, taxi_width,
    taxisurface, apronsurface, apron_perimeterlights, apron_floodlights, bldg_height,
    terminal_height):
        if not genpath:
            path = '.'
        else:
            path = genpath.path
        OSMAirportsData = OSMAirportDataExtractor(icao, file=osmfileref.path, ourairportsdata = OurAirportsData)
        retVal = OSMAirportsData.ExtractData()
        if retVal == -1:
            q.put("Did not find one or more runways in OSM Data!  \
                        May be incorrect/outdated. The generation will proceed anyway.")
        OXpsc = XPAPTDataCreator(icao, osmfileref, centerlines=centerlines, 
                                centerlights=centerlights, 
                                edgelines=edgelines, 
                                edgelights=edgelights, 
                                taxiway_width=int(taxi_width), 
                                taxiway_type=taxisurface,
                                apron_type=apronsurface,
                                apron_perimeterlights=apron_perimeterlights,
                                apron_floodlights=apron_floodlights,
                                ourairportsdata = OurAirportsData, 
                                osmdata = OSMAirportsData, genpath = path)
        OXpsc.WriteFileHeader()
        OXpsc.WriteAPTHeader()
        q.put("Writing Runway Definitions...")
        retVal = OXpsc.WriteRunwayDefs()
        if retVal == -1:
            q.put("Did not find runway in OSM Data!  \
                        May be incorrect/outdated. Correct the problem to proceed further")
            return -1
        q.put("Writing PAPI/VASI Definitions...")
        OXpsc.WritePapiDefs()
        q.put("Writing Taxiway Definitions...")
        OXpsc.WriteTaxiwaySurfaceDefs()
        if OXpsc.centerlines:
            q.put("Writing Taxiway Centerlines...")
            OXpsc.WriteTaxiwayCenterLineDefs()
        q.put("Writing Service Road Definitions...")
        OXpsc.WriteServiceRoadDefs()
        q.put("Writing Service Road Centerlines...")
        OXpsc.WriteServiceRoadCenterLineDefs()
        q.put("Writing Holding Position Definitions...")
        OXpsc.WriteHoldingPositionLineDefs()
        q.put("Writing Paved Surface Definitions...")
        OXpsc.WritePavedSurfaceDefs()
        #OXpsc.WriteTransparentSurfaceDefs()
        q.put("Writing Airport Boundary Definitions...")
        OXpsc.WriteAirportBoundaryDefs()
        q.put("Adding Beacon...")
        OXpsc.WriteBeaconDefs()
        q.put("Adding Windsocks...")
        OXpsc.WriteWindsockDefs()
        q.put("Adding Taxi Starts...")
        OXpsc.WriteTaxiStartDefs()
        q.put("Adding Frequencies...")
        OXpsc.WriteFreqDefs()
        OXpsc.close()
        DSFObject = DSFDataCreator(icao, osmdata=OSMAirportsData,
                                    bldg_height=bldg_height, 
                                    terminal_height=terminal_height, genpath=path)
        q.put("Create Terminals...")
        DSFObject.CreateTerminals()
        q.put("Create Gates...")
        DSFObject.CreateGates()
        q.put("Create Hangars...")
        DSFObject.CreateHangars()
        q.put("Create Buildings...")
        DSFObject.CreateBldgs()
        q.put("Create Towers...")
        DSFObject.CreateTowers()
        q.put("Create Fences...")
        DSFObject.CreateFences()
        if apron_floodlights == True:
            DSFObject.CreateApronFloodLights()
        DSFObject.close()
        return 0

class OSMAirportsXWindow(Window):

    def setup_menus(self, m):
        m.about_cmd.enabled = 1
        
    def about_cmd(self):
        dlog = Dialog(width = 600, height = 480, closable = True)
        lbl = Label(text = "OSMAirportsX v1.1")
        lbl1 = Label(text = "by Shankar Giri V.")
        str = "This software is available under an open-source license. \nVisit https://bitbucket.org/girivs/osmairportsx for more information."
        lbl2 = Label(text = str)
        lbl3 = Label(text = "(c) 2013, Shankar Giri V.")
        lbl4 = Label(text = "This software uses python and third-party modules. Details below: ")
        lbl5 = Label(text = "lxml")
        lbl6 = Label(text = "XML and HTML with Python: http://lxml.de")
        lbl7 = Label(text = "shapely")
        lbl8 = Label(text = "PostGIS-ish operations outside a database context\nfor Pythoneers and Pythonistas. https://pypi.python.org/pypi/Shapely")
        lbl9 = Label(text = "PyGUI")
        lbl10 = Label(text = "A cross-platform pythonic GUI API:\nhttp://www.cosc.canterbury.ac.nz/greg.ewing/python_gui/")
        lbl11 = Label(text = "This tool generates data based on information extracted from openstreetmaps.org. \n\
This data is not provided as part of the tool. Users have to export this data themselves. \n\
This data is available under the Open Database License (ODbL). - See more at: \n\
http://opendatacommons.org/licenses/odbl/1.0/ \n\
This tool uses data extracted from OurAirports.com, an open-aviation data website,\n\
where airport data is released under public domain. See more at: \n\
http://www.ourairports.com/data/")
        dlog.place(lbl, left = 20, top = 20)
        dlog.place(lbl1, left = 20, top = lbl.bottom + 20)
        dlog.place(lbl2, left = 20, top = lbl1.bottom + 20)
        dlog.place(lbl3, left = 20, top = lbl2.bottom + 20)
        dlog.place(lbl11, left = 20, top = lbl3.bottom + 20)
        dlog.place(lbl4, left = 20, top = lbl11.bottom + 20)
        items = [[lbl5, lbl6], [lbl7, lbl8], [lbl9, lbl10]]
        grid = Grid(items, top = lbl4.bottom + 20, left = 20, width = dlog.width - 40, height = 400)
        dlog.add(grid)
        dlog.show()

class OSMAirportsX(object):
    
    def __init__(self):
        self.osmfileref = ''
        self.genpath = None
        self.OurAirportsData = None
        self.proc = None
        self.timer = None
        self.start = 0
        self.last_dir = DirRef(os.path.expanduser("~"))
        #self.last_dir = DirRef(path = os.path.abspath(os.path.dirname(sys.argv[0])))
        self.genpath = self.last_dir
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
        label15 = Label(text = "Apron Settings:", color = rgb(0, 0.5, 0))
        self.lblgenpath = Label(text = "Generation Path: ", width=400)
        self.filename = Label(text = "Filename: ", width = 150) 
        self.lbl_le_rm = Label(width=100, text = "")
        self.lbl_he_rm = Label(width=100, text = "")
        self.status_label = None
        """Text Fields"""
        self.icao = TextField(width = 100)
        self.taxi_width = TextField(width = 100, value = '32')
        self.bldg_height_min = TextField(width = 100, value = '20')
        self.bldg_height_max = TextField(width = 100, value = '50')
        self.terminal_height_min = TextField(width = 100, value = '50')
        self.terminal_height_max = TextField(width = 100, value = '100')
        """Check Boxes"""
        self.taxi_centerlines = CheckBox(title = "Centerlines", on = 1, width=150)
        self.taxi_centerlights = CheckBox(title = "Centerlights",  on = 1, width=150)
        self.taxi_edgelines = CheckBox(title = "Edgelines", on = 1, width=150)
        self.taxi_edgelights = CheckBox(title = "Edgelights", on = 1, width=150)
        self.apron_perimeterlights = CheckBox(title = "Perimeter Lights", on = 0, width=150)
        self.apron_floodlights = CheckBox(title = "Flood Lights", on = 0, width=150)
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
        self.btnIdentify = Button(width = 150, title = 'Identify Runways', color = rgb(0.5, 0, 0), action = self.identify_runways, enabled = 0)
        self.btnGenerate = Button(width = 150, title = 'Generate', color = rgb(0.5, 0, 0), action = self.generate, enabled = 0)
        dirpath = Button(width = 150, title = 'Set Path', color = rgb(0.5, 0, 0), action = self.set_genpath)
        items = [[label, self.icao, osmfile, self.filename],
                [label1, None, label15],
                [self.taxi_centerlines, self.taxi_centerlights, self.apron_perimeterlights], 
                [self.taxi_edgelines, self.taxi_edgelights, self.apron_floodlights],
                [label2, self.taxi_width], [label6, self.btnIdentify], [label7, label8], 
                [self.runwaylist, self.shouldersurface], 
                [self.centerlights, self.edgelights, self.drs], 
                [None, label9, label10, label11], 
                [self.lbl_le_rm, self.le_rm, self.le_appr_lighting, self.le_reil, self.le_tdz], 
                [self.lbl_he_rm, self.he_rm, self.he_appr_lighting, self.he_reil, self.he_tdz],
                [label3], [label4, self.taxisurface], [label5, self.apronsurface], [label12], 
                [label13, self.bldg_height_min, Label(text="-"), self.bldg_height_max],
                [label14, self.terminal_height_min, Label(text="-"), self.terminal_height_max],
                [self.btnGenerate, dirpath]]
        grid = Grid(items, top = 20, left = 20, width = 780, height = 580)
        self.win = OSMAirportsXWindow(width = 800, height =  600, title = "OSMAirportsX", resizable = False, zoomable = False)
        self.win.add(grid)
        self.win.place(self.lblgenpath, left = dirpath.right + 20, top = dirpath.bottom)
        self.win.show()
        app = application() 
        app.menus = basic_menus(exclude = file_cmds + edit_cmds + print_cmds) 
        app.run()
    
    def open_file(self):
        file_type = FileType(name = "OSM XML File", suffix = "osm")
        file_type1 = FileType(name = "OSM XML File", suffix = "xml")
        self.osmfileref = FileDialogs.request_old_file("Open OSM File:",
                default_dir = self.last_dir, file_types = [file_type, file_type1])
        if self.osmfileref:
            self.filename.text = self.osmfileref.name
            self.last_dir = self.osmfileref.dir
            self.btnIdentify.enabled = 1
        
    def set_genpath(self):
        self.genpath = FileDialogs.request_old_directory("Set Path:", default_dir = self.genpath)
        if self.genpath:
            self.lblgenpath.text = self.genpath.path
    
    def update_rwylist(self):
        self.lbl_le_rm.text = self.OurAirportsData.GetLeRunwayNumber(self.runwaylist.value)
        self.lbl_he_rm.text = self.OurAirportsData.GetHeRunwayNumber(self.runwaylist.value)
        if self.lbl_he_rm.text[-1] == 'W' or self.lbl_le_rm.text[-1] == 'W':
            self.le_rm.enabled = 0
            self.he_rm.enabled = 0
            self.shouldersurface.enabled = 0
            self.le_appr_lighting.enabled = 0
            self.he_appr_lighting.enabled = 0
            self.le_reil.enabled = 0
            self.he_reil.enabled = 0
            self.le_tdz.enabled = 0
            self.he_tdz.enabled = 0
            self.centerlights.enabled = 0
            self.edgelights.enabled = 0
            self.drs.enabled = 0
        else:
            self.le_rm.enabled = 1
            self.he_rm.enabled = 1
            self.shouldersurface.enabled = 1
            self.le_appr_lighting.enabled = 1
            self.he_appr_lighting.enabled = 1
            self.le_reil.enabled = 1
            self.he_reil.enabled = 1
            self.le_tdz.enabled = 1
            self.he_tdz.enabled = 1
            self.centerlights.enabled = 1
            self.edgelights.enabled = 1
            self.drs.enabled = 1
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
        if not self.OurAirportsData.lstRunways:
            self.icao.text = ''
            stop_alert("ICAO not found in database! Try again.")
            return
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
        self.btnGenerate.enabled = 1
        
    def generate(self):
        self.q = Queue()
        self.timer = Task(self.check_task, 1.0, True)
        icao = self.icao.text
        centerlines = self.taxi_centerlines.on
        centerlights = self.taxi_centerlights.on
        edgelines = self.taxi_edgelines.on
        edgelights = self.taxi_edgelights.on
        taxi_width = self.taxi_width.value
        taxisurface = self.taxisurface.value
        apronsurface = self.apronsurface.value
        apron_perimeterlights = self.apron_perimeterlights.on
        apron_floodlights = self.apron_floodlights.on
        bldg_height=(int(self.bldg_height_min.value), int(self.bldg_height_max.value))
        terminal_height=(int(self.terminal_height_min.value), int(self.terminal_height_max.value))
        self.proc = Process(target=execute, args=(self.q, self.genpath, icao, 
            self.osmfileref, self.OurAirportsData, centerlines, 
            centerlights, edgelines, edgelights, taxi_width, taxisurface, 
            apronsurface, apron_perimeterlights, apron_floodlights, bldg_height, terminal_height))
        self.proc.start()
        self.status = ModalDialog(width = 400, height = 80, closable = False)
        self.lbl = Label(text = "Extracting OSM Data...", width = 360)
        self.elapsed = Label(text = "Elapsed Time: ", width = 360)
        self.status.place(self.lbl)
        self.status.place(self.elapsed, left = self.lbl.left, top = self.lbl.top + 40)
        self.status.center()
        self.start = time.time()
        self.status.show()

    def check_task(self):
        if not self.proc.is_alive():
            self.timer.stop()
            del self.timer
            note_alert('Airport scenery generated.')
            self.status.destroy()
            del self.status
        else:
            elapsed = (time.time() - self.start)
            if not self.q.empty():
                self.lbl.text = self.q.get()
            self.elapsed.text = "Elapsed Time: " + str(int(elapsed+0.5))
        
    
        
if __name__ == "__main__":
    OSMAirportsX()

    


    
