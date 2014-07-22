## Data points for determining reporting party (RP)

### Scenarios not accounted for:
	+ cleared swaps
	+ Non-LEI identifier
	+ Novated transactionsctions
	+ Transactions with non-US parties conducted outside of a facility


## Data Fields


### Entity
	+ LEI:  # legal entity identifier
	+ entity_type: SD, MSP, end_user  (Swap Dealer, Major Swap Participant)
	+ country_of_origin
	+ financial_entity: True or False



### Swap
	+ swap_facility: SEF, DCM, none (Swap Execution Facility, Designated Contract Market)
	+ seller: LEI #
	+ asset_class: rates, credit, equity, commodity, fx

### Credit:
	+ floating_rate_payer: LEI
	+ swaption: True or False

### Rates:
	+ trade_type: cap_floor, debt_option, exotic, fra, irs_basis, irs_fix_fix, irs_fix_float, ir_swap_inflation, ir_swap_ois, swaption, xccy_basis, xccy_fix_fix, xccy_fix_float
	+ option_buyer:  (only for debt_option, swaption) 
	+ fixed_rate_payer: # (only for cap_floor, fra, irs_fix_float, irswap_inflation,
							irs_swap_ois, fix_float)
	* Note: cap_floor could have two fixed rate payers)

### Equity:
	+ seller_of_performance: LEI
	+ agreed_rp (only if no seller): LEI
	+ negative_affirmation: true or false

	

### Commodities:
	+ trade_type: fixed_floating_swap, option, swaption, option_strategies, other
	+ receiver_premium: LEI (only for option, swaption, option_strategies) 
		(premium not mandatory for option_strategy)
	+ seller_fixed_leg: LEI (only fixed_floating_swap )


### FX:
	+ trade_type: forward, ndf, option, ndo, simple_exotic, complex_exotic
	+ currency
		* LEI
		* Currency_Name
	+ seller_option: LEI # only for option, ndo, simple/complex_exotic
