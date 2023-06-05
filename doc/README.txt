# Libraries required to be installed in advance to run staging.py
  - pandas	1.4.2


# dir containing codes

  /code
    |- GUI/
      |- build/
      |- dist/
        |- app/
          |- LightIntensityPlot/	# A folder spared to hold individual plotting of the time course of light raw intensity at some wavelength, HbO2 or HbR for some channel
          |- GrandAvgGroup/	# A folder spared to hold grand averaged per channel timecourse pictorial representations of the HbO2 and HbR for a group with dispersion regions
          |- BoxPlotSubject/	# A folder spared to hold boxplots comparing the distribution of either HbO2 or HbR concentrations for two intervals of time for a subject
          |- BoxPlotGroup/	# A folder spared to hold boxplots comparing the distribution of either HbO2 or HbR concentrations for two intervals of time for a group
          |- app.exe	# An Executable file recompiled from a Flask project, a browser based intuitive GUI for querying
    |- CreateDB.sql	# An SQL source file to create the database "smdvault"
    |- dataVault.sql	# An SQL source file to build an Enterprise layer for data storing and management
    |- InfoMart.sql	# An SQL source file to build an Information Mart layer providing abundant support for rudimentary database querying
    |- staging.py	# A Python file to implement ETL process


# Instructions to run the code

**Remember to change all the '\' in the windows filepaths into '/' before pasting them to PostgreSQL shell.**

## Step Zero	Run CreateDB.sql, then switch to database "smdvault" in shell(with "\c smdvault").
## Step One	Run dataVault.sql and InfoMart.sql in Shell.
## Step Two	Install pandas and run staging.py in any python IDE.
## Step Three	To access GUI, go find "../GUI/dist/app/app.exe", then double click "app.exe" and check "http://127.0.0.1:5000/" in a browser (Chrome is recommended). More detailed instructions will be available on the webpage.