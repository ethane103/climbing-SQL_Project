#######################
# Stores commands to construct the app views 
#######################
import tkinter as tk
import tkinter.ttk as ttk
from db_funcs import autoQuery as aQ
import pandas as pd

class pageManager():
    def __init__(self):
        self.pages = []

    def register(self, pg):
        self.pages.append(pg)
    
    def clear(self):
        [pg.grid_forget() for pg in self.pages]


class page(tk.Frame):
    manager = pageManager()
    autoQuery = aQ()

    def __init__(self, root, title):
        super().__init__(root, bg = "lightgrey")
        self.title = title
        #self.grid(row=0, column=0)
        self.manager.register(self)

        self.bg = "lightgrey"

    def on_show(self):
        self.manager.clear()
        self.grid(row=0, column=0, sticky="nsew")
        self.tkraise()
        

class front_page(page):
    def __init__(self, root, title):
        super().__init__(root, title)
        self.info = tk.Label(self, text = "Welcome, please pick a tab to continue!", bg=self.bg)
        self.info.pack(expand=True)
        

class wall_page(page):
    def __init__(self, root, title):
        super().__init__(root, title)

        self.infoFrame = tk.Frame(self, bg=self.bg)
        self.wallFrame = tk.Frame(self)
        self.infoFrame.pack(side=tk.TOP)
        self.wallFrame.pack(side=tk.BOTTOM)

        self.info = tk.Label(self.infoFrame, text = "You got to the wall page! Filter by holds, difficulty, gym and rating", bg=self.bg)   
        self.info.pack(expand=True, sticky = 'n')        

        self.scrollbar = tk.Scrollbar(self.wallFrame)
        self.scrollbar.pack(side = "right", fill="both")

        self.walls = []
        self.wall_list = None

        self.hold_include= []
        self.hold_exclude= []
        self.createHoldSubframe()

        

    def getWalls(self, args = {}):
        self.walls = self.autoQuery.getWalls(args = args)

    def remakeList(self, fill = True):
        if not self.wall_list is None: self.wall_list.delete()
        
        self.wall_list = ttk.Treeview(self.wallFrame)
        self.wall_list.pack(expand=True, side = "left", fill = "both")

        self.wall_list.config(yscrollcommand = self.scrollbar.set)
        self.scrollbar.config(command = self.wall_list.yview)

        if fill:
            self.wall_list["columns"] = self.walls.columns.tolist() # type: ignore
            for idx, ele in enumerate(self.wall_list["columns"]):
                self.wall_list.heading(column=idx, text=ele)

            for wall in self.walls.values: # type: ignore
                self.wall_list.insert("", 0, values=tuple(wall))

    def createHoldSubframe(self):
        self.holdsList = sum(self.autoQuery.getHolds().values.tolist(), []) # type: ignore
        self.holdSubFrame = tk.Frame(self.infoFrame, bg=self.bg)
        self.holdSubFrame.pack(side = tk.BOTTOM)
        holdGuideOn = tk.Label(self.holdSubFrame, text = "Select holds to mandate", bg=self.bg)   
        holdGuideOff = tk.Label(self.holdSubFrame, text = "Select holds to exclude", bg=self.bg)  
        holdGuideOn.grid(row=1, column=0, sticky='n')
        holdGuideOff.grid(row=2, column=0, sticky='s')
        
        for idx, hold in enumerate(self.holdsList):
            onState = tk.IntVar(value = 0) # 0 do nothing, 1 include,
            offState = tk.IntVar(value = 0) # 0 do nothing, 1 iexclude, 
            self.hold_include.append(onState)
            self.hold_exclude.append(offState)
            hold_on_cb = tk.Checkbutton(self.holdSubFrame, variable=onState)
            hold_off_cb = tk.Checkbutton(self.holdSubFrame, variable=offState)
            hold_names = tk.Label(self.holdSubFrame, text = hold, bg=self.bg)  
            hold_names.grid(row = 0, column=idx+1, sticky='n')
            hold_on_cb.grid(row = 1, column=idx+1)
            hold_off_cb.grid(row = 2, column=idx+1, sticky='s')

    def on_show(self):
        self.getWalls()
        self.remakeList()
        super().on_show()


