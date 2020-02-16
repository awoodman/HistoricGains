#!/usr/bin/python3

import requests
import json
from datetime import datetime
from alpha_vantage.timeseries import TimeSeries
import time

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
startIndex = 0
endIndex = 0

# Header
print("*** Dollar Cost Averaging Calculator ***\n")

# Menu Options
menuOption = input("Choose an option: \n1. Previous N years of history\n2. Specific date range\n3. Precanned data (Array of: symbol, years, start year, monthly investment)\n")

def readInputFile():
        inData = []
        inFile = open("StockCombinations.csv", "r")
        for line in inFile:
                if (not line.startswith("#")):
                     newLine = line.split(",")
                     print("inFile: %s,%s,%s,%s" % (newLine[0].strip(), newLine[1].strip(), newLine[2].strip(), newLine[3].strip()))
                     inData.append({"symbol":newLine[0].strip(), "numYears":newLine[1].strip(), "startYear":newLine[2].strip(), "investPerMonth":newLine[3].strip()})
        return inData

def getStockHistory(stockSym = None):
	stockHistory = {}
	totalEnt = 0
	sortedKeys = []

	numRetries = 20

	if (stockSym == None):
		symbol = input("Enter a stock or ETF symbol: ")
	else:
		symbol = stockSym

	PARAMS = {'function':"TIME_SERIES_MONTHLY",'symbol':symbol,'apikey':key}

	gotHistory = False
	retryNum = 0

	while ((not gotHistory) and (retryNum < numRetries)):
		try:
			r = requests.get(url = URL, params = PARAMS)
			stockHistory = r.json()['Monthly Time Series']
			sortedKeys = sorted(stockHistory)
			totalEnt = len(stockHistory)
			gotHistory = True
		except:
			time.sleep(5)
			retryNum = retryNum + 1
			#print("Error fetching history...")

	return (stockHistory, sortedKeys, totalEnt, symbol)

def purchaseShares(stockHistory, tradeDate, leftOverCash, dollarsPerMonthInvested, sharesPurchasedTotal, totalInvested):
        sharePrice = float(stockHistory[tradeDate]['1. open'])
        amountToInvestDuringMonth = leftOverCash + dollarsPerMonthInvested
        sharesPurchasedDuringMonth = int(amountToInvestDuringMonth / sharePrice)
        sharesPurchasedTotal = sharesPurchasedTotal + sharesPurchasedDuringMonth
        totalInvested = totalInvested + (sharePrice * sharesPurchasedDuringMonth)
        leftOverCash = amountToInvestDuringMonth % sharePrice
        #print("Share price: %s, Amount to Invest: %s, Shares Purchased: %s, Left Over: %s" % (sharePrice, amountToInvestDuringMonth, sharesPurchasedDuringMonth, leftOverCash))
        return (sharesPurchasedTotal, totalInvested, leftOverCash)

def printResults(sharesPurchasedTotal, stockHistory, sortedKeys, totalEnt, totalInvested, menuOption, symbol, firstTradeDate, lastTradeDate):
        # Print results
        if (totalInvested == 0):
                print("Error fetching data, not this many years of history for %s" % symbol)
        else:
                totalCurrValue = sharesPurchasedTotal * float(stockHistory[lastTradeDate]['1. open'])
                #print("Date stocks sold: %s" % sortedKeys[totalEnt - 1])
                #print("Last trade date: %s" % lastTradeDate)
                netGain = totalCurrValue - totalInvested
                percentGain = 100 * netGain / totalInvested
                # Get start/end months from trade dates
                startMonth = firstTradeDate.split("-")[1]
                endMonth = lastTradeDate.split("-")[1]
                if (int(menuOption) == 1):
                        print("\nResults for investing $%s/mo in %s for the past %s years (%s/%s - %s/%s):" % (dollarsPerMonthInvested, symbol, yearsOfHistory, startMonth, startYear, endMonth, (int(startYear) + yearsOfHistory)))
                elif ((int(menuOption) == 2) or (int(menuOption) == 3)):
                        print("\nResults for investing $%s/mo in %s for %s years, (%s/%s - %s/%s):" % (dollarsPerMonthInvested, symbol, yearsOfHistory, startMonth, startYear, endMonth, (int(startYear) + yearsOfHistory)))
                print("- Total Invested: $%.2f (%s shares)" % (totalInvested, sharesPurchasedTotal))
                print("- Total Value: $%.2f" % totalCurrValue)
                percentSymbol = "%"
                print("- Total Earnings $%.2f (%.1f%s gain)" % (netGain, percentGain, str(percentSymbol)))
                #avgAnnualRateOfReturn = (((totalCurrValue / totalInvested) ** (1 / yearsOfHistory)) - 1 ) * 100
                #avgAnnualRateOfReturn = percentGain / yearsOfHistory
                #print("- Average annual rate of return: %.1f%s" % (avgAnnualRateOfReturn, str(percentSymbol)))

