from tkinter import *
from tkinter.filedialog import askopenfilename
from PIL import ImageTk, Image

def OnButtonClick(numberOfPhoto,image1Loaded,image2Loaded):
    img = Image.open(askopenfilename())
    img = img.resize((150,267))
    render = ImageTk.PhotoImage(img)
    print(image1Loaded)
    print(image2Loaded)
    if numberOfPhoto == 1:
        imageLabel1.configure(image = render)
        imageLabel1.photo_ref = render
        image1Loaded = True
    else:
        imageLabel2.configure(image = render)
        imageLabel2.photo_ref = render
        image2Loaded = True
        
    if image1Loaded == True and image2Loaded == True:
        GenerateCasualB.configure(state = 'normal')
        GenerateDuboisB.configure(state = 'normal')
    
        
image1Loaded = False
image2Loaded = False

#Generate window
root = Tk()
root.geometry("800x600")
root.title("Moncochromatic anaglyph converter")
root.resizable(width = False, height = False)

#Adjust grid weights parameters
root.columnconfigure(0,weight = 1)
root.columnconfigure(1,weight = 1)
root.columnconfigure(2,weight = 1)
root.columnconfigure(3,weight = 1)
root.rowconfigure(0,weight = 1)
root.rowconfigure(1,weight = 1)
root.rowconfigure(2,weight = 1)
root.rowconfigure(3,weight = 1)
root.rowconfigure(4,weight = 1)

#Create buttons
loadImg1B = Button(root, text = 'Load image1', command = lambda: OnButtonClick(1,image1Loaded,image2Loaded),width = 16, height = 5)
loadImg2B = Button(root, text = 'Load image2', command = lambda: OnButtonClick(2,image1Loaded,image2Loaded),width = 16, height = 5)
GenerateCasualB = Button(root, text = 'Generate Basic\n Anaglyph', command = lambda: OnButtonClick(1),width = 16, height = 5,state = 'disabled')
GenerateDuboisB = Button(root, text = 'Generate Dubois\n Anaglyph', command = lambda: OnButtonClick(1),width = 16, height = 5, state = 'disabled')
loadImg1B.grid(row = 2,column = 0, sticky = 'n')
loadImg2B.grid(row = 2,column = 1, sticky = 'n')
GenerateCasualB.grid(row = 2,column = 2, sticky = 'n')
GenerateDuboisB.grid(row = 2,column = 3, sticky = 'n')
 
#Create image labels
templateImage = Image.open('template.png')
templateImageRend = ImageTk.PhotoImage(templateImage)
imageLabel1 = Label(root, image = templateImageRend)
imageLabel2 = Label(root, image = templateImageRend)
imageLabel3 = Label(root, image = templateImageRend)
imageLabel4 = Label(root, image = templateImageRend)
imageLabel1.grid(row = 0, column = 0, sticky = 'nesw')
imageLabel2.grid(row = 0, column = 1, sticky = 'nesw')
imageLabel3.grid(row = 0, column = 2, sticky = 'nesw')
imageLabel4.grid(row = 0, column = 3, sticky = 'nesw')



#Create text for thread
threadText = Label(root, text='Choose number of threads')
threadText.grid(row = 3, column=0, columnspan=2, sticky='s')

#Create threadSlider
threadSlider = Scale(root, from_=1, to=8,orient = 'horizontal',length = 300)
threadSlider.grid(row = 4,column=0,columnspan=2, sticky='n')

#Add frame for radio buttons
optionFrame = LabelFrame(root, text='Function Details')
optionFrame.grid(row = 3, column = 0, columnspan = 2, sticky = 'n')

#Radio buttons
rbValue = IntVar()
rbValue.set(2)
assemblyRadio = Radiobutton(optionFrame, text = "Assembly",value = 1, variable = rbValue)
pythonRadio = Radiobutton(optionFrame, text = "Python",value = 2, variable = rbValue)
assemblyRadio.grid(row=0,column=0,sticky = 'w')
pythonRadio.grid(row=1,column=0, sticky = 'w')
#img = Image.open(askopenfilename())
#img = img.resize((224,400))
#render = ImageTk.PhotoImage(img)
#canvas = Canvas(root)

#canvas.create_image(112,200,image = render)
#canvas.pack(side = LEFT, expand =True,fill=BOTH)
root.mainloop()