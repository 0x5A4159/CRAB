from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
import random
import time
import pickle
import numpy as np
import os
from imagelib import imageRandomizer

opentime = time.time_ns()

class NeuralBuilder:
    def __init__(self, threadnum):
        self.pathtoimages = "/pfpanalyzer/naziimages/"
        self.starttime = time.time_ns()
        self.threadnum = threadnum

        # This is a really bad method of training, but it should work for the time being
        try:
            self.regmodel = pickle.load(open(f"32batchbestmodel{self.threadnum}.sav",'rb'))
            print("Loaded pickle model")
            self.lastbestscore = .95
        except:
            # oh rectified linear activation, you are so computationally efficient i love you
            self.regmodel = MLPClassifier(activation='relu',hidden_layer_sizes=(1024,512))
            print("Starting new model")
            self.lastbestscore = 0
        self.divtomulti = (1/255)
        self.cluster = 32
        print(f"Init threadbuild {self.threadnum}\n"
              f"Cluster size: {self.cluster}\n\n")


    # load an array of 32x32 images to an array to be processed for training
    def loadimages(self):
        self.xlists = []
        self.ylists = []
        for i in range(self.cluster):
            selectedfolder = random.choice(os.listdir(self.pathtoimages))
            selectedimg = random.choice(os.listdir(self.pathtoimages+selectedfolder+"/"))

            # Please restructure with pathlib or some other pathing library!!!
            imgdata = imageRandomizer(f"{self.pathtoimages}{selectedfolder}/{selectedimg}")
            if selectedfolder == 'negative':
                self.xlists.append(imgdata*self.divtomulti)
                self.ylists.append(0)
            else:
                self.xlists.append(imgdata*self.divtomulti)
                self.ylists.append(1)



    def feedimages(self):
        xtrain,xtest,ytrain,ytest = train_test_split(self.xlists,self.ylists,test_size=0.8,random_state=random.randint(
            1,100))
        self.regmodel.partial_fit(xtrain, ytrain, classes=[0,1])
        score = self.regmodel.score(xtest, ytest)
        # I know printing to output technically slows it down but just gauging the average time to run a training set
        print(f"Threadnum {self.threadnum}")
        print(f'Time from start: {(time.time_ns() - opentime) * 0.000000001}')
        print(f'Current accuracy: {score}\n')
        if score > self.lastbestscore or score >= 0.99:
            pickle.dump(self.regmodel, open(f'32batchbestmodel{self.threadnum}.sav', 'wb'))
            print("Saved last best model")
            self.lastbestscore = score
        self.loadimages()