if (int(menuOption) == 1):
	stockHistory, sortedKeys, totalEnt, symbol = getStockHistory()
	yearsOfHistory = int(input("Enter years of history: "))
	monthsOfHistory = yearsOfHistory * 12
	# If enough history exists, proceed
	if (totalEnt >= monthsOfHistory):
		dollarsPerMonthInvested = int(input("Enter dollars per month invested: $"))
		startYear = datetime.now().year - yearsOfHistory
		# Get the last N months of data, ending on the last trade day of last month
		# If we are not near the end of current month, end at end of last month
		#if (int(datetime.today().day) < 27):
		#	endIndex = -2
		#else:
		#	endIndex = -1
		# Accept most recent entry as the last
		endIndex = -1
		startIndex = totalEnt - monthsOfHistory
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

		endIndex = startIndex + monthsOfHistory - 1
		tradeDates = sortedKeys[startIndex:endIndex]
		for tradeDate in tradeDates:
			sharesPurchasedTotal, totalInvested, leftOverCash = purchaseShares(stockHistory, tradeDate, leftOverCash, dollarsPerMonthInvested, sharesPurchasedTotal, totalInvested)
		printResults(sharesPurchasedTotal, stockHistory, sortedKeys, totalEnt, totalInvested, menuOption, symbol, sortedKeys[startIndex], sortedKeys[endIndex])
	else:
		print("Not enough history for this stock from API, try a shorter time period")
		
elif (int(menuOption) == 2):
	stockHistory, sortedKeys, totalEnt, symbol = getStockHistory()
	startYear = input("Enter starting year (format YYYY): ")
	yearsOfHistory = int(input("Enter duration (years): "))
	dollarsPerMonthInvested = int(input("Enter dollars per month invested: $ "))
	monthsOfHistory = 12 * yearsOfHistory
	totalMonthsOfHistoryRequired = (int(datetime.now().year) - int(startYear)) * 12
	if (totalEnt >= totalMonthsOfHistoryRequired):
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
		#print(tradeDates)
		for tradeDate in tradeDates:
			sharesPurchasedTotal, totalInvested, leftOverCash = purchaseShares(stockHistory, tradeDate, leftOverCash, dollarsPerMonthInvested, sharesPurchasedTotal, totalInvested)

		printResults(sharesPurchasedTotal, stockHistory, sortedKeys, totalEnt, totalInvested, menuOption, symbol, sortedKeys[startIndex], sortedKeys[endIndex])
	else:
		print("Not enough history for this stock from API, try a shorter time period")

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
		totalMonthsOfHistoryRequired = (datetime.now().year - startYear) * 12
		if (totalEnt >= totalMonthsOfHistoryRequired):
			# Last business day in month varies
			for day in range(25, 32):
				try:
					startIndex = sortedKeys.index("%s-01-%s" % (startYear, day))
				except:
					"Do nothing, dont error on exception"
				else:
					"Found Index"
					break

			endIndex = startIndex + monthsOfHistory - 1
			tradeDates = sortedKeys[startIndex:endIndex]

			for tradeDate in tradeDates:
				sharesPurchasedTotal, totalInvested, leftOverCash = purchaseShares(stockHistory, tradeDate, leftOverCash, dollarsPerMonthInvested, sharesPurchasedTotal, totalInvested)

			printResults(sharesPurchasedTotal, stockHistory, sortedKeys, totalEnt, totalInvested, menuOption, symbol, sortedKeys[startIndex], sortedKeys[endIndex])
			# API seems to like some wait time between requests
			time.sleep(1)
		else:
			print("Not enough history for this stock from API, try a shorter time period")

else:
	print("Invalid option chosen, try again...")

