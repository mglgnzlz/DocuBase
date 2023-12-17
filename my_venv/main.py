from tkinter import *
 
root = Tk()
root.geometry("300x300")
root.title(" Camera Scanner ")
 
doc = Label(text = "Document name:",
            anchor = W ,
            justify= LEFT)
doctxt = Text(root, height = 2,
                width = 35,
                bg = "light yellow"
            )

date = Label(text = "Date: ")
datetxt = Text(root, height = 2,
                width = 35,
                bg = "light yellow")
 
fm = Frame(root, width=300, height=200, bg="blue")
fm.pack(side=BOTTOM, expand=NO, fill=NONE)
    
Button(fm, text="retake", width=10).pack(side=LEFT)
Button(fm, text="add", width=10).pack(side=LEFT)
Button(fm, text="finish", width=10).pack(side=LEFT)

fm.place(x= 20, y= 20)
    
 
doc.pack()
doctxt.pack()
date.pack()
datetxt.pack()
fm.pack()
 
mainloop()