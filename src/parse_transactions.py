from lxml import etree
from StringIO import StringIO
from datetime import datetime

'''
This script takes an xml file of swap transactions and parses them to determine who is the Dodd-Frank "reporting party"
The result is output in XML in the format below:
<transactions>
    <transaction>
        <unique_swap_id>5555555aaaa555</unique_swap_id>
        <reporting_party_45>4d8832hfjahfadf</reporting_party>
        <reporting_party_43>4d8832hfjahfadf</reporting_party>
    </transaction>
</transactions>

'''

def process_file(swaps_file):
    '''
    This is the initial function. It reads the XML file, parses it and
    sends off each transaction to be processed.

    It also puts together the results xml file and writes to a file.
    '''

    # Open the income xml file
    f = open(swaps_file, 'r+')
    swap_xml = f.read()

    # Parse the file with lxml
    swap_xml = etree.parse(StringIO(swap_xml))

    # Create an element to house all the results
    transactions_element = etree.Element('transactions')

    # Iterate through each transaction and send to get processed
    for swap in swap_xml.iter('transaction'):
        result = get_reporting_party(swap)

        # Append unique identifier element
        result.append(swap.find('unique_swap_id'))

        # Adds result to transactions_element
        transactions_element.append(result)

    # Prepare to write to file
    results_string = etree.ElementTree(transactions_element)

    # Create file name from timestamp
    timestamp = 'result_xml/' + datetime.now().strftime("%H_%M_%Y_%m_%d") + ".xml"

    f.close()

    # Write transactions to file
    results_string.write(timestamp, pretty_print=True, xml_declaration=True)

    # Notify of completion
    print('Complete...')



def get_reporting_party(swap):
    '''
    Parses a transaction XML element and returns the following structure:
    <transaction>
        <reporting_party_45>4d8832hfjahfadf</reporting_party>
        <reporting_party_43>4d8832hfjahfadf</reporting_party>
    </transaction>
    '''
    # element.find('lei').text

    # Iterate through all the entities
    count = 0
    swap_dict = {}
    entities_list = []
    for entity in swap.iter('entity'):
        entity_dict = {}

        # Unpack all variables
        entity_dict['lei'] = entity.find('lei').text
        entity_dict['country'] = entity.find('country').text
        entity_dict['financial_entity'] = entity.find('financial_entity').text
        entity_dict['entity_type'] = entity.find('entity_type').text

        # Assign list of entities to a python list
        entities_list.append(entity_dict)

    # Create entities key in entities_dict
    swap_dict['entities'] = entities_list


    # Unpack Swap objects and add to swap_dict
    swap_dict['facility'] = swap.find('swap').find('facility').text
    swap_dict['seller'] = swap.find('swap').find('seller').text
    swap_dict['asset_class'] = swap.find('swap').find('asset_class').text

    # Check for initial results of reporting party.
    # Pass along swap info in case further calculation is needed
    result = first_check_result(swap_dict, swap)
    return result


def first_check_result(swap_dict, swap):
    '''
    Check to see if the initial rules fits the swap.
    If so, return result.
    If not, forward on for more processing
    '''
    entity_1 = swap_dict['entities'][0]
    entity_2 = swap_dict['entities'][1]


    if swap_dict['facility'] in ['SEF', 'DCM']:
        reporting_party_43 = swap_dict['facility']
        if  entity_1['country'] == 'USA' or entity_2['country'] == 'USA':
            reporting_party_45 = swap_dict['facility']
        else:
            reporting_party_45 = "Agree between parties"
            
        return create_final_transaction(reporting_party_45, reporting_party_43)

    # Dodd-Frank rules for when both parties are US Persons and are SD or MSP (not End User)
    if  entity_1['entity_type'] == entity_2['entity_type'] and entity_1['entity_type'] != 'End USer':
        return further_check_result(swap_dict, swap)

    # This code block checks to see who is the RP using the entity_type hierarchy
    # SD wins over MSP and End User
    # MSP wins over End User
    # This code block assumes that SD/SD and MSP/MSP combinations are already eliminated
    if entity_1['entity_type'] == 'SD' and entity_2['entity_type'] in ['MSP', 'End User']:
        reporting_party_45 = entity_1['lei']
        reporting_party_43 = entity_1['lei']
        return create_final_transaction(reporting_party_45, reporting_party_43)

    if entity_1['entity_type'] == 'End User' and entity_2['entity_type'] in ['SD', 'MSP']:
        reporting_party_45 = entity_2['lei']
        reporting_party_43 = entity_2['lei']
        return create_final_transaction(reporting_party_45, reporting_party_43)

    if entity_1['entity_type'] == 'MSP':
        if entity_2['entity_type'] == 'End User':
            reporting_party_45 = entity_1['lei']
            reporting_party_43 = entity_1['lei']
            return create_final_transaction(reporting_party_45, reporting_party_43)

        else:
            reporting_party_45 = entity_2['lei']
            reporting_party_43 = entity_2['lei']
            return create_final_transaction(reporting_party_45, reporting_party_43)


    # This code block determies the result if both entities are End Users
    if entity_1['entity_type'] == 'End User' and entity_2['entity_type'] == 'End User':

        # If only on entity is based in USA, they are responsible for RP45
        # Entities decide who is responsible for RP43
        if entity_1['country'] == 'USA' and entity_2['entity_type'] != 'USA':
            reporting_party_45 = entity_1['lei']
            reporting_party_43 = "Agree between parties"
            return create_final_transaction(reporting_party_45, reporting_party_43)

        if entity_2['country'] == 'USA' and entity_1['entity_type'] != 'USA':
            reporting_party_45 = entity_2['lei']
            reporting_party_43 = "Agree between parties"
            return create_final_transaction(reporting_party_45, reporting_party_43)


        # Code block now includes transactions where both participants are US based
        # End Users that are financial entities are the RP for Rule 45
        # Rule 43 is determined with the Same Level Reporting Rules
        if entity_1['financial_entity'] == entity_2['financial_entity']:
            reporting_party_45 = "Agree between parties"

        if entity_1['financial_entity'] == 'True' and entity_2['financial_entity'] == 'False':
            reporting_party_45 = entity_1['lei']
        
        if entity_1['financial_entity'] == 'False' and entity_2['financial_entity'] == 'True':
            reporting_party_45 = entity_1['lei']

        # Passes along to determine the RP43 entity.
        return further_check_result(swap_dict, swap, reporting_party_45=reporting_party_45)



