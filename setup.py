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
                         options=dict(py2app=dict(argv_emulation=True,
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
        window=['OSMAirportsX.py'],
        data_files=[
            'airports.csv',
            'runways.csv',
            'navaids.csv',
            'airport-frequencies.csv',
            'geos_c.dll'
        ],
        **extra_options
    )



