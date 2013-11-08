import sys
from distutils.core import setup


vincludes=[
           'OurAirportsDataExtractor',
           'OSMAirportDataExtractor',
           'DSFDataCreator',
           'XPAPTDataCreator',
           ]

if sys.platform == 'darwin':
    import py2app
    extra_options = dict(
                         setup_requires=['py2app'],
                         options=dict(py2app=dict(
                                      plist = {
                                                'CFBundleName': 'OSMAirportsX',
                                                'CFBundleShortVersionString':'2.0.3', # must be in X.X.X format
                                                'CFBundleVersion': '2.0.3',
                                                },
                                      includes=vincludes,
                                      excludes=['numpy', 'scipy', 'matplotlib', 'email'],
                                      packages=['lxml', 'shapely'])))
    setup(
        name='OSMAirportsX',
        app=['OSMAirportsX.py'],
        data_files=[
            'airports.csv',
            'runways.csv',
            'navaids.csv',
            'airport-frequencies.csv'
        ],
        **extra_options
    )
elif sys.platform == 'win32':
    import GUI.py2exe
    import py2exe
	
    manifest = '''
<?xml version='1.0' encoding='UTF-8' standalone='yes'?>
<assembly xmlns='urn:schemas-microsoft-com:asm.v1' manifestVersion='1.0'>
  <trustInfo xmlns="urn:schemas-microsoft-com:asm.v3">
    <security>
      <requestedPrivileges>
        <requestedExecutionLevel level='asInvoker' uiAccess='false' />
      </requestedPrivileges>
    </security>
  </trustInfo>
  <dependency>
    <dependentAssembly>
      <assemblyIdentity
     type='win32'
     name='Microsoft.VC90.CRT'
     version='9.0.21022.8'
     processorArchitecture='*'
     publicKeyToken='1fc8b3b9a1e18e3b' />
    </dependentAssembly>
  </dependency>
  <dependency>
    <dependentAssembly>
      <assemblyIdentity
         type="win32"
         name="Microsoft.Windows.Common-Controls"
         version="6.0.0.0"
         processorArchitecture="*"
         publicKeyToken="6595b64144ccf1df"
         language="*" />
    </dependentAssembly>
  </dependency>
</assembly>
    '''
    extra_options = dict(
                         setup_requires=['py2exe'],
                         options = dict(
                            py2exe=dict(
                            includes=vincludes,
                            excludes=['numpy', 'scipy', 'matplotlib', 'email'],
                            packages=['lxml', 'shapely'])))
    setup(
        name='OSMAirportsX',
        app=['OSMAirportsX.py'],
        console=[dict(
			script='OSMAirportsX.py',
			other_resources= [(24,1,manifest)]
			)],
        data_files=[
            'airports.csv',
            'runways.csv',
            'navaids.csv',
            'airport-frequencies.csv',
            'geos_c.dll'
        ],
        **extra_options
    )