def create_final_transaction(reporting_party_45, reporting_party_43):
    '''
    Creates the transaction element for the result
    '''

    # Create the root element (transaction) and result elements
    transaction_element = etree.Element('transaction')
    reporting_party_45_element = etree.Element('reporting_party_45')
    reporting_party_43_element = etree.Element('reporting_party_43')

    # Assign the answer to the elements
    reporting_party_45_element.text = reporting_party_45
    reporting_party_43_element.text = reporting_party_43

    transaction_element.append(reporting_party_45_element)
    transaction_element.append(reporting_party_43_element)

    return transaction_element



def further_check_result(swap_dict, swap, **kwargs):
    '''
    This function returns a completed transaction element.
    It is called in the scenarios wher ethe entities are the same.
    It can take in random key-value pairs to see for when a reporting_party is already determined.
    i.e. - reporting_party_45="foobar"  or reporting_party_43="foobar"
    '''

    if swap_dict['asset_class'] == 'credit':
        # Credit RP is the floaing_rate_payer
        reporting_party_45 = swap.find('credit').find('floating_rate_payer').text
        reporting_party_43 = reporting_party_45

        # Check if an RP was already determined in the kwargs argument
        reporting_party_45 = kwargs.get('reporting_party_45', reporting_party_45)
        reporting_party_43 = kwargs.get('reporting_party_43', reporting_party_43)

        return create_final_transaction(reporting_party_45, reporting_party_43)


    if swap_dict['asset_class'] == 'rates':
        # Get the swap element
        available_trade_types = ['cap_floor', 'debt_option', 'exotic', 'fra', 'irs_basis',
                             'irs_fix_fix', 'irs_fix_float', 'ir_swap_inflation', 'ir_swap_ois',
                             'swaption', 'xccy_basis', 'xccy_fix_fix', 'xccy_fix_float']

        # Create a dict to store results of trade_type searches
        rates = {}

        # Iterate through available_trade_types and find the search results
        # Find function returns None if it is not found
        for trade_type in available_trade_types:
            rates[trade_type] = swap.find(trade_type)

        if rates['fra'] is not None:
            obj = rates['fra']
            # RP is the fixed rate payer
            result = obj.find('fixed_rate_payer').text
            return get_further_check_result(result, kwargs)


        if rates['irs_fix_float'] is not None:
            obj = rates['irs_fix_float']
            # RP is the fixed rate payer
            result = obj.find('fixed_rate_payer').text
            return get_further_check_result(result, kwargs)

        if rates['ir_swap_ois'] is not None:
            obj = rates['ir_swap_ois']
            # RP is the fixed rate payer
            result = obj.find('fixed_rate_payer').text
            return get_further_check_result(result, kwargs)

        if rates['xccy_fix_float'] is not None:
            obj = rates['xccy_fix_float']
            # RP is the fixed rate payer
            result = obj.find('fixed_rate_payer').text
            return get_further_check_result(result, kwargs)

        if rates['cap_floor'] is not None:
            obj = rates['cap_floor']
            if len(obj.findall('fixed_rate_payer')) == 1:
                # RP is the fixed rate payer
                result = obj.find('fixed_rate_payer').text
                return get_further_check_result(result, kwargs)
            else:
                result = reverse_ascii_sort(swap_dict)
                return get_further_check_result(result, kwargs)

        if rates['ir_swap_inflation'] is not None:
            obj = rates['ir_swap_inflation']
            if len(obj.findall('fixed_rate_payer')) == 1:
                # RP is the fixed rate payer
                result = obj.find('fixed_rate_payer').text
                return get_further_check_result(result, kwargs)
            else:
                result = reverse_ascii_sort(swap_dict)
                return get_further_check_result(result, kwargs)

        if rates['debt_option'] is not None:
            obj = rates['debt_option']
            result = obj.find('option_buyer')
            return get_further_check_result(result, kwargs)

        if rates['swaption'] is not None:
            obj = rates['swaption']
            result = obj.find('option_buyer')
            return get_further_check_result(result, kwargs)

        if rates['exotic'] is not None:
            result = reverse_ascii_sort(swap_dict)
            return get_further_check_result(result, kwargs)

        if rates['irs_basis'] is not None:
            result = reverse_ascii_sort(swap_dict)
            return get_further_check_result(result, kwargs)

        if rates['irs_fix_fix'] is not None:
            result = reverse_ascii_sort(swap_dict)
            return get_further_check_result(result, kwargs)

        if rates['xccy_basis'] is not None:
            result = reverse_ascii_sort(swap_dict)
            return get_further_check_result(result, kwargs)

        if rates['xccy_fix_fix'] is not None:
            result = reverse_ascii_sort(swap_dict)
            return get_further_check_result(result, kwargs)

    if swap_dict['asset_class'] == 'equity':
        
        if swap.find('negative_affirmation').text != 'False':
            result = swap.find('negative_affirmation').text
            return get_further_check_result(result, kwargs)

        if swap.find('performance_seller') is not None:
            result = swap.find('performance_seller').text
            return get_further_check_result(result, kwargs)

        else:
            result = swap.find('agreed_rp').text
            return get_further_check_result(result, kwargs)

    if swap_dict['asset_class'] == 'commodity':
        swap = swap.find('commodity')

        trade_type = swap.find('trade_type').text

        if trade_type == 'option_strategies':
            if swap.find('receiver_premium') is not None:
                result = swap.find('receiver_premium').text
                return get_further_check_result(result, kwargs)
            else:
                result = reverse_ascii_sort(swap_dict)
                return get_further_check_result(result, kwargs)

        if trade_type == 'other':
            result = reverse_ascii_sort(swap_dict)
            return get_further_check_result(result, kwargs)

        if swap.find('receiver_premium') is not None:
            result = swap.find('receiver_premium').text
            return get_further_check_result(result, kwargs)

        if swap.find('seller_fixed_leg') is not None:
            result = swap.find('seller_fixed_leg').text
            return get_further_check_result(result, kwargs)

    if swap_dict['asset_class'] == 'fx':
        swap = swap.find('swap').find('fx')

        trade_type = swap.find('trade_type').text

        if trade_type in ['option', 'ndo', 'simple_exotic', 'complex_exotic']:
            result = swap.find('seller_option').text
            return get_further_check_result(result, kwargs)
        else:
            currencies = swap.find('currencies')
            currency_list = []
            # Creates a list made up of (currency_name, lei)
            for currency in currencies.iter('currency'):
                currency_name = currency.find('currency_name').text
                lei = currency.find('lei').text
                currency_list.append((currency_name, lei))

            # Sorts the list by first element in the tuple; returns the first tuple; then the 2nd element (lei)
            result = sorted(currency_list, key=lambda tup: tup[0])[0][1]
            return get_further_check_result(result, kwargs)


def reverse_ascii_sort(swap_dict):
    '''
    Implement Reverse Sort Per Regulations
    '''

    # Get lei from swap_dict
    entities = swap_dict['entities']
    item1 = entities[0]['lei']
    item2 = entities[1]['lei']

    for item in zip(item1, item2):
        if item[0] > item[1]:
            return item1

        if item[0] < item[1]:
            return item2



def get_further_check_result(result, old_kwargs):
        reporting_party_45 = result
        reporting_party_43 = reporting_party_45

        # Check if an RP was already determined in the kwargs argument
        reporting_party_45 = old_kwargs.get('reporting_party_45', reporting_party_45)
        reporting_party_43 = old_kwargs.get('reporting_party_43', reporting_party_43)

        return create_final_transaction(reporting_party_45, reporting_party_43)


if __name__ == '__main__':
    process_file('sample_xml/18_51_2014_07_21.xml')
