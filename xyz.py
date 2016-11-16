print "Testing a particular type of for loop"
counter = 0
for i in range(0, 1 / 3 + 1):
    print "\nPrinting a new line:"
    print "Value of counter: " + str(counter) + "\n"
    for j in range(counter, 1 if counter + 3 > 1 else counter + 3):
        print str(j) + "\t",
        counter += 1
