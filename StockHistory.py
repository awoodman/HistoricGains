#!/usr/bin/python3

import requests
import json
from datetime import datetime
from alpha_vantage.timeseries import TimeSeries

# Fetch all data
URL = "https://www.alphavantage.co/query"
keyFile = open('alphaVantageApiKey.txt','r')
key = keyFile.readline()

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
validOption = False
leftOverCash = 0
symbol = ""

# Header
print("*** Dollar Cost Averaging Calculator ***\n")

# Menu Options
menuOption = input("Choose an option: \n1. Previous N years of history\n2. Specific date range\n3. Precanned data (Array of: symbol, years, start year, monthly investment)\n")

def readInputFile():
        inData = []
        inFile = open("StockCombinations.csv", "r")
        for line in inFile:
                newLine = line.split(",")
                inData.append({"symbol":newLine[0].strip(), "numYears":newLine[1].strip(), "startYear":newLine[2].strip(), "investPerMonth":newLine[3].strip()})
        return inData

def getStockHistory(stockSym = None):
	if (stockSym == None):
		symbol = input("Enter a stock or ETF symbol: ")
	else:
		symbol = stockSym
	PARAMS = {'function':"TIME_SERIES_MONTHLY",'symbol':symbol,'apikey':key}
	r = requests.get(url = URL, params = PARAMS)
	stockHistory = r.json()['Monthly Time Series']
	sortedKeys = sorted(stockHistory)
	totalEnt = len(stockHistory)
	return (stockHistory, sortedKeys, totalEnt, symbol)

def purchaseShares(stockHistory, tradeDate, leftOverCash, dollarsPerMonthInvested, sharesPurchasedTotal, totalInvested):
        sharePrice = float(stockHistory[tradeDate]['1. open'])
        amountToInvestDuringMonth = leftOverCash + dollarsPerMonthInvested
        sharesPurchasedDuringMonth = int(amountToInvestDuringMonth / sharePrice)
        sharesPurchasedTotal = sharesPurchasedTotal + sharesPurchasedDuringMonth
        totalInvested = totalInvested + (sharePrice * sharesPurchasedDuringMonth)
        leftOverCash = amountToInvestDuringMonth % sharePrice
        return (sharesPurchasedTotal, totalInvested, leftOverCash)

def printResults(sharesPurchasedTotal, stockHistory, sortedKeys, totalEnt, totalInvested, menuOption, symbol, firstTradeDate, lastTradeDate):
        # Print results
        totalCurrValue = sharesPurchasedTotal * float(stockHistory[sortedKeys[totalEnt - 1]]['1. open'])
        netGain = totalCurrValue - totalInvested
        percentGain = 100 * netGain / totalInvested
        # Get start/end months from trade dates
        startMonth = firstTradeDate.split("-")[1]
        endMonth = lastTradeDate.split("-")[1]
        if (int(menuOption) == 1):
                print("\nResults for investing $%s/mo in %s for the past %s years (%s/%s - %s/%s):" % (dollarsPerMonthInvested, symbol, yearsOfHistory, startMonth, startYear, endMonth, (int(startYear) + yearsOfHistory)))
        elif ((int(menuOption) == 2) or (int(menuOption) == 3)):
                print("\nResults for investing $%s/mo in %s for %s years, (%s/%s - %s/%s):" % (dollarsPerMonthInvested, symbol, yearsOfHistory, startMonth, startYear, endMonth, (int(startYear) + yearsOfHistory)))
        print("- Total money invested: $%.2f (%s shares)" % (totalInvested, sharesPurchasedTotal))
        print("- Current Total Worth: $%.2f" % totalCurrValue)
        percentSymbol = "%"
        print("- You have made $%.2f (%.1f%s gain)" % (netGain, percentGain, str(percentSymbol)))
        #avgAnnualRateOfReturn = (((totalCurrValue / totalInvested) ** (1 / yearsOfHistory)) - 1 ) * 100
        #avgAnnualRateOfReturn = percentGain / yearsOfHistory
        #print("- Average annual rate of return: %.1f%s" % (avgAnnualRateOfReturn, str(percentSymbol)))

if (int(menuOption) == 1):
	stockHistory, sortedKeys, totalEnt, symbol = getStockHistory()
	yearsOfHistory = int(input("Enter years of history: "))
	monthsOfHistory = yearsOfHistory * 12
	dollarsPerMonthInvested = int(input("Enter dollars per month invested: $"))
	startYear = datetime.now().year - yearsOfHistory
	# Get the last N months of data, ending on the last trade day of last month
	# If we are not near the end of current month, end at end of last month
	if (int(datetime.today().day) < 27):
		endIndex = -2
	else:
		endIndex = -1
	startIndex = totalEnt - monthsOfHistory - 1
	tradeDates = sortedKeys[startIndex:endIndex]
	for tradeDate in tradeDates:
		sharesPurchasedTotal, totalInvested, leftOverCash = purchaseShares(stockHistory, tradeDate, leftOverCash, dollarsPerMonthInvested, sharesPurchasedTotal, totalInvested)
	printResults(sharesPurchasedTotal, stockHistory, sortedKeys, totalEnt, totalInvested, menuOption, symbol, sortedKeys[(totalEnt - monthsOfHistory - 1)], sortedKeys[endIndex])

elif (int(menuOption) == 2):
	stockHistory, sortedKeys, totalEnt, symbol = getStockHistory()
	startYear = input("Enter starting year (format YYYY): ")
	yearsOfHistory = int(input("Enter duration (years): "))
	dollarsPerMonthInvested = int(input("Enter dollars per month invested: $ "))
	monthsOfHistory = 12 * yearsOfHistory - 1

	# Last business day in month varies
	for day in range(25, 32):
		try:
			startIndex = sortedKeys.index("%s-01-%s" % (startYear, day))
		except:
			"Do nothing, dont error on exception"
		else:
			"Found Index"
			break

	endIndex = startIndex + monthsOfHistory
	tradeDates = sortedKeys[startIndex:endIndex]
	print(tradeDates)
	for tradeDate in tradeDates:
		sharesPurchasedTotal, totalInvested, leftOverCash = purchaseShares(stockHistory, tradeDate, leftOverCash, dollarsPerMonthInvested, sharesPurchasedTotal, totalInvested)

	printResults(sharesPurchasedTotal, stockHistory, sortedKeys, totalEnt, totalInvested, menuOption, symbol, sortedKeys[startIndex], sortedKeys[endIndex])

elif (int(menuOption) == 3):
	stockCombinations = readInputFile()
	for entry in stockCombinations:
		leftOverCash = 0
		sharesPurchasedTotal = 0
		totalInvested = 0
		stockHistory, sortedKeys, totalEnt, symbol = getStockHistory(entry["symbol"])
		startYear = int(entry["startYear"])
		yearsOfHistory = int(entry["numYears"])
		dollarsPerMonthInvested = int(entry["investPerMonth"])
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

		for tradeDate in tradeDates:
			sharesPurchasedTotal, totalInvested, leftOverCash = purchaseShares(stockHistory, tradeDate, leftOverCash, dollarsPerMonthInvested, sharesPurchasedTotal, totalInvested)

		printResults(sharesPurchasedTotal, stockHistory, sortedKeys, totalEnt, totalInvested, menuOption, symbol, sortedKeys[(totalEnt - monthsOfHistory - 1)], sortedKeys[-1])

else:
	print("Invalid option chosen, try again...")

