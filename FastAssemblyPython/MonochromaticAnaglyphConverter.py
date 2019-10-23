from tkinter import PhotoImage, filedialog, Button, Canvas, messagebox, Tk # note that module name has changed from Tkinter in Python 2 to tkinter in Python 3
from tkinter import *
import logging
import threading
import time
import PIL


global photo1
global photo2
global photo3
photo1Loaded = False
photo2Loaded = False
generator = False
global anaglyphPixelsArray

def ThreadFunction(startPointY,endPointY,pixelsWidth,pixelsArray1,pixelsArray2):
    for i in range(startPointY, endPointY + 1):
        for j in range (0,pixelsWidth):
            anaglyphPixelsArray[i][j] = (pixelsArray1[i][j][0] * 0.4561 + pixelsArray1[i][j][1] * 0.500484 + pixelsArray1[i][j][2] * 0.176381 - pixelsArray2[i][j][0] *0.0434706 - pixelsArray2[i][j][1] * 0.0879388 - pixelsArray2[i][j][2] * 0.00155529,
                               - pixelsArray1[i][j][0] * 0.0400822 - pixelsArray1[i][j][1] * 0.0378246 - pixelsArray1[i][j][2] * 0.0157589 + pixelsArray2[i][j][0] * 0.378476 + pixelsArray2[i][j][1] * 0.73364 - pixelsArray2[i][j][2] * 0.0184503,
                               - pixelsArray1[i][j][0] * 0.0152161 - pixelsArray1[i][j][1] * 0.0205971 - pixelsArray1[i][j][2] * 0.00546856 - pixelsArray2[i][j][0] * 0.0721527 - pixelsArray2[i][j][1] * 0.112961 + pixelsArray2[i][j][2] * 1.2264) 
            
def OnButtonClick(numberOfPhoto):
    filename = filedialog.askopenfilename()  
    if numberOfPhoto == 1:
        photo1 = PIL.Image.open(filename)
        render = tkinter.PhotoImage(photo1)
        canv.create_image(20,20, anchor = NW, image = render)                   
        photo1Loaded = True      
    if numberOfPhoto == 2:
        photo2 = PIL.Image.open(filename)
        render = tkinter.Pho, image = templateImageRendtoImage(photo2)
        img = tkinter.Label(top,image=render)
        img.image = render
        img.place(x=50,y=50) 
        photo2Loaded = True
        
def CheckForGeneratingValidation(gen):
    if photo1Loaded == True and photo2Loaded == True:
        gen = True
    if gen == True:
        buttonMakeAnaglyph['state'] = 'normal'

def GenerateAnaglyph(w):
    photo1Dimensions = photo1.size  
    photo2Dimensions = photo2.size
    if (photo1Dimensions[0] == photo2Dimensions[0] and 
        photo1Dimensions[1] == photo2Dimensions[1]):
        pixels1 = photo1.load()
        pixels2 = photo2.load()
        for i in range(0, scaler.get()):
            ##TODO add threads
            return
    else:
        messagebox.showinfo('Bad data','Dimensions of images don''t match')
        
        
root = tkinter.Tk()
# Window display
root.geometry("800x500")
root.title("Moncochromatic anaglyph converter")

canv = Canvas(root,width = 800,height = 500, bg = 'white')
canv.create_rectangle(50,50,230,370,fill='blue')
canv.create_rectangle(300,50,480,370,fill='blue')
buttonLoadP1 = Button(root, text = 'Load image1', command = lambda: OnButtonClick(1),width = 16, height = 5)
buttonLoadP2 = Button(root, text = 'Load image2',width = 16, height = 5,command = lambda: OnButtonClick(2))
buttonMakeAnaglyph = Button(root,text = 'Generate Anaglyph',width = 16, height = 5,state = 'disabled',command = GenerateAnaglyph)
buttonLoadP1.place(x = 75,y = 400)
buttonLoadP2.place(x = 325,y = 400)
buttonMakeAnaglyph.place(x = 575, y =400)
CheckForGeneratingValidation(generator)
scaler = Scale(root, from_=1, to=8,orient = 'horizontal',length = 300)
scaler.pack()
canv.pack()


top.mainloop()
