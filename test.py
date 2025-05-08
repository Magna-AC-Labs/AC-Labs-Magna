from Lab_01 import check_license_plate
from Lab_01 import check_common_plate
from colorama import Fore, Back, Style, init

passed = 0
total = 16
failed = 0

numbers = [
    "TM13SKY",
    "T113SSS",
    "TT00SSS",
    "TM111SS",
    "TM 01 SMT",
    "CS 111 SME",
    "SC 11 SMA",
    "MH 01 S!S",
    "mh 101 sss",
    "B 101 ANA",
    "B 11 ANA",
    "AB 00 BBB",
    "CJ 1 CCC",
    "B1 01 AAA", # Returneaza true pentru ca dupa prelucrare spatii o sa am B101AAA, cazul Bucuresti cu 3 cifre
    "BM 11 Asa"
    ,"CS 01231"
    ,"BH 0121313"
    ,"AR 13124"
    ,"CT 013141"
    ,"CJ 13141"
    ,"VL 01"
    ,"A 12331"
    ,"B 12321"
    ,"A 12314141"
    ,"CD 146 512"
    ,"TC 123 123"
    ,"CO 123 132"
    ,"CD 1231"
    ,"IF 001212"
    ,"MAI 12345"
    ,"IMA 12345"
    ,"IF O4 LYD"
    ,"BT 10 AAA"
]

expectedOutput = [
    True, 
    False,
    False,
    False,
    True, 
    False, 
    False, 
    False, 
    False,
    True,
    True,
    False, 
    False,
    True,
    False
    ,True
    ,False
    ,True
    ,True
    ,True
    ,False
    ,True
    ,False
    ,False
    ,True
    ,True
    ,True
    ,False
    ,False
    ,True
    ,False
    ,True
    ,True
]

failedTestContents = []

for i in range(len(numbers)):
    if check_license_plate(numbers[i]) != expectedOutput[i]:
        failed += 1
        failedTestContents.append(numbers[i])
    else:
        passed +=1

    
print(Fore.GREEN + "Passed tests " + Style.BRIGHT + str(passed) + Style.RESET_ALL + Fore.RESET)
print(Fore.RED + "Failed tests " + Style.BRIGHT + str(failed) + Style.RESET_ALL + Fore.RESET)

print("")
if failed != 0:
    print(Fore.RED + "Failed cases: " + Fore.RESET)
    for i in range(failed):
        print(Fore.YELLOW + failedTestContents[i], "output: ", check_license_plate(failedTestContents[i]))