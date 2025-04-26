import re

valid_counties = ["AB", "AR", "AG", "BC", "BH", "BN", "BR", "BT", "BV", "BZ", "CS",
                  "CL", "CJ", "CT", "CV", "DB", "DJ", "GL", "GR", "GJ", "HR", "HD",
                  "IL", "IS", "IF", "MM", "MH", "MS", "NT", "OT", "PH", "SM", "SJ",
                  "SB", "SV", "TR", "TM", "TL", "VS", "VL", "VN", "B"]  

def check_license_plate(plate, allowed_county="TM"):
    plate = plate.strip().upper()

    
    # format 1-2 litere + spatiu + 2-3 cifre + spatiu + 3 litere
    pattern = r"^([A-Z]{1,2})\s(\d{2,3})\s([A-Z]{3})$"

    match = re.match(pattern, plate)
    
    if not match:
        return False

    county = match.group(1)
    return county in valid_counties


# Test
plates = ["TM 12 ABC", "B 123 XYZ", "CJ 34 QWE", "TM123ABC", "XY 99 ZZZ"]

for plate in plates:
    if check_license_plate(plate):
        print(f"{plate} is a valid license plate.")
    else:
        print(f"{plate} is not a valid license plate.")
