from sys import argv
from lxml import etree
import string as string
from random import randint, sample
from datetime import datetime

'''
This script creates sample swap transactions in XML format.
The default is 100 but you can pass in another amount
'''

def generate_samples(no_transactions=100):
    '''
    Creates root node, begins sample generation process,
    saves result to an xml file
    '''
    print 'starting..'
    
    # Create the parent element
    transactions = etree.Element("transactions")

    count = 0
    while count < no_transactions:
        transactions.append(get_transaction())
        count += 1

    # Prepare to write to file
    transactions_string = etree.ElementTree(transactions)

    # Create file name from timestamp
    timestamp = 'sample_xml/' + datetime.now().strftime("%H_%M_%Y_%m_%d") + ".xml"

    # Write transactions to file
    transactions_string.write(timestamp, pretty_print=True, xml_declaration=True)

    # Notify of completion
    print('Complete...')



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
    swap = get_swap(entities)

    # Create transaction parent element
    transaction = etree.Element('transaction')

    # Add nodes to parent
    transaction.append(entities)
    transaction.append(swap)

    # Generate unique swap ID
    available_string = string.ascii_uppercase + string.digits

    unique_swap_id = ''
    # Generate a twenty digit LEI
    while len(unique_swap_id) < 15:
        unique_swap_id += available_string[randint(0, len(available_string)-1)]

    # Create uniqe_identifier element
    unique_identifier_element = etree.Element('unique_swap_id')
    unique_identifier_element.text = unique_swap_id

    # Add swap ID to transaction
    transaction.append(unique_identifier_element)

    # Return transaction element
    return transaction

    
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

    financial_entity_element = etree.Element("financial_entity")
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

    # get the available leis and countries
    lei_countries = get_populate_lei_country(entities)
    available_lei = lei_countries['lei']
    country_list = lei_countries['countries']

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
    asset_class = available_asset_classes[randint(0, len(available_asset_classes)-1)]

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

    # Create asset_type element (pass entities to a function that creates the appropriate asset type)
    asset_type = populate_asset_type(asset_class, available_lei)
    # import pdb; pdb.set_trace()

    # Append asset_type element
    swap.append(asset_type)

    # return the swap element with child nodes included
    return swap


def populate_asset_type(asset_class, available_lei):
    '''
        Takes available lei and returns an asset_type element
    '''

    available_asset_types = {'rates': create_swap_rates,
                             'credit': create_swap_credit,
                             'equity': create_swap_equity,
                             'commodity': create_swap_commodity,
                             'fx': create_swap_fx}

    # Select a random asset_type and get send off to corresponding creation function
    asset_type_element = available_asset_types[asset_class](available_lei)

    # Return asset_type element
    return asset_type_element


def create_swap_rates(available_lei):
    '''
        Create a swap for asset_class == 'swap_rate'
    '''
    available_trade_types = ['cap_floor', 'debt_option', 'exotic', 'fra', 'irs_basis',
                             'irs_fix_fix', 'irs_fix_float', 'ir_swap_inflation', 'ir_swap_ois',
                             'swaption', 'xccy_basis', 'xccy_fix_fix', 'xccy_fix_float']

    # Choose random trade type
    trade_type = available_trade_types[randint(0, len(available_trade_types)-1)]

    # Create root element and append the trade type
    rates_element = etree.Element('rates')

    # Add trade_type to rates_element
    trade_type_element = etree.Element('trade_type')
    trade_type_element.text = trade_type

    # Append trade_type element to root (rates_element)
    rates_element.append(trade_type_element)

    # Option_buyer (LEI) is required if trade_type is a debt_option or swaption
    if trade_type in ['debt_option', 'swaption']:
        option_buyer = available_lei[randint(0, len(available_lei)-1)]

        # Create option buyer element and append to rates element
        option_buyer_element = etree.Element('option_buyer')
        option_buyer_element.text = option_buyer

        rates_element.append(option_buyer_element)


    # Check for trade type and designate fixed_rate_payer as necessary
    if trade_type in ['cap_floor', 'fra', 'irs_fix_float',
                      'irswap_inflation', 'irs_swap_ois', 'fix_float']:
        
        # Create a copy of the available_lei list
        available_lei2 = available_lei

        # Create an element for fixed rate payer
        fixed_rate_payer_element = etree.Element('fixed_rate_payer')

        # Get a fixed rate payer (random) and append to fixed_rate_payer element
        payer1 = available_lei2[randint(0, len(available_lei2)-1)]
        fixed_rate_payer_element.text = payer1

        # Append fixed rate element to rates_element (root)
        rates_element.append(fixed_rate_payer_element)

        # Cap_floor trades can have two fixed rate payers.
        # In 33% of the time, add a second fixed rate payer if the trade_type is cap_floor
        if trade_type in ['cap_floor', 'ir_swap_inflation'] and randint(1, 3) % 2 == 0:
            available_lei2.remove(payer1)
            if len(available_lei2) > 0:
                fixed_rate_payer_element2 = etree.Element('fixed_rate_payer')
                fixed_rate_payer_element2.text = available_lei2[randint(0, len(available_lei2)-1)]
                rates_element.append(fixed_rate_payer_element2)

    # Return Rates element
    return rates_element


