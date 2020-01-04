from tkinter import *
from tkinter.filedialog import askopenfilename
from PIL import ImageTk, Image
import time
import numpy as np
from tkinter import messagebox
import asm
import copy
import multiprocessing as mp
from io import BytesIO
from multiprocessing import Process, Manager
from numba import jit, cuda

global imageLeft
global imageRight


@jit(target ="cuda")
def ThreadFunctionWithArrays(startPointY, endPointY, pixelsWidth, pixelsArray1, pixelsArray2, arrayToReturn, procNumber):
    numberOfRows = endPointY - startPointY
    pixelArray = GenerateEmptyPartMatrix(pixelsWidth, numberOfRows)
    y = 0
    for j in range(startPointY, endPointY):
        for i in range(0, pixelsWidth):
            r1, g1, b1 = pixelsArray1.getpixel((i, j))
            r2, g2, b2 = pixelsArray2.getpixel((i, j))
            pixelArray[y][i] = (
                r1 * 0.4561 + g1 * 0.500484 + b1 * 0.176381 - r2 * 0.0434706 - g2 * 0.0879388 - b2 * 0.00155529,
                - r1 * 0.0400822 - g1 * 0.0378246 - b1 * 0.0157589 + r2 * 0.378476 + g2 * 0.73364 - b2 * 0.0184503,
                - r1 * 0.0152161 - g1 * 0.0205971 - b1 * 0.00546856 - r2 * 0.0721527 - g2 * 0.112961 + b2 * 1.2264)
        y += 1
    arrayToReturn[procNumber] = pixelArray


def ThreadFunctionWithArraysSimple(startPointY, endPointY, pixelsWidth, pixelsArray1, pixelsArray2, arrayToReturn,
                             procNumber):
    numberOfRows = endPointY - startPointY
    pixelArray = GenerateEmptyPartMatrix(pixelsWidth, numberOfRows)
    y = 0
    for j in range(startPointY, endPointY):
        for i in range(0, pixelsWidth):
            r1, g1, b1 = pixelsArray1.getpixel((i, j))
            r2, g2, b2 = pixelsArray2.getpixel((i, j))
            pixelArray[y][i] = (
                0.299 * r1 + 0.587 * g1 + 0.114 * b1,
                0.299 * r2 + 0.587 * g2 + 0.114 * b2,
                0.299 * r2 + 0.587 * g2 + 0.114 * b2)
        y += 1
    arrayToReturn[procNumber] = pixelArray


def AsmMethod(arr1, arr2, size, arrayToReturn, procNumber):
    array = asm.convert_image(arr1, arr2, size)
    arrayToReturn[procNumber] = array


def CreateImage(anaglyphPixelArray, name):
    pixelsArray = np.array(anaglyphPixelArray, dtype=np.uint8)
    newImage = Image.fromarray(pixelsArray)
    newImage.save(name)


def CreateImageFromBuffer(pixelArray, name, width, height):
    newImage = Image.frombytes("RGB", (width, height), pixelArray)
    newImage = newImage.transpose(Image.ROTATE_180)
    newImage.save(name)


def GenerateEmptyPartMatrix(width, height):
    pixelArray = [[(0, 0, 0) for x in range(width)] for y in range(height)]
    return pixelArray


