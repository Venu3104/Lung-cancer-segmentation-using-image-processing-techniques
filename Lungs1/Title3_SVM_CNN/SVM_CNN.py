
from tkinter import messagebox
from tkinter import *
from tkinter import simpledialog
import tkinter
from tkinter import filedialog
import matplotlib.pyplot as plt
import numpy as np
from tkinter.filedialog import askopenfilename
import pandas as pd 
import os
import cv2
import numpy as np
from sklearn import svm
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.decomposition import PCA
from keras.utils.np_utils import to_categorical
from keras.layers import  MaxPooling2D
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Convolution2D
from keras.models import Sequential

main = tkinter.Tk()
main.title("Detection of Lung cancer from CT image using SVM classification and compare the survival rate of patients using 3D Convolutional neural network(3D CNN)on lung nodules data set")
main.geometry("1300x1200")

global filename
global classifier
global svm_sr, cnn_sr
global X, Y
global X_train, X_test, y_train, y_test
global pca

def uploadDataset():
    global filename
    filename = filedialog.askdirectory(initialdir=".")
    text.delete('1.0', END)
    text.insert(END,filename+" loaded\n");
    
    
def splitDataset():
    global X, Y
    global X_train, X_test, y_train, y_test
    global pca
    text.delete('1.0', END)
    X = np.load('features/X.txt.npy')
    Y = np.load('features/Y.txt.npy')
    X = np.reshape(X, (X.shape[0],(X.shape[1]*X.shape[2]*X.shape[3])))

    pca = PCA(n_components = 100)
    X = pca.fit_transform(X)
    print(X.shape)
    X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2)
    text.insert(END,"Total CT Scan Images Found in dataset : "+str(len(X))+"\n")
    text.insert(END,"Train split dataset to 80% : "+str(len(X_train))+"\n")
    text.insert(END,"Test split dataset to 20%  : "+str(len(X_test))+"\n")


def executeSVM():
    global classifier
    global svm_sr
    text.delete('1.0', END)
    cls = svm.SVC() 
    cls.fit(X_train, y_train)
    predict = cls.predict(X_test)
    svm_sr = accuracy_score(y_test,predict) * 100
    classifier = cls
    text.insert(END,"SVM Survival Rate : "+str(svm_sr)+"\n")

def executeCNN():
    global cnn_sr
    X = np.load('features/X.txt.npy')
    Y = np.load('features/Y.txt.npy')
    Y = to_categorical(Y)
    classifier = Sequential()
    classifier.add(Convolution2D(32, 3, 3, input_shape = (64, 64, 3), activation = 'relu'))
    classifier.add(MaxPooling2D(pool_size = (2, 2)))
    classifier.add(Convolution2D(32, 3, 3, activation = 'relu'))
    classifier.add(MaxPooling2D(pool_size = (2, 2)))
    classifier.add(Flatten())
    classifier.add(Dense(output_dim = 256, activation = 'relu'))
    classifier.add(Dense(output_dim = 2, activation = 'softmax'))
    print(classifier.summary())
    classifier.compile(optimizer = 'adam', loss = 'categorical_crossentropy', metrics = ['acc'])
    hist = classifier.fit(X, Y, batch_size=16, epochs=10, shuffle=True, verbose=2)
    hist = hist.history
    acc = hist['acc']
    cnn_sr = acc[9] * 100
    text.insert(END,"CNN Survival Rate : "+str(cnn_sr)+"\n")
    

def predictCancer():
    filename = filedialog.askopenfilename(initialdir="testSamples")
    img = cv2.imread(filename)
    img = cv2.resize(img, (64,64))
    im2arr = np.array(img)
    im2arr = im2arr.reshape(64,64,3)
    im2arr = im2arr.astype('float32')
    im2arr = im2arr/255
    test = []
    test.append(im2arr)
    test = np.asarray(test)
    test = np.reshape(test, (test.shape[0],(test.shape[1]*test.shape[2]*test.shape[3])))
    test = pca.transform(test)
    predict = classifier.predict(test)[0]
    msg = ''
    if predict == 0:
        msg = "Uploaded CT Scan is Normal"
    if predict == 1:
        msg = "Uploaded CT Scan is Abnormal"
    img = cv2.imread(filename)
    img = cv2.resize(img, (400,400))
    cv2.putText(img, msg, (10, 25),  cv2.FONT_HERSHEY_SIMPLEX,0.7, (0, 255, 255), 2)
    cv2.imshow(msg, img)
    cv2.waitKey(0)    

def graph():
    height = [svm_sr, cnn_sr]
    bars = ('SVM Survival Rate','CNN Survival Rate')
    y_pos = np.arange(len(bars))
    plt.bar(y_pos, height)
    plt.xticks(y_pos, bars)
    plt.show()

font = ('times', 14, 'bold')
title = Label(main, text='Detection of Lung cancer from CT image using SVM classification and compare the survival rate of patients using 3D Convolutional neural network(3D CNN)on lung nodules data set')
title.config(bg='deep sky blue', fg='white')  
title.config(font=font)           
title.config(height=3, width=120)       
title.place(x=0,y=5)

font1 = ('times', 12, 'bold')
text=Text(main,height=20,width=150)
scroll=Scrollbar(text)
text.configure(yscrollcommand=scroll.set)
text.place(x=50,y=120)
text.config(font=font1)


font1 = ('times', 13, 'bold')
uploadButton = Button(main, text="Upload Lung Cancer Dataset", command=uploadDataset)
uploadButton.place(x=50,y=550)
uploadButton.config(font=font1)  

readButton = Button(main, text="Read & Split Dataset to Train & Test", command=splitDataset)
readButton.place(x=350,y=550)
readButton.config(font=font1) 

svmButton = Button(main, text="Execute SVM Algorithms", command=executeSVM)
svmButton.place(x=50,y=600)
svmButton.config(font=font1) 

kmeansButton = Button(main, text="Execute CNN Algorithm", command=executeCNN)
kmeansButton.place(x=350,y=600)
kmeansButton.config(font=font1) 

predictButton = Button(main, text="Predict Lung Cancer", command=predictCancer)
predictButton.place(x=50,y=650)
predictButton.config(font=font1)

graphButton = Button(main, text="Survival Rate Graph", command=graph)
graphButton.place(x=350,y=650)
graphButton.config(font=font1) 

main.config(bg='LightSteelBlue3')
main.mainloop()