def create_swap_equity(available_lei):
    '''
    Create a swap for asset_type == equity

    '''
    # Create root element
    equity_element = etree.Element('equity')

    # Creates the negative_affirmation element and populates it (50-50)
    # Append to root element (credit_element)
    negative_affirmation_element = etree.Element('negative_affirmation')
    negative_affirmation_element.text = available_lei[randint(0, len(available_lei)-1)] if randint(2,3) % 2 == 0 else 'False'
    equity_element.append(negative_affirmation_element)

    # Creates a 33% chance of not having a 'performance_seller'
    # Adds the agreed Reporting Party (RP) to the root element
    # Append to root element (equity_element)
    if randint(1,3) % 2 == 0 and negative_affirmation_element.text == 'False':
        agreed_rp_element = etree.Element('agreed_rp')
        agreed_rp_element.text = available_lei[randint(0, len(available_lei)-1)]
        equity_element.append(agreed_rp_element)
    else:
        performance_seller_element = etree.Element('performance_seller')
        performance_seller_element.text = available_lei[randint(0, len(available_lei)-1)]
        equity_element.append(performance_seller_element)

    return equity_element


def create_swap_credit(available_lei):
    '''
    Create a swap for asset_type == credit
    '''
    # Create root element
    credit_element = etree.Element('credit')

    # Create floating_rate_payer element
    # Populate and append to credit_element (root)
    floating_rate_payer_element = etree.Element('floating_rate_payer')
    floating_rate_payer_element.text = available_lei[randint(0, len(available_lei)-1)]
    credit_element.append(floating_rate_payer_element)

    # Create Swaption element (True or False)
    # Populate and append to credit_element (root)
    # Make swap a swaption 33% of the time
    swaption_element = etree.Element('swaption')
    swaption_element.text = 'True' if randint(1,3) % 2 == 0 else 'False'
    credit_element.append(swaption_element)

    return credit_element


def create_swap_commodity(available_lei):
    '''
    Create a swap for asset_type == commodity
    '''

    # Create root element (commodity)
    commodity_element = etree.Element('commodity')

    #options for trade_type
    available_trade_types = ['fixed_floating_swap', 'option', 'swaption', 'option_strategies', 'other']

    # Create a trade_type element
    trade_type_element = etree.Element('trade_type')
    trade_type_element.text = available_trade_types[randint(0, len(available_trade_types)-1)]

    # Add trade_type element to root (commodity)
    commodity_element.append(trade_type_element)

    # Check if the trade types are option, swaption, option_strategies
    # If so add a corresponding receiver_premium
    # Note that option_strategies could or could not have a receiver premium
    if trade_type_element.text in ['option_strategies', 'swaption', 'option']:
        if trade_type_element.text == 'option_strategies' and randint(1,3) % 2 == 0:
            pass
        else:
            receiver_premium_element = etree.Element('receiver_premium')
            receiver_premium_element.text = available_lei[randint(0, len(available_lei)-1)]

            # add receiver_premium_element to root (commodity)
            commodity_element.append(receiver_premium_element)

    # Add a seller_fixed_leg if trade_type == fixed_floating_swap
    if trade_type_element.text == 'fixed_floating_swap':
        seller_fixed_leg_element = etree.Element('seller_fixed_leg')
        seller_fixed_leg_element.text = available_lei[randint(0, len(available_lei)-1)]

        # add seller_fixed_leg_element to root (commodity)
        commodity_element.append(seller_fixed_leg_element)


    # Return Root element (commodity)
    return commodity_element


