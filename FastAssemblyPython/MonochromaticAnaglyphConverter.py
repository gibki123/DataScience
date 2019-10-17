from tkinter import PhotoImage # note that module name has changed from Tkinter in Python 2 to tkinter in Python 3
from tkinter import filedialog
from tkinter import Button
from tkinter import Canvas
from tkinter import messagebox


global photo1
global photo2
global photo3
photo1Loaded = False
photo2Loaded = False
generator = False


def OnButtonClick(numberOfPhoto):
    filename = filedialog.askopenfilename()  
    if numberOfPhoto == 1:
        photo1 = PhotoImage(file=filename)
        photo1Loaded = True
    if numberOfPhoto == 2:
        photo2 = PhotoImage(file=filename)
        photo2Loaded = True
        
def CheckForGeneratingValidation(gen):
    if photo1Loaded == True and photo2Loaded == True:
        gen = True
    if gen == True:
        buttonMakeAnaglyph['state'] = 'normal'

def GenerateAnaglyph(w):
    photo1Dimensions = (photo1Loaded.width(),photo1Loaded.height())
    photo2Dimensions = (photo2Loaded.width(),photo2Loaded.height())
    if (photo1Dimensions[0] == photo2Dimensions[0] and 
        photo1Dimensions[1] == photo2Dimensions[1]):
        return
        
    else:
        messagebox.showinfo('Bad data','Dimensions of images don''t match')
        
        
top = tkinter.Tk()
top.geometry("800x500")
top.resizable(width=False,height=False)
canv = Canvas(top,width = 800,height = 500, bg = 'white')
canv.create_rectangle(50,50,230,370,fill='blue')
canv.create_rectangle(300,50,480,370,fill='white')
buttonLoadP1 = Button(top, text = 'Load image1', command = lambda: OnButtonClick(1),width = 16, height = 5)
buttonLoadP2 = Button(top, text = 'Load image2',width = 16, height = 5,command = lambda: OnButtonClick(2))
buttonMakeAnaglyph = Button(top,text = 'Generate Anaglyph',width = 16, height = 5,state = 'disabled',command = GenerateAnaglyph)
buttonLoadP1.place(x = 75,y = 400)
buttonLoadP2.place(x = 325,y = 400)
buttonMakeAnaglyph.place(x = 575, y =400)
CheckForGeneratingValidation(generator)
w = Scale(top, from_=0, to=100,orient = 'horizontal',length = 300)
w.pack()

canv.pack()


top.mainloop()
