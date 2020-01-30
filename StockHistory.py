#!/usr/bin/python3
import requests
import json
from datetime import datetime
from alpha_vantage.timeseries import TimeSeries

# Fetch all data
URL = "https://www.alphavantage.co/query"
keyFile = open('alphaVantageApiKey.txt','r')
key = keyFile.readline()
#key = 'LEU4ECTWL6XRRGPU'

# Calculations
currMonth = datetime.now().month

# Initialization
totalInvested = 0
sharesPurchasedMonthly = 0
sharesPurchasedTotal = 0
dollarsPerMonthInvested = 0
yearsOfHistory = 0
monthsOfHistory = 0
startYear = 0
validOption = True

# Header
print("*** Dollar Cost Averaging Calculator ***\n")

# Menu Options
menuOption = input("Choose an option: \n1. Previous N years of history\n2. Specific date range\n")
symbol = input("Enter a stock or ETF symbol: ")
PARAMS = {'function':"TIME_SERIES_MONTHLY",'symbol':symbol,'apikey':key}
r = requests.get(url = URL, params = PARAMS)
stockHistory = r.json()['Monthly Time Series']
sortedKeys = sorted(stockHistory)
totalEnt = len(stockHistory)

if (int(menuOption) == 1):
	yearsOfHistory = int(input("Enter years of history: "))
	monthsOfHistory = yearsOfHistory * 12
	dollarsPerMonthInvested = int(input("Enter dollars per month invested: $"))
	startYear = datetime.now().year - yearsOfHistory
	# Get the last N months of data, ending on the last day of last month
	tradeDates = sortedKeys[(totalEnt - monthsOfHistory - 1):-1]
	leftOverCash = 0
	for tradeDate in tradeDates:
		# OLD
		#totalInvested = totalInvested + dollarsPerMonthInvested
		#sharePrice = float(stockHistory[tradeDate]['1. open'])
		#sharesPurchasedTotal = sharesPurchasedTotal + (dollarsPerMonthInvested / sharePrice)
		
		# NEW	
		amountToInvestDuringMonth = leftOverCash + dollarsPerMonthInvested
		sharedPurchasedDuringMonth = int(amountToInvest / sharePrice)
		sharesPurchasedTotal = sharesPurchasedTotal + sharesPurchasedDuringMonth
		totalInvested = totalInvested + (sharePrice * sharesPurchasedDuringMonth)
		leftOverCash = amountToInvest % sharePrice
		print("Amount to invest: %.2f, Whole share cost: %.2f, left over: %.2f" % (amountToInvest, sharePrice, leftOverCash))
		print("Total Invested: %.2f" % totalInvested)	
elif (int(menuOption) == 2):
	startYear = input("Enter starting year (format YYYY): ")
	yearsOfHistory = int(input("Enter duration (years): "))
	dollarsPerMonthInvested = int(input("Enter dollars per month invested: $ "))
	monthsOfHistory = 12 * yearsOfHistory
	# Last business day in month varies
	for day in range(25, 32):
		try:
			startIndex = sortedKeys.index("%s-01-%s" % (startYear, day))
		except:
			"Do nothing, dont error on exception"
		else:
			"Found Index"
			break
	tradeDates = sortedKeys[startIndex:(startIndex + monthsOfHistory)]
	print("Dates Traded: %s" % tradeDates)
	for tradeDate in tradeDates:
		totalInvested = totalInvested + dollarsPerMonthInvested
		sharePrice = float(stockHistory[tradeDate]['1. open'])
		sharesPurchasedTotal = sharesPurchasedTotal + (dollarsPerMonthInvested / sharePrice)
else:
	print("Invalid option chosen, try again...")
	validOption = False

if (validOption):
	# Print results
	totalCurrValue = sharesPurchasedTotal * float(stockHistory[sortedKeys[totalEnt - 1]]['1. open'])
	netGain = totalCurrValue - totalInvested
	percentGain = 100 * netGain / totalInvested
	if (int(menuOption) == 1):
		print("\nResults for investing $%s/mo in %s for %s years, starting in %s:" % (dollarsPerMonthInvested, symbol, yearsOfHistory, startYear))
	else:
		print("\nResults for investing $%s/mo in %s for %s years, starting in January %s:" % (dollarsPerMonthInvested, symbol, yearsOfHistory, startYear))
	print("- Total money invested: $%.2f (%s shares)" % (totalInvested, sharesPurchasedTotal))
	print("- Current Total Worth: $%.2f" % totalCurrValue)
	percentSymbol = "%"
	print("- You have made $%.2f (%.1f%s gain)" % (netGain, percentGain, str(percentSymbol)))
