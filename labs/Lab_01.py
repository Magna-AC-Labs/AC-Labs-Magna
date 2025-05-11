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
    return number.isdigit() and number != "00"

def check_name(name):
    for char in name:
        if not char.isalpha():
            return False
    return True

def check_license_plate(plate_number):
    string = plate_number.replace(" ", "").upper()

    if len(string) == 7:

        county = string[:2]

        number = string[2:4]

        name = string[4:7]

        return check_county(county) and check_numbers(number) and check_name(name)
    elif len(string) == 6:

        county = string[:2]

        number = string[2:4]

        name = string[4:6]

        return check_county(county) and check_numbers(number) and check_name(name)
    else:
        return False

# Example test

plates = ["TM 12 ABC", "B 123 XYZ", "CJ 34 QWE", "TM123ABC", "XY 99 ZZZ", "TM 00 ABC", "TM 12 AB1"]

for plate in plates:
    if check_license_plate(plate):
        print(f"{plate} is a valid license plate.")
    else:
        print(f"{plate} is not a valid license plate.")