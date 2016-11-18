print "Testing a particular type of for loop"
counter = 0
value = 4
for i in range(0, value / 3 + 1):
    print "\nPrinting a new line:"
    print "Value of counter: " + str(counter) + "\n"
    for j in range(counter, value if counter + 3 > value else counter + 3):
        print str(j) + "\t",
        counter += 1
