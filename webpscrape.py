import re
import requests
# import time
import random
import os


with open('discordpage.txt', 'rb') as file:
    i = file.read()
    i = rf"{i}"
    pattern = re.compile(r'https:.{81,110}(jpg|png)')
    matches = pattern.finditer(i)
    for match in matches:
        print(match[0])
        response = requests.get(match[0])
        randstring = "".join(chr(random.randint(65, 90)) for i in range(10))
        if response.status_code == 200:
            f = open(f'/pfpanalyzer/steamavatar/{randstring}.png', 'wb')
            f.write(response.content)
            f.close()
            with open(f"/steamavatar/{randstring}.png", 'wb') as f:
                f.write(response.content)