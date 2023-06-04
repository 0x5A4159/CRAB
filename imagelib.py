from PIL import Image, ImageOps
import random
import os
import numpy as np

# imageRandomizer creates multiple copies of an image with different placements and zoom to help artificially expand
# data sets

def imageRandomizer(image):
    with Image.open(image) as file:
        file = ImageOps.grayscale(file)
        if random.randint(0,1) == 1:
            file = ImageOps.mirror(file)
        if random.randint(0,1) == 1:
            file = file.rotate(random.randint(-45, 45))
            x1,y1,x2,y2 = file.getbbox()
            x1,y1,x2,y2 = x1 + x2*0.1 ,y1 + y2 * 0.1,x2 * 0.9,y2 * 0.9
            file = file.crop((x1,y1,x2,y2))
        file = file.resize((32, 32))
        img = np.asarray(file.getdata())
        empty = []
        fullimage = []
        for i in img:
            randomint = random.randint(0,5)
            xadjusted = i*0.003921568627451
            if randomint == 0:
                rand1 = random.randint(-3,-1)
                rand2 = random.randint(1,3)
                empty.append((xadjusted + (random.randint(rand1,rand2)*.1)))
            else:
                empty.append(xadjusted)
        fullimage.append(empty)
        fullimage = np.asarray(fullimage)[0]
    return fullimage

