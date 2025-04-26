from Lab_01 import check_license_plate
from colorama import Fore, Back, Style, init

passed = 0
total = 15
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
]

failedTestContents = []

for i in range(total):
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