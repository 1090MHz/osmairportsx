import glob
import os, sys
from OurAirportsDataExtractor import OurAirportsDataExtractor
from OSMAirportDataExtractor import OSMAirportDataExtractor
from XPAPTDataCreator import XPAPTDataCreator
from DSFDataCreator import DSFDataCreator


genpath = './test'
OurAirportsData = None
runwaylist = []

        
def update_fields(OurAirportsData, shouldersurface, le_rm, he_rm, le_appr_lighting, 
                    he_appr_lighting, le_reil, he_reil, le_tdz, he_tdz, centerlights,
                    edgelights, drs):
    for runwaylist in OurAirportsData.lstRunways:
        OurAirportsData.SetRunwayShoulderSurface(runwaylist, shouldersurface)
        OurAirportsData.SetLeRunwayMarkingCode(runwaylist, le_rm)
        OurAirportsData.SetHeRunwayMarkingCode(runwaylist, he_rm)
        OurAirportsData.SetLeApproachLightingCode(runwaylist, le_appr_lighting)
        OurAirportsData.SetHeApproachLightingCode(runwaylist, he_appr_lighting)
        OurAirportsData.SetLeREILCode(runwaylist, le_reil)
        OurAirportsData.SetHeREILCode(runwaylist, he_reil)
        OurAirportsData.SetLeTDZCode(runwaylist, le_tdz)
        OurAirportsData.SetHeTDZCode(runwaylist, he_tdz)
        OurAirportsData.SetRunwayCenterLighting(runwaylist, centerlights)
        OurAirportsData.SetRunwayEdgeLighting(runwaylist, edgelights)
        OurAirportsData.SetRunwayDRS(runwaylist, drs)

def identify_runways(icao, OurAirportsData):
    taxisurface = 1
    apronsurface = 2
    shouldersurface = 1
    le_rm = 3
    he_rm = 3
    le_appr_lighting = 12
    he_appr_lighting = 12
    le_reil = 0
    he_reil = 0
    le_tdz = True
    he_tdz = True
    drs = True
    
    if not OurAirportsData.lstRunways:
        icao.text = ''
        sys.exit("ICAO not found in database! Try again.")
        return
    update_fields(OurAirportsData, shouldersurface, le_rm, he_rm, le_appr_lighting, 
                    he_appr_lighting, le_reil, he_reil, le_tdz, he_tdz, centerlights, 
                    edgelights, drs)

def execute(icao, osmfileref, ourairportsdata, taxi_centerlines, taxi_centerlights, 
        taxi_edgelines, taxi_edgelights, taxi_width, taxisurface, apronsurface, 
        apron_perimeterlights, apron_floodlights, bldg_height_min, bldg_height_max,
        terminal_height_min, terminal_height_max):
    if not genpath:
        path = '.'
    else:
        path = genpath
    identify_runways(icao, ourairportsdata)
    OSMAirportsData = OSMAirportDataExtractor(icao, file=osmfileref, ourairportsdata = ourairportsdata)
    retVal = OSMAirportsData.ExtractData()
    OXpsc = XPAPTDataCreator(icao, osmfileref, centerlines=taxi_centerlines, 
                            centerlights=taxi_centerlights, 
                            edgelines=taxi_edgelines, 
                            edgelights=taxi_edgelights, 
                            taxiway_width=int(taxi_width), 
                            taxiway_type=taxisurface,
                            apron_type=apronsurface,
                            apron_perimeterlights=apron_perimeterlights,
                            apron_floodlights=apron_floodlights,
                            ourairportsdata = ourairportsdata, 
                            osmdata = OSMAirportsData, genpath = path)
    OXpsc.WriteFileHeader()
    OXpsc.WriteAPTHeader()
    retVal = OXpsc.WriteRunwayDefs()
    OXpsc.WritePapiDefs()
    OXpsc.WriteTaxiwaySurfaceDefs()
    if OXpsc.centerlines:
        OXpsc.WriteTaxiwayCenterLineDefs()
    OXpsc.WriteServiceRoadDefs()
    OXpsc.WriteServiceRoadCenterLineDefs()
    OXpsc.WriteHoldingPositionLineDefs()
    OXpsc.WritePavedSurfaceDefs()
    #OXpsc.WriteTransparentSurfaceDefs()
    OXpsc.WriteAirportBoundaryDefs()
    OXpsc.WriteBeaconDefs()
    OXpsc.WriteWindsockDefs()
    OXpsc.WriteTaxiStartDefs()
    OXpsc.WriteFreqDefs()
    OXpsc.close()
    DSFObject = DSFDataCreator(icao, osmdata=OSMAirportsData,
                                bldg_height=(int(bldg_height_min), int(bldg_height_max)), 
                                terminal_height=(int(terminal_height_min), 
                                int(terminal_height_max)), genpath=path)
    DSFObject.CreateTerminals()
    DSFObject.CreateGates()
    DSFObject.CreateHangars()
    DSFObject.CreateBldgs()
    DSFObject.CreateTowers()
    DSFObject.CreateFences()
    if apron_floodlights == True:
        DSFObject.CreateApronFloodLights()
    DSFObject.close()
    return 0
        
if __name__ == "__main__":
    if len(sys.argv) == 2:
        filelist = sys.argv[1:]
    else:
        filelist =  glob.glob("*.osm") 
    for files in filelist:
        fileName, fileExtension = os.path.splitext(files)
        icao = fileName.upper()
        centerlights = True
        centerlines = True
        edgelines = True
        edgelights = True
        taxiway_width = 32
        taxiway_type = 1
        apron_type = 2
        apron_perimeterlights = False
        apron_floodlights = False
        bldg_height_min = 10
        bldg_height_max = 50
        terminal_height_min = 50
        terminal_height_max = 80
        ourairportsdata = OurAirportsDataExtractor(icao)
        execute(icao, files, ourairportsdata, centerlines, centerlights, 
                edgelines, edgelights, taxiway_width, taxiway_type, apron_type, 
                apron_perimeterlights, apron_floodlights, bldg_height_min, 
                bldg_height_max, terminal_height_min, terminal_height_max)
