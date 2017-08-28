CsdlCsvParser [parser.py] v1 using Modgrammar
Created by Joe Bremner (Dell summer intern, 2017)
*** README ***

Description: a Python 3 script intended to convert CSDL (XML) schema files into CSV files in order to ease understanding of the files' contents

Dependencies:
- Python 3 (works on all versions)
- pip (required to install modgrammar)
- Modgrammar

How to run (command line):
> curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
> python get-pip.py
> pip install modgrammar
(alternatively: download Modgrammar from http://pypi.python.org/pypi/modgrammar)
> python parser.py [desired CSDL file]

Output: [CSDL entity name].csv in local folder

Notes:
- users should ensure there are no spaces in property names in CSDL file
- users should ensure there is no newline at the end of CSDL file
- write privileges must be enabled in folder