def create_swap_fx(available_lei):
    '''
    Create a swap for asset_type == fx
    '''

    # Create root element (fx)
    fx_element = etree.Element('fx')

    # list of available trade types
    available_trade_types = ['forward', 'ndf', 'option', 'ndo', 'simple_exotic', 'complex_exotic']

    # Choose trade type, create the element
    chosen_trade_type = available_trade_types[randint(0, len(available_trade_types)-1)]
    trade_type_element = etree.Element('trade_type')
    trade_type_element.text = chosen_trade_type

    # Append trade_type element to root (fx)
    fx_element.append(trade_type_element)

    # list of available currencies
    available_currencies = ['usd', 'eur', 'jpy', 'gbp', 'chf', 'cad', 'aud', 'zar']

    # Create currency_element for currency_1 and currency_2 and add text
    currency_1_element = etree.Element('currency')
    currency_2_element = etree.Element('currency')

    # Choose two currencies_name for the swap
    currency_1_name = available_currencies[randint(0, len(available_currencies)-1)]

    # Remove chosen currency to avoid duplicates
    available_currencies.remove(currency_1_name)

    currency_2_name = available_currencies[randint(0, len(available_currencies)-1)]

    # Create currency_name elements
    currency_1_name_element = etree.Element('currency_name')
    currency_2_name_element = etree.Element('currency_name')

    # Assign currency_names to respective elements
    currency_1_name_element.text = currency_1_name
    currency_2_name_element.text = currency_2_name

    # Choose random lei for currency 1
    available_lei_2 = available_lei
    currency_lei_1 = available_lei_2[randint(0, len(available_lei_2)-1)]

    # remove chosen lei to avoid duplicates
    available_lei_2.remove(currency_lei_1)

    # Choose random lei for currency 2
    currency_lei_2 = available_lei_2[randint(0, len(available_lei_2)-1)]

    # Create lei elements for each currency and add the appropriate lei
    lei_1_element = etree.Element('lei')
    lei_2_element = etree.Element('lei')

    # Assign lei to respective elements
    lei_1_element.text = currency_lei_1
    lei_2_element.text = currency_lei_2

    # Assign currency_name and lei to appropriate elements
    currency_1_element.append(currency_1_name_element)
    currency_1_element.append(lei_1_element)

    currency_2_element.append(currency_2_name_element)
    currency_2_element.append(lei_2_element)

    # Create currencies root element
    currencies_element = etree.Element('currencies')

    # Add both currency elements to the currencies elements
    currencies_element.append(currency_1_element)
    currencies_element.append(currency_2_element)

    # Add currencies element to fx_element
    fx_element.append(currencies_element)

    # See if seller_option is necessary
    if chosen_trade_type in ['option', 'ndo', 'simple_exotic', 'complex_exotic']:

        # Create a seller_option element
        seller_option_element = etree.Element('seller_option')
        
        # Add a random lei
        seller_option_element.text = available_lei[randint(0, len(available_lei)-1)]

        # Add seller_option to fx element
        fx_element.append(seller_option_element)

    # Return fx element
    return fx_element


def get_populate_lei_country(entities):
    '''
    Populate lei and country list from an entities XML element
    '''
    available_lei = []
    available_countries = []
    for element in entities.iter('entity'):
        available_lei.append(element.find('lei').text)
        available_countries.append(element.find('country').text)

    return {'lei': available_lei, 'countries': available_countries}


if __name__ == "__main__":
    if len(argv) > 1:
        no_transactions = int(argv[1])
        generate_samples(no_transactions)
    else:
        generate_samples()
