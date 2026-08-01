def capitalize_first_last(sentence):
    # Write your code here
    captilize = sentence.split()
    
    result = []

    for val in captilize:
        if len(val) == 1:
            result.append(val.upper())
        else:
            new_word = val[0].upper() + val[1:-1]+val[-1].upper() 
            result.append(new_word)
            

    return " ".join(result)
