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
#from numba import jit, cuda

global imageLeft
global imageRight


#@jit(target ="cuda")
def ThreadFunctionWithArrays(startPointY, endPointY, pixelsWidth, pixelsArray1, pixelsArray2, arrayToReturn, procNumber, isDubois):
    numberOfRows = endPointY - startPointY
    pixelArray = GenerateEmptyPartMatrix(pixelsWidth, numberOfRows)
    pixel_values1 = pixelsArray1.load()
    pixel_values2 = pixelsArray2.load()
    y = 0
    if(isDubois == True):
        for j in range(startPointY, endPointY):
            for i in range(0, pixelsWidth):
                r1, g1, b1 = pixel_values1[i, j]
                r2, g2, b2 = pixel_values2[i, j]
                pixelArray[y][i] = (
                    int(r1 * 0.4561 + g1 * 0.500484 + b1 * 0.176381 - r2 * 0.0434706 - g2 * 0.0879388 - b2 * 0.00155529),
                    int(- r1 * 0.0400822 - g1 * 0.0378246 - b1 * 0.0157589 + r2 * 0.378476 + g2 * 0.73364 - b2 * 0.0184503),
                    int(- r1 * 0.0152161 - g1 * 0.0205971 - b1 * 0.00546856 - r2 * 0.0721527 - g2 * 0.112961 + b2 * 1.2264))
            y += 1
    else:
        for j in range(startPointY, endPointY):
            for i in range(0, pixelsWidth):
                r1, g1, b1 = pixel_values1[i, j]
                r2, g2, b2 = pixel_values2[i, j]
                pixelArray[y][i] = (
                    int(0.299 * r1 + 0.587 * g1 + 0.114 * b1),
                    int(0.299 * r2 + 0.587 * g2 + 0.114 * b2),
                    int(0.299 * r2 + 0.587 * g2 + 0.114 * b2))
            y += 1
    arrayToReturn[procNumber] = pixelArray


def AsmMethod(arr1, arr2, size, arrayToReturn, procNumber):
    array = asm.convert_image(arr1, arr2, size)
    arrayToReturn[procNumber] = array


def AsmSimpleMethod(arr1, arr2, size, arrayToReturn, procNumber):
    array = asm.simpleconvert_image(arr1, arr2, size)
    arrayToReturn[procNumber] = array


def CreateImage(anaglyphPixelArray, name):
    pixelsArray = np.array(anaglyphPixelArray, dtype=np.uint8)
    newImage = Image.fromarray(pixelsArray)
    newImage.save(name)


def CreateImageFromBuffer(pixelArray, name, width, height):
    newImage = Image.frombytes("RGB", (width, height), pixelArray)
    newImage = newImage.transpose(Image.FLIP_LEFT_RIGHT)
    newImage.save(name)


def GenerateEmptyPartMatrix(width, height):
    pixelArray = [[(0, 0, 0) for x in range(width)] for y in range(height)]
    return pixelArray


def StartDuboisThreadsPy(rowsPerThread, height, width, d1, processes, numberOfThreads):
    global imageLeft
    global imageRight
    for i in range(0, numberOfThreads):
        if (i != numberOfThreads - 1):
            processes.append(Process(target=ThreadFunctionWithArrays, args=(
                i * rowsPerThread, (i + 1) * rowsPerThread, width, imageLeft, imageRight, d1, i, True)))
            processes[i].start()
        else:
            processes.append(Process(target=ThreadFunctionWithArrays, args=(
                i * rowsPerThread, height, width, imageLeft, imageRight, d1, i, True)))
            processes[i].start()

def StartCasualThreadsPy(rowsPerThread, height, width, d1, processes, numberOfThreads):
    global imageLeft
    global imageRight
    for i in range(0, numberOfThreads):
        if (i != numberOfThreads - 1):
            processes.append(Process(target=ThreadFunctionWithArrays, args=(
                i * rowsPerThread, (i + 1) * rowsPerThread, width, imageLeft, imageRight, d1, i, False)))
            processes[i].start()
        else:
            processes.append(Process(target=ThreadFunctionWithArrays, args=(
                i * rowsPerThread, height, width, imageLeft, imageRight, d1, i, False)))
            processes[i].start()


def StartDuboisThreadsAsm(bytes1,bytes2,rowsPerThread, width, d1, processes, sizeOfBytes, numberOfThreads):
    for i in range(0, numberOfThreads):
        if (i != numberOfThreads - 1):
            processBytes1 = bytes1[i * rowsPerThread * width * 3:(i + 1) * rowsPerThread * width * 3]
            processBytes2 = bytes2[i * rowsPerThread * width * 3:(i + 1) * rowsPerThread * width * 3]
            processes.append(Process(target=AsmMethod, args=(
                processBytes1, processBytes2, width * rowsPerThread * 3, d1, i)))
            processes[i].start()
        else:
            processBytes1 = bytes1[i * rowsPerThread * width * 3:sizeOfBytes]
            processBytes2 = bytes2[i * rowsPerThread * width * 3:sizeOfBytes]
            processes.append(Process(target=AsmMethod, args=(
                processBytes1, processBytes2, sizeOfBytes - (i * rowsPerThread * width * 3), d1, i)))
            processes[i].start()


