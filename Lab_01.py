# TM 13 SKY -> license plate -> permission granted 
# " " to ""

def check_county(county):
    for i in county:
        if i.isdigit():  
            return False
        
    county_list = ["B", "AB", "AR", "AG", "BC", "BH", "BN", "BT", "BV", "BR", "BZ", "CS", "CL", "CJ",
                   "CT", "CV", "DB", "DJ", "GL", "GR", "GJ", "HR", "HD", "IL", "IS", "IF", "MM", "MH", "MS",
                   "NT", "OT", "PH", "SM", "SJ", "SB", "SV", "TR", "TM", "TL", "VL", "VS", "VN"]

    if county in county_list:
        return True
    else:
        return False
    
def check_numbers(number):
    for i in number:
        if i.isalpha():
            return False

    if number == "00":
        return False

    return True

def check_numbers_B(number):
    for i in number:
        if i.isalpha():
            return False;
    
    if number == "000":
        return False

    return True

def check_name(name):
    for i in name:
        if i.isalpha() == False:
            return False
    return True

def check_license_plate(plate_number):
    string = plate_number.replace(" ", "")
    string = string.upper()
    #TM13SKY

    if len(string) == 7:
        #split
        #* Bucharest case with 3 digits
        if(string[0] == 'B'):
            number = string[1:4]
            name = string[4:]
            
            return check_numbers_B(number) and check_name(name)
        else :
            #* Common plate with 2 letters for county and 2 digits for number
            county = string[:2]
            number = string[2:4]
            name = string[4:]

            return check_county(county) and check_numbers(number) and check_name(name)
    elif len(string) == 6:
        
        #* Bucharest with 2 digits
        if string[0] == 'B':
            number = string[1:3]
            name = string[3:]
            
            return check_numbers(number) and check_name(name)
        else: 
            return False
    else:
        #print("Invalid plate number")
        return False
    