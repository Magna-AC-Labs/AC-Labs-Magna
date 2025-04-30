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

def check_common_plate(plate_number):
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

def check_red_license_plate(plate_number):
    #CS + [3 <-> 6] digits
    string = plate_number.replace(" ", "")
    string = string.upper()
    
    county = string[0:2]
    number = string[2:]
    
    for i in number:
        if i.isalpha() == True:
            return False
    
    if(len(number) >= 3 and len(number) <= 6):     #? 3 up to 6 digits
        if number[0] == '0' and number[1] != '0':   #? first one must be 0 and the second one must be non zero
            return check_county(county)
    
    return False

def check_long_term_license_plate(plate_number):
    #CS + [3 <-> 6] digits
    string = plate_number.replace(" ", "")
    string = string.upper()
    
    county = string[0:2]
    number = string[2:]
    
    for i in number:
        if i.isalpha() == True:
            return False
        
    if(len(number) >= 3 and len(number) <= 6):     #? 3 up to 6 digits
        if number[0] != '0':   #? first one must be non-zero
            return check_county(county)
    
    return False

def check_army_license_plate(plate_number):
    #A + [3 <-> 7 ] digits (3 up to 7 digits)
    string = plate_number.replace(" ", "")
    string = string.upper()
    
    number = string[1:]
    if(string[0] == 'A'):  # Starts with letter 'A'
        if(len(number) >= 3 and len(number) <= 7):  # 3 up to 7 digits
            for i in number:
                if i.isalpha():
                    return False
            return True
    return False
    
def check_police_license_plate(plate_number):
    #MAI + []
    #! Aici nu stiu ce format are, MAI + 4 cifre? MAI + NNN + LL?
    return False

def check_diplomatic_license_plate(plate_number):
    #CD 146 512
    #TC 146 512
    #CO 146 512
    
    string = plate_number.replace(" ", "")
    string = string.upper()
    
    county = string[0:2]
    number = string[2:]
    
    if(county == "CD" or county == "TC" or county == "CO"):
        if(len(number) == 6):
            for i in number:
                if i.isalpha():
                    return False
            return True
    return False
 
def check_license_plate(plate_number):
    if(check_common_plate(plate_number)):
        print("Common plate -> ", plate_number)
        return True

    if(check_red_license_plate(plate_number)):
        print("Red plate -> ", plate_number)
        return True

    if(check_long_term_license_plate(plate_number)):
        print("Long_Term -> ", plate_number)
        return True
    
    if(check_army_license_plate(plate_number)):
        print("Army -> ", plate_number)
        return True
    
    if(check_diplomatic_license_plate(plate_number)):
        print("Diplomatic -> ", plate_number)
        return True
    
    return False