def StartDuboisThreading():
    global imageLeft
    global imageRight
    numberOfThreads = threadSlider.get()
    width, height = imageLeft.size
    rgb_imgLeft = imageLeft.convert('RGB')
    rgb_imgRight = imageRight.convert('RGB')
    rowsPerThread = int(height / numberOfThreads)
    processes = list()
    start = time.time()
    manager = Manager()
    d1 = manager.dict()

    if (rbValue.get() == 2):
        for i in range(0, numberOfThreads):
            if (i != numberOfThreads - 1):
                processes.append(Process(target=ThreadFunctionWithArrays, args=(
                    i * rowsPerThread, (i + 1) * rowsPerThread, width, rgb_imgLeft, rgb_imgRight, d1, i)))
                processes[i].start()
            else:
                processes.append(Process(target=ThreadFunctionWithArrays, args=(
                    i * rowsPerThread, height, width, rgb_imgLeft, rgb_imgRight, d1, i)))
                processes[i].start()
    else:
        for i in range(0, numberOfThreads):
            bytes1 = BytesIO()
            imageLeft.save(bytes1, 'bmp')
            bytes2 = BytesIO()
            imageRight.save(bytes2, 'bmp')
            bytes1 = bytes1.getvalue()
            bytes2 = bytes2.getvalue()
            bytes1 = bytes1[54:]
            bytes2 = bytes2[54:]
            sizeOfBytes = height*width*3

            if (i != numberOfThreads - 1):
                processBytes1 = bytes1[i * rowsPerThread*width:(i+1)*rowsPerThread*width*3]
                processBytes2 = bytes2[i * rowsPerThread*width:(i+1)*rowsPerThread*width*3]
                processes.append(Process(target=AsmMethod, args=(
                    processBytes1, processBytes2, width*rowsPerThread, d1, i)))
                processes[i].start()
            else:
                processBytes1 = bytes1[i * rowsPerThread * width:sizeOfBytes]
                processBytes2 = bytes2[i * rowsPerThread * width:sizeOfBytes]
                processes.append(Process(target=AsmMethod, args=(
                    processBytes1, processBytes2, sizeOfBytes-(i*rowsPerThread), d1, i)))
                processes[i].start()

    pixelArray = None
    for i in range(0, numberOfThreads):
        processes[i].join()
        if pixelArray is None:
            pixelArray = d1[i]
        else:
            pixelArray = np.append(pixelArray, d1[i], axis=0)
    end = time.time()
    timeElapsed = end - start
    operationTimeText.configure(text='Time of operation: ' + timeElapsed.__str__())
    image = None

    if rbValue.get() == 2 :
        CreateImage(pixelArray, 'DuboisAnaglyph.png')
        image = Image.open('DuboisAnaglyph.png')
    else:
        CreateImageFromBuffer(pixelArray, 'DuboisAnaglyphASM.png', width, height)
        image = Image.open('DuboisAnaglyphASM.png')

    image = image.resize((150, 267))
    render = ImageTk.PhotoImage(image)
    imageLabel4.configure(image=render)
    imageLabel4.photo_ref = render


def StartCasualThreading():
    global imageLeft
    global imageRight
    numberOfThreads = threadSlider.get()
    width, height = imageLeft.size
    rgb_imgLeft = imageLeft.convert('RGB')
    rgb_imgRight = imageRight.convert('RGB')
    rowsPerThread = int(height / numberOfThreads)
    processes = list()
    start = time.time()
    manager = mp.Manager()
    dictionaries = manager.dict()

    for i in range(0, numberOfThreads):
        copyImgLeft = copy.deepcopy(rgb_imgLeft)
        copyImgRight = copy.deepcopy(rgb_imgRight)
        if (i != numberOfThreads - 1):
            processes.append(Process(target=ThreadFunctionWithArraysSimple, args=(
                i * rowsPerThread, (i + 1) * rowsPerThread, width, copyImgLeft, copyImgRight,
                dictionaries, i)))
            processes[i].start()
        else:
            processes.append(Process(target=ThreadFunctionWithArraysSimple, args=(
                i * rowsPerThread, height, width, copyImgLeft, copyImgRight,
                dictionaries, i)))
            processes[i].start()
    pixelArray = None
    for i in range(0, numberOfThreads):
        processes[i].join()
        if pixelArray is None:
            pixelArray = dictionaries[i]
        else:
            pixelArray = np.append(pixelArray, dictionaries[i], axis=0)

    end = time.time()
    timeElapsed = end - start
    operationTimeText.configure(text='Time of operation: ' + timeElapsed.__str__())
    CreateImage(pixelArray, 'SimpleAnaglyph.png')
    image = Image.open('SimpleAnaglyph.png')
    image = image.resize((150, 267))
    render = ImageTk.PhotoImage(image)
    imageLabel3.configure(image=render)
    imageLabel3.photo_ref = render

