## Dodd-Frank Swap Reporting Party Determination


### Overview

Dodd-Frank (financial legislation) introduced reporting requirements for swap transaction.

Later, regulation was released outlining who is responsible for Rule 45 and Rule 43 reporting.

This is a side-project to work through the logic to determine the reporting party using Python using fake financial data generated with an accompanying script.

Source for reporting rules: http://www2.isda.org/attachment/NjE4NA==/Reporting%20Party%20Requirements_16Dec13_Final.pdf

### Testing out the project

+ Step 1: In a clean directory, create a virtual environment using virtualenv with this command
> virtualenv venv --no-site-packages

+ Step 1a: To start your virual environment, type:
> source venv/bin/activate


+ Step 2: Git clone the repository into the root project folder and enter the folder


+ Step 3: Install the dependencies for the project
> pip install -r requirements.txt

+ Step 4: Run generate_sample_xml.py to generate an xml document containing 100 random swap transactions.  
The result will be written to an xml file in the directory "sample_xml".
          To generate a different amount of variables, pass an argument when running the script.  
          For example, to create 40 transactions:

>         python generate_sample_xml.py 40

          

+ Step 5: Run parse_transactions.py to process the xml and determine the appropriate reporting party.  
		  The result will be written to an xml file in the directory "result_xml"  
		  To default sample xml is: sample_xml/18_51_2014_07_21.xml  
		  To run a different file, pass an argument when running the script.  
		  For example, to run the file: "sample_xml/foobar.xml"  

>		  python parse_transactions.py sample_xml/foobar.xml