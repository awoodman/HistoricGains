import math

initVal = 0
years = 10
rate = .1
compInterval = 12
monthlyAdd = 500
totalAmt = initVal + (12 * years * monthlyAdd)

print("Initial Value: %s" % initVal)

firstTerm = initVal * math.pow(1 + (rate / compInterval), (compInterval * years))
secondTerm = monthlyAdd * (((math.pow((1 + (rate / compInterval)), (compInterval * years))) - 1) / (rate / compInterval)) 
finalVal = firstTerm + secondTerm

print("Total amount invested: %s" % totalAmt)
print("Value after %s years: %s" % (years, finalVal))
