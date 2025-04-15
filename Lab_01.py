# TM 13 SKY -> license plate -> permission granted 
# " " to ""

def check_county(county):
    for i in county:
        if i.isdigit():
            return False
        
    county_list = ["TM", "CS", "GJ", "MH"]

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

def check_name(name):


def check_license_plate(plate_number):
    string = plate_number.replace(" ", "")
    

    string = string.upper()
    #TM13SKY

    if len(string) == 7:
        #split
        county = string[:2]

        if check_county(county) == False:
            return False
        
        number = string[2:4]

        if check_numbers(number) == False:
            return False
        
        name = string[4:7]

        #checks
        print(check_county(county))
        print(check_numbers(number))

        print(county)
        print(number)
        print(name)
    elif len(string) == 6:
        print("B")
    else:
        print("Invalid plate number")

check_license_plate("tm 00 SKY")


# count_region = 0
#         count_number = 0

#         region = "" 
#         number = "" 
#         name = ""

#         # edge case -> 5C 48 ABC 
#         # edge case -> TM 00 ABC

#         for i in string:
#             if i.isalpha() and count_region < 2 :
#                 region += i
#                 count_region += 1
#             elif i.isdigit() and count_number < 2:
#                 number += i
#                 count_number += 1
#             else:
#                 name += i
            
#         print(region)
#         print(number)
#         print(name)