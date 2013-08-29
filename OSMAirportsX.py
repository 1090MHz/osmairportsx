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
from optparse import OptionParser
from OurAirportsDataExtractor import OurAirportsDataExtractor
from OSMAirportDataExtractor import OSMAirportDataExtractor
from XPAPTDataCreator import XPAPTDataCreator
from DSFDataCreator import DSFDataCreator

usage = "usage: %prog [options] arg1 arg2"
parser = OptionParser(usage)
parser.add_option("--Ttype",
                  action="store", type="string", dest="taxi_type", default="ASPHALT",
                  help="Set taxiway type (ASPHALT, CONCRETE, GRASS, DIRT, GRAVEL)")
parser.add_option("--Tcenterlines",
                  action="store_true", dest="taxi_centerlines", default=False,
                  help="Generate Taxiway centerlines")
parser.add_option("--Tcenterlights",
                  action="store_true", dest="taxi_centerlights", default=False,
                  help="Generate Taxiway centerline lights")
parser.add_option("--Bheight",
                  action="store", type="float", nargs=2, dest="bheight", default=(20, 30),
                  help="Set building height range min, max")
parser.add_option("--ATheight",
                  action="store", type="float", nargs=2, dest="atheight", default=(30, 40),
                  help="Set airport terminal building height range min, max")

(options, args) = parser.parse_args()
print options, args
if len(args) != 2:
    parser.print_help()   
    parser.error("Two arguments required!")
elif len(args[0])!=4:
    parser.error("ICAO should be 4 characters")     

if __name__ == "__main__":
    OurAirportsData = OurAirportsDataExtractor(icao=args[0])
    OSMAirportsData = OSMAirportDataExtractor(icao=args[0], file=args[1])
    OXpsc = XPAPTDataCreator(args[0], args[1], centerlines=options.taxi_centerlines, 
                            centerlights=options.taxi_centerlines, taxiway_type=options.taxi_type, 
                            ourairportsdata = OurAirportsData, osmdata = OSMAirportsData)
    OXpsc.WriteFileHeader()
    OXpsc.WriteAPTHeader()
    OXpsc.WriteRunwayDefs()
    OXpsc.WritePapiDefs()
    OXpsc.WriteTaxiwaySurfaceDefs()
    OXpsc.WriteTaxiwayCenterLineDefs()
    OXpsc.WriteServiceRoadDefs()
    OXpsc.WritePavedSurfaceDefs()
    OXpsc.WriteAirportBoundaryDefs()
    OXpsc.WriteBeaconDefs()
    OXpsc.WriteFreqDefs()
    OXpsc.close()
    DSFObject = DSFDataCreator(icao=args[0], osmdata=OXpsc.OSMAirportsData,
                                bldg_height=options.bheight, terminal_height=options.atheight )
    DSFObject.WriteFileHeader()
    DSFObject.WriteSceneryBoundaries()
    DSFObject.DefineFacadeObjects()
    DSFObject.CreateTerminals()
    DSFObject.CreateHangars()
    DSFObject.CreateBldgs()
    DSFObject.CreateFences()
    DSFObject.close()
    
