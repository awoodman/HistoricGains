import requests
import json
from datetime import datetime
from alpha_vantage.timeseries import TimeSeries

# Fetch all data
URL = "https://www.alphavantage.co/query"
key = 'LEU4ECTWL6XRRGPU'


# Calculations
currMonth = datetime.now().month

# Initialization
totalInvested = 0
sharesPurchased = 0
dollarsPerMonthInvested = 0
yearsOfHistory = 0
monthsOfHistory = 0
startYear = 0
validOption = True

# Menu Options
menuOption = input("Choose an option: \n1. Previous N years of history\n2. Specific date range\n")
symbol = input("Enter a stock or ETF symbol: ")
PARAMS = {'function':"TIME_SERIES_MONTHLY",'symbol':symbol,'apikey':key}
r = requests.get(url = URL, params = PARAMS)
stockHistory = r.json()['Monthly Time Series']
sortedKeys = sorted(stockHistory)
totalEnt = len(stockHistory)

if (int(menuOption) == 1):
	yearsOfHistory = int(input("How many years of history? "))
	monthsOfHistory = yearsOfHistory * 12
	dollarsPerMonthInvested = int(input("How many dollars per month invested? "))
	startYear = datetime.now().year - yearsOfHistory
	# Get the last N months of data, ending on the last day of last month
	tradeDates = sortedKeys[(totalEnt - monthsOfHistory - 1):-1]
	for tradeDate in tradeDates:
		totalInvested = totalInvested + dollarsPerMonthInvested
		sharePrice = float(stockHistory[tradeDate]['1. open'])
		sharesPurchased = sharesPurchased + (dollarsPerMonthInvested / sharePrice)
elif (int(menuOption) == 2):
	startYear = input("Choose starting year (format YYYY): ")
	yearsOfHistory = int(input("Choose years of duration: "))
	dollarsPerMonthInvested = int(input("How many dollars per month invested? "))
	monthsOfHistory = 12 * yearsOfHistory
	for day in range(25, 32):
		try:
			startIndex = sortedKeys.index("%s-01-%s" % (startYear, day))
		except:
			"Do nothing, dont error on exception"
		else:
			"Found Index"
			break
	tradeDates = sortedKeys[startIndex:(startIndex + monthsOfHistory)]
	for tradeDate in tradeDates:
		totalInvested = totalInvested + dollarsPerMonthInvested
		sharePrice = float(stockHistory[tradeDate]['1. open'])
		sharesPurchased = sharesPurchased + (dollarsPerMonthInvested / sharePrice)
else:
	print("Invalid option chosen")
	validOption = False

if (validOption):
	# Print results
	totalCurrValue = sharesPurchased * float(stockHistory[sortedKeys[totalEnt - 1]]['1. open'])
	netGain = totalCurrValue - totalInvested
	percentGain = 100 * netGain / totalInvested
	print("\nResults for investing $%s/mo in %s for %s years, starting in %s:" % (dollarsPerMonthInvested, symbol, yearsOfHistory, startYear))
	print("- Total money invested: $%s (%s shares)" % (totalInvested, sharesPurchased))
	print("- Current Total Worth: $%s" % totalCurrValue)
	print("- You have made $%s, which is a %s percent gain" % (str(netGain), str(percentGain)))
