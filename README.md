## Dodd-Frank Swap Reporting Party Determination


### Overview

Dodd-Frank (financial legislation) introduced some reporting requirements for each swap transaction.

Later, regulation was released outlining who is responsible for Rule 45 and Rule 43 reporting.

This is a side-project to work through the logic to determine the reporting party using Python using fake financial data generated with an accompanying script

Source for reporting rules: http://www2.isda.org/attachment/NjE4NA==/Reporting%20Party%20Requirements_16Dec13_Final.pdf

### Testing out the project

+ Step 1: In a clean directory, create a virtual environment using virtualenv with this command
'''
virtualenv venv --no-site-packages
'''

+ Step 2: Git clone the repository into the root project folder and enter the folder


+ Step 3: Install the dependencies for the project
'''
pip install -r requirements.txt
'''

+ Step 4: Run generate_sample_xml.py to generate an xml document containing 100 random swap transactions.
          To generate a different amount of variables, pass an argument when running the file.
          For example, to create 40 transactions:
          '''
          python generate_sample_xml.py 40
          '''
          The result will be written to an xml file in the directory "sample_xml"

+ Step 5: Run parse_transactions.py to process the xml and determine the appropriate reporting party.
		  The result will be written to an xml file in the directory "result_xml"


### Closing note
This is the first pass and just intended for creating a code sample + learn more about Dodd-Frank.