def StartCasualThreadsAsm(bytes1, bytes2, rowsPerThread, width, d1, processes, sizeOfBytes, numberOfThreads):
    for i in range(0, numberOfThreads):
        if (i != numberOfThreads - 1):
            processBytes1 = bytes1[i * rowsPerThread * width * 3:(i + 1) * rowsPerThread * width * 3]
            processBytes2 = bytes2[i * rowsPerThread * width * 3:(i + 1) * rowsPerThread * width * 3]
            processes.append(Process(target=AsmSimpleMethod, args=(
                processBytes1, processBytes2, width * rowsPerThread * 3, d1, i)))
            processes[i].start()
        else:
            processBytes1 = bytes1[i * rowsPerThread * width * 3:sizeOfBytes]
            processBytes2 = bytes2[i * rowsPerThread * width * 3:sizeOfBytes]
            processes.append(Process(target=AsmSimpleMethod, args=(
                processBytes1, processBytes2, sizeOfBytes - (i * rowsPerThread * width * 3), d1, i)))
            processes[i].start()


def JoinProcesses(processes, numberOfThreads, d1, optionNumber):
    pixelArray = None
    for i in range(0, numberOfThreads):
        processes[i].join()
        if pixelArray is None:
            pixelArray = d1[i]
        else:
            if (optionNumber == 2):
                pixelArray += d1[i]
            else:
                pixelArray = d1[i] + pixelArray
    return pixelArray


def PrepareBytesData(height, width):
    global imageLeft
    global imageRight
    bytes1 = BytesIO()
    imageLeft.save(bytes1, 'bmp')
    bytes2 = BytesIO()
    imageRight.save(bytes2, 'bmp')
    bytes1 = bytes1.getvalue()
    bytes2 = bytes2.getvalue()
    bytes1 = bytes1[54:]
    bytes2 = bytes2[54:]
    sizeOfBytes = height * width * 3
    return bytes1, bytes2, sizeOfBytes


def SaveOutputImage(pixelArray, optionNumber, isDubois, width, height):
    if (optionNumber == 2):
        if (isDubois == True):
            CreateImage(pixelArray, 'DuboisAnaglyph.png')
            return Image.open('DuboisAnaglyph.png')
        else:
            CreateImage(pixelArray, 'DuboisSimpleAnaglyph.png')
            return Image.open('DuboisSimpleAnaglyph.png')
    else:
        if (isDubois == True):
            CreateImageFromBuffer(pixelArray, 'DuboisAnaglyphASM.png', width, height)
            return Image.open('DuboisAnaglyphASM.png')
        else:
            CreateImageFromBuffer(pixelArray, 'DuboisSimpleAnaglyphASM.png', width, height)
            return Image.open('DuboisSimpleAnaglyphASM.png')

def RenderOutputImage(image, isDubois):
    image = image.resize((150, 267))
    render = ImageTk.PhotoImage(image)
    if(isDubois == True):
        imageLabel4.configure(image=render)
        imageLabel4.photo_ref = render
    else:
        imageLabel3.configure(image=render)
        imageLabel3.photo_ref = render

def StartThreading(isDubois):

    # Prepare Data for threading
    numberOfThreads = threadSlider.get()
    width, height = imageLeft.size
    rowsPerThread = int(height / numberOfThreads)
    processes = list()
    manager = Manager()
    d1 = manager.dict()
    optionNumber = rbValue.get()

    # Start timer
    start = time.time()

    if (optionNumber == 2):
        if (isDubois == True):
            StartDuboisThreadsPy(rowsPerThread, height, width, d1, processes, numberOfThreads)
        else:
            StartCasualThreadsPy(rowsPerThread, height, width, d1, processes, numberOfThreads)
    else:
        bytes1, bytes2, sizeOfBytes = PrepareBytesData(height, width)
        if (isDubois == True):
            StartDuboisThreadsAsm(bytes1, bytes2, rowsPerThread, width, d1, processes, sizeOfBytes, numberOfThreads)
        else:
            StartCasualThreadsAsm(bytes1, bytes2, rowsPerThread, width, d1, processes, sizeOfBytes, numberOfThreads)

    pixelArray = JoinProcesses(processes, numberOfThreads, d1, optionNumber)
    # end timer
    end = time.time()
    timeElapsed = end - start
    operationTimeText.configure(text='Time of operation: ' + timeElapsed.__str__())

    image = SaveOutputImage(pixelArray, optionNumber, isDubois, width, height)
    RenderOutputImage(image, isDubois)


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
GenerateCasualB = Button(root, text='Generate Basic\n Anaglyph', command=lambda: StartThreading(False), width=16, height=5,
                         state='disabled')
GenerateDuboisB = Button(root, text='Generate Dubois\n Anaglyph', command=lambda: StartThreading(True), width=16,
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
threadSlider = Scale(root, from_=1, to=64, orient='horizontal', length=300)
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
