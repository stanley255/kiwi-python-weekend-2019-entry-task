"""
Assignment: Python weekend Kiwi.com - Entry task
Created By: Stanislav Pekarovič
Date: 12.06.2019
Link: https://pw.engeto.com/

Task is to find all combinations of flights for passengers with no bags, one bag or two bags are able to travel,
having 1 to 4 hours for each transfer between flights.

For input CSV given app tries to find all combinations of trips(flight or flight combinations that fulfills
task requirements) for amount of baggage in BAGGAGE_AMOUNT array

I've considered even one flight as combination
Also:
 - A->B->A->B is not a valid combination
 - A->B->A is a valid combination
And last but not least app also shows flight combinations following same destinations when there are different flights
(flight_numbers) taken

App was tested and developed on Windows using bash command:
cat input.csv | python find_combinations.py
"""

import sys
import fileinput
from datetime import datetime, timedelta

COLUMN_COUNT = 8  # Number of columns in loaded CSV file
BAGGAGE_AMOUNT = [0, 1, 2]  # Amount of baggage to check flights and their price


# Flight class that has all information about flight loaded from CSV
class Flight:
    def __init__(self, flightInfo):
        flightInfoVector = flightInfo.split(',')
        if len(flightInfoVector) < COLUMN_COUNT:
            sys.stderr.write("Not enough flight info input data provided!")
            exit()
        self.source = flightInfoVector[0]
        self.destination = flightInfoVector[1]
        try:
            self.departure = datetime.strptime(flightInfoVector[2], '%Y-%m-%dT%X')
            self.arrival = datetime.strptime(flightInfoVector[3], '%Y-%m-%dT%X')
        except ValueError:
            sys.stderr.write("Error in date format of input data!")
            exit()
        self.flightNumber = flightInfoVector[4]
        try:
            self.price = int(flightInfoVector[5])
            self.bagsAllowed = int(flightInfoVector[6])
            self.bagPrice = int(flightInfoVector[7])
        except ValueError:
            sys.stderr.write("Error in integer format of input data!")
            exit()

    def transferTimeToFlight(self, flightToCheck):
        if (self.departure > flightToCheck.departure):
            return self.departure - flightToCheck.arrival
        elif (self.departure < flightToCheck.departure):
            return flightToCheck.departure - self.arrival
        else:
            return flightToCheck.departure - flightToCheck.departure

    def getBaggagePrice(self, baggageAmount):
        if baggageAmount > self.bagsAllowed:
            raise ValueError("This flight does not support given amount of baggage")
        return self.bagPrice * baggageAmount


# Trip is a class that connects one or multiple flights together and forms one trip that meets requirements
# of given assignment
class Trip:
    def __init__(self, flight, trip):
        if trip is None:
            self.flights = [flight]
            self.cannotVisitAgain = set()
            self.cannotVisitAgain.add(flight.destination)
        else:
            self.flights = []
            self.cannotVisitAgain = set()
            for originalFlight in trip.flights:
                self.flights.append(originalFlight)
            for originalVisited in trip.cannotVisitAgain:
                self.cannotVisitAgain.add(originalVisited)
            self.flights.append(flight)
            self.cannotVisitAgain.add(flight.destination)

    def getLastFlight(self):
        return self.flights[len(self.flights) - 1]

    def getStartingDestination(self):
        return self.flights[0].source

    def getPriceForFlights(self):
        price = 0
        for flight in self.flights:
            price += flight.price
        return price

    def getPriceForBaggage(self, baggageAmount):
        price = 0
        for flight in self.flights:
            price += flight.getBaggagePrice(baggageAmount)
        return price

    def getTotalPrice(self, baggageAmount):
        price = 0
        for flight in self.flights:
            price += flight.price + flight.getBaggagePrice(baggageAmount)
        return price


# Function planTrip is called from main for each flight and baggage amount and recursively adding flights to trips
def planTrip(availableFlights, plannedTrips, trip):
    plannedTrips.append(trip)
    for flight in availableFlights:
        # Checks current destination against flight source
        if not (trip.getLastFlight().destination == flight.source):
            continue
        # Checks time difference
        timeDifference = trip.getLastFlight().transferTimeToFlight(flight)
        if not (timedelta(hours=1) <= timeDifference <= timedelta(hours=4)):
            continue
        # Checks if destination was visited or not
        if flight.destination not in trip.cannotVisitAgain:
            if flight.destination == trip.getStartingDestination():
                newTrip = Trip(flight, trip)
                plannedTrips.append(newTrip)
                # We do not longer need to add flights to trip because we have returned home :)
            else:
                # Creates new trip and runs recursion, because there could be some flights suitable for trip
                newTrip = Trip(flight, trip)
                planTrip(availableFlights, plannedTrips, newTrip)


flightInfo = []

lineCount = 0
for row in fileinput.input():
    # Check for header and skip it
    if lineCount == 0:
        lineCount += 1
        continue
    flightInfo.append(Flight(row))
    lineCount += 1
if lineCount == 0 or len(flightInfo) == 0:
    sys.stderr.write("Wrong input data provided!")
    exit()

for baggageAmount in BAGGAGE_AMOUNT:
    plannedTrips = []
    availableFlights = [flight for flight in flightInfo if flight.bagsAllowed >= baggageAmount]
    for flight in availableFlights:
        trip = Trip(flight, None)
        planTrip(availableFlights, plannedTrips, trip)

    print("******************************")
    print("Trips with " + str(baggageAmount) + " pieces of baggage")
    print("******************************")
    for trip in plannedTrips:
        print("******" + trip.flights[0].source + " to " + trip.getLastFlight().destination + "******")
        for flight in trip.flights:
            print("(" + flight.flightNumber + ")" + flight.source + " -> " + flight.destination + "(" + str(
                flight.price) + "€)")
        print("Price of flight(s): " + str(trip.getPriceForFlights()) + "€")
        print("Price of baggage: " + str(trip.getPriceForBaggage(baggageAmount)) + "€")
        print("Total price: " + str(trip.getTotalPrice(baggageAmount)) + "€")
        print()
    print("\n\n")
