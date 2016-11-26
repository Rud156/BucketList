search_terms = ["Natsu", "Erza", "Fairy", "Tail"]
for i in range(0, len(search_terms)):
    for j in range(i, len(search_terms)):
        result = ""
        for k in range(i, j + 1):
            result += search_terms[k]
            if k != j:
                result += " "
        print "Result String: " + result
