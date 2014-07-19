from lxml import etree
import string as string

'''
This script creates sample swap transactions in XML format.
The default is 100 but you can pass in another amount
'''

def generate_samples(no_transactions=100):
	'''
	Creates root node, begins sample generation process,
	saves result to an xml file
	'''
	
	# Create the parent element
	transactions = etree.Element("transactions")

	count = 0
	while count < no_transactions:
		try:
			get_transaction()
			count += 1
		except:
			break

	# Write transactions to file


def get_transaction():
	'''
	Generates a swap transaction transaction.
	'''

	# Create entities parent element
	entities = etree.Element("entities")

	# Adds two entity elements to entities element
	entities.append(get_entity())
	entities.append(get_entity())

	# create a swap element
	swap = entities.append(get_swap(entities))

	# Create transaction parent element
	swap = etree.Element('transaction')

	# Add nodes to parent 

	# Create asset_type (pass entities to a function that creates the appropriate asset type)





def get_entity():
	'''
	Creates a random entity element.
	'''
	available_countries = ['USA', 'UK', 'FRA', 'JPN', 'GER', 'SAFR', 'NGR', 'MEX', 'ARG']
	available_string = string.ascii_uppercase + string.digits
	entity_types = ['SD', 'MSP', 'End User']

	lei = ''
	# Generate a twenty digit LEI
	while len(lei) < 20:
		lei += available_string[randint(0, len(available_string)-1)]

	# Give USA a higher chance of being selected as the country of entity
	if randint(1,5) % 2 == 0:
		country = 'USA'
	else:
		# select entity country
		country = available_countries[randint(0, len(available_countries)-1)]

	# Select whether entity is a financial institution - 66.7% chance
	financial_entity = 'True' if randint(2, 4) % 2 == 0 else 'False'
	if financial_entity == 'True':
		entity_type = entity_types[randint(0,2)]
	else:
		# Make sure that only a financial institution has to be an SD or MSP
		entity_type = "End User"

	# Create entity parent element
	entity = etree.Element("entity")

	# Create and populate child elements
	lei_element = etree.Element("lei")
	lei_element.text = lei

	country_element = etree.Element("country")
	country_element.text = country

	financial_entity_element = etree.Element("financial_entity").text(financial_entity)
	financial_entity_element.text = financial_entity

	entity_type_element = etree.Element("entity_type")
	entity_type_element.text = entity_type

	# Append child elements to parent (entity)
	entity.append(lei_element)
	entity.append(country_element)
	entity.append(financial_entity_element)
	entity.append(entity_type_element)

	# return entity element with child nodes included
	return entity


def get_swap(entities):
	'''
	Uses the entities created to construct a random swap element
	'''
	
	# Create available options for facilities, asset classes, and lei
	available_facilities = ['SEF', 'DCM', 'None']
	available_asset_classes = ['rates', 'credit', 'equity', 'commodity', 'fx']
	available_lei = []
	country_list = []

	# populate lei and country list
	for element in entities.iter('entity'):
		available_lei.append(element.find('lei').text)
		country_list.append(element.find('country').text)

	# Check to make sure at least one entity is in USA
	one_USA = False
	for country in country_list:
		if country == 'USA':
			one_USA = True
			break

	# Assign facility based on value of one_USA - this makes sure if both
	# entities are out of US; the facility will be SEF or DCM
	if not one_USA:
		facility = available_facilities[randint(0, 1)]
	else:
		facility = available_facilities[randint(0, len(available_facilities)-1)]

	# Assign seller
	seller = available_lei[randint(0, len(available_lei)-1)]

	# Assign asset_class
	asset_class = available_asset_classes[(0, len(available_asset_classes)-1)]

	# Create swap parent element
	swap = etree.Element('swap')

	# Create and populate child elements
	facility_element = etree.Element('facility')
	facility_element.text = facility

	seller_element = etree.Element('seller')
	seller_element.text = seller

	asset_class_element = etree.Element('asset_class')
	asset_class_element.text = asset_class


	# Append child elements to parent (swap)
	swap.append(facility_element)
	swap.append(seller_element)
	swap.append(asset_class_element)

	# return the swap element with child nodes included
	return swap