def OnLoadImage(numberOfPhoto):
    path = askopenfilename()
    if path:
        image = Image.open(path)
        imageR = image.resize((150, 267))
        render = ImageTk.PhotoImage(imageR)
        if numberOfPhoto == 1:
            global imageLeft
            imageLeft = image
            rgb_imgLeft = imageLeft.convert('RGB')
            imageLabel1.configure(image=render)
            imageLabel1.photo_ref = render
            global image1Loaded
            image1Loaded = True
        else:
            global imageRight
            imageRight = image
            imageLabel2.configure(image=render)
            imageLabel2.photo_ref = render
            global image2Loaded
            image2Loaded = True
        if image1Loaded == True and image2Loaded == True:
            GenerateCasualB.configure(state='normal')
            GenerateDuboisB.configure(state='normal')
    else:
        messagebox.showerror('Image error', 'Image was not loaded properly')



# Main program starts here
image1Loaded = False
image2Loaded = False

# Generate window
root = Tk()
root.geometry("800x600")
root.title("Moncochromatic anaglyph converter")
root.resizable(width=False, height=False)

# Adjust grid weights parameters
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
root.columnconfigure(2, weight=1)
root.columnconfigure(3, weight=1)
root.rowconfigure(0, weight=1)
root.rowconfigure(1, weight=1)
root.rowconfigure(2, weight=1)
root.rowconfigure(3, weight=1)
root.rowconfigure(4, weight=1)

# Create buttons
loadImg1B = Button(root, text='Load image1', command=lambda: OnLoadImage(1), width=16,
                   height=5)
loadImg2B = Button(root, text='Load image2', command=lambda: OnLoadImage(2), width=16,
                   height=5)
GenerateCasualB = Button(root, text='Generate Basic\n Anaglyph', command=lambda: StartCasualThreading(), width=16, height=5,
                         state='disabled')
GenerateDuboisB = Button(root, text='Generate Dubois\n Anaglyph', command=lambda: StartDuboisThreading(), width=16,
                         height=5,
                         state='disabled')
loadImg1B.grid(row=2, column=0, sticky='n')
loadImg2B.grid(row=2, column=1, sticky='n')
GenerateCasualB.grid(row=2, column=2, sticky='n')
GenerateDuboisB.grid(row=2, column=3, sticky='n')

# Create image labels
templateImage = Image.open('template.png')
templateImageRend = ImageTk.PhotoImage(templateImage)
imageLabel1 = Label(root, image=templateImageRend)
imageLabel2 = Label(root, image=templateImageRend)
imageLabel3 = Label(root, image=templateImageRend)
imageLabel4 = Label(root, image=templateImageRend)
imageLabel1.grid(row=0, column=0, sticky='nesw')
imageLabel2.grid(row=0, column=1, sticky='nesw')
imageLabel3.grid(row=0, column=2, sticky='nesw')
imageLabel4.grid(row=0, column=3, sticky='nesw')

# Create text for thread
threadText = Label(root, text='Choose number of threads')
threadText.grid(row=3, column=0, columnspan=2, sticky='s')

# Create text for time of operaiton
operationTimeText = Label(root, text='Time of operation: ')
operationTimeText.grid(row=3, column=2, columnspan=2, sticky='n')

# Create threadSlider
threadSlider = Scale(root, from_=1, to=8, orient='horizontal', length=300)
threadSlider.grid(row=4, column=0, columnspan=2, sticky='n')

# Add frame for radio buttons
optionFrame = LabelFrame(root, text='Function Details')
optionFrame.grid(row=3, column=0, columnspan=2, sticky='n')

# Radio buttons
rbValue = IntVar()
rbValue.set(2)
assemblyRadio = Radiobutton(optionFrame, text="Assembly", value=1, variable=rbValue)
pythonRadio = Radiobutton(optionFrame, text="Python", value=2, variable=rbValue)
assemblyRadio.grid(row=0, column=0, sticky='w')
pythonRadio.grid(row=1, column=0, sticky='w')

root.mainloop()
