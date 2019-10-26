from tkinter import *
from tkinter.filedialog import askopenfilename
from PIL import ImageTk, Image
import threading
import time
import numpy as np
from tkinter import messagebox

global imageLeft
global imageRight
global imageCasualAnaglyph
global imageDuboisAnaglyph
global anaglyphPixelsArray


def ThreadFunction(startPointY, endPointY, pixelsWidth, pixelsArray1, pixelsArray2):
    for i in range(0, pixelsWidth):
        for j in range(startPointY, endPointY):
            r1, g1, b1 = pixelsArray1.getpixel((i, j))
            r2, g2, b2 = pixelsArray2.getpixel((i, j))
            global anaglyphPixelsArray
            anaglyphPixelsArray[i][j] = (
                r1 * 0.4561 + g1 * 0.500484 + b1 * 0.176381 - r2 * 0.0434706 - g2 * 0.0879388 - b2 * 0.00155529,
                - r1 * 0.0400822 - g1 * 0.0378246 - b1 * 0.0157589 + r2 * 0.378476 + g2 * 0.73364 - b2 * 0.0184503,
                - r1 * 0.0152161 - g1 * 0.0205971 - b1 * 0.00546856 - r2 * 0.0721527 - g2 * 0.112961 + b2 * 1.2264)


def CreateImage():
    global anaglyphPixelsArray
    pixelsArray = np.array(anaglyphPixelsArray, dtype=np.uint8)
    newImage = Image.fromarray(pixelsArray)
    newImage.save('Anaglyph.png')


def GenerateEmptyImageMatrix(width, height):
    global anaglyphPixelsArray
    anaglyphPixelsArray = [[(0, 0, 0) for x in range(height)] for y in range(width)]


def StartDuboisThreading():
    global imageLeft
    global imageRight
    numberOfThreads = threadSlider.get()
    width, height = imageLeft.size
    GenerateEmptyImageMatrix(width, height)
    rgb_imgLeft = imageLeft.convert('RGB')
    rgb_imgRight = imageRight.convert('RGB')
    rowsPerThread = int(height / numberOfThreads)
    threads = list()

    start = time.time()
    for i in range(0, numberOfThreads):
        threads.append(threading.Thread(target=ThreadFunction, args=(
        i * rowsPerThread, (i + 1) * rowsPerThread, width, rgb_imgLeft, rgb_imgRight)))
        threads[i].start()
    for i in range(0, numberOfThreads):
        threads[i].join()
    end = time.time()
    timeElapsed = end - start
    operationTimeText.configure(text='Time of operation: ' + timeElapsed.__str__())
    CreateImage()

# def StartCasualThreading():


def OnButtonClick(numberOfPhoto):
    path = askopenfilename()
    if path:
        image = Image.open(path)
        imageR = image.resize((150, 267))
        render = ImageTk.PhotoImage(imageR)
        if numberOfPhoto == 1:
            global imageLeft
            imageLeft = image
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
        print(image1Loaded)
        print(image2Loaded)
        if image1Loaded == True and image2Loaded == True:
            GenerateCasualB.configure(state='normal')
            GenerateDuboisB.configure(state='normal')
    else:
        messagebox.showerror('Image error', 'Image was not loaded properly')


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
loadImg1B = Button(root, text='Load image1', command=lambda: OnButtonClick(1), width=16,
                   height=5)
loadImg2B = Button(root, text='Load image2', command=lambda: OnButtonClick(2), width=16,
                   height=5)
GenerateCasualB = Button(root, text='Generate Basic\n Anaglyph', command=lambda: OnButtonClick(1), width=16, height=5,
                         state='disabled')
GenerateDuboisB = Button(root, text='Generate Dubois\n Anaglyph', command=lambda: StartDuboisThreading(), width=16, height=5,
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
