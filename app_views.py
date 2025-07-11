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
        self.info.pack(expand=True, side = 'top')        

        self.scrollbar = tk.Scrollbar(self.wallFrame)
        self.scrollbar.pack(side = "right", fill="both")

        self.walls = []
        self.wall_list = None

        self.holdStates= []
        self.createHoldSubframe()

        self.filterButton = tk.Button(self, text="Apply Filter", command = self.remakeList)
        self.filterButton.pack()

        self.diffStates = []
        self.createDiffSubframe()

        self.gym_id = None
        self.createGymSubframe()
        

    def getWalls(self, args = {}):
        self.walls = self.autoQuery.getWalls(args = args)

    def remakeList(self, fill = True):
        args = self.generateArgs()
        self.getWalls(args)

        if not self.wall_list is None: 
            [self.wall_list.delete(item) for item in self.wall_list.get_children()]
        else:
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
        self.holdSubFrame = tk.Frame(self.infoFrame, bg=self.bg, padx = 0.5, pady=0.5)
        self.holdSubFrame.pack()
        holdGuideFree = tk.Label(self.holdSubFrame, text = "Free Holds", bg=self.bg)  
        holdGuideOn = tk.Label(self.holdSubFrame, text = "Select holds to mandate", bg=self.bg)   
        holdGuideOff = tk.Label(self.holdSubFrame, text = "Select holds to exclude", bg=self.bg)  
        holdGuideFree.grid(row=1, column=0, sticky='n')
        holdGuideOn.grid(row=2, column=0)   
        holdGuideOff.grid(row=3, column=0, sticky='s')
        
        for idx, hold in enumerate(self.holdsList):
            holdState = tk.IntVar(value = 0) # -1 exclude, 0 do nothing, 1 include,
            self.holdStates.append(holdState)
            hold_free_cb = ttk.Radiobutton(self.holdSubFrame, variable=holdState, value = 0)
            hold_on_cb = ttk.Radiobutton(self.holdSubFrame, variable=holdState, value=  1)
            hold_off_cb = ttk.Radiobutton(self.holdSubFrame, variable=holdState, value = -1)
            hold_names = tk.Label(self.holdSubFrame, text = hold, bg=self.bg)  
            hold_names.grid(row = 0, column=idx+1, sticky='n')
            hold_free_cb.grid(row = 1, column=idx+1)
            hold_on_cb.grid(row = 2, column=idx+1)
            hold_off_cb.grid(row = 3, column=idx+1, sticky='s')

    def createDiffSubframe(self):
        self.diffSubFrame = tk.Frame(self.infoFrame, bg=self.bg)
        self.diffSubFrame.pack(side = tk.BOTTOM, padx = 0.5, pady=0.5)

        self.diffs = ['V' + a for a in ['B'] + [str(num) for num in range(0,13)]]

        diffGuide = tk.Label(self.diffSubFrame, text = "Pick your difficulties", bg=self.bg)   
        diffGuide.grid(row = 0, column=0, columnspan=len(self.diffs),sticky='n')

        for idx, diff in enumerate(self.diffs):
            diffState = tk.IntVar(value = 0) # -1 exclude, 0 do nothing, 1 include,
            self.diffStates.append(diffState)
            diffCB = ttk.Checkbutton(self.diffSubFrame, variable=diffState, offvalue = 0, onvalue='1', text=diff)
            diffCB.grid(row = 1, column=idx, sticky='s')           

    def createGymSubframe(self):
        self.gymSubframe = tk.Frame(self.infoFrame, bg = self.bg)
        self.gymSubframe.pack(padx=0.5, pady=0.5)

        self.gyms = self.autoQuery.getGyms()
        self.gym_id = tk.StringVar(value = None)
        self.gymText = tk.Label(self.gymSubframe, text="Select which Gym to Filter By")
        self.gymText.pack(side='top', pady=0.1)
        self.gymdrop = tk.OptionMenu(self.gymSubframe, variable= self.gym_id, value='')

        for gym, id in zip(self.gyms.values, self.gyms.index):
            self.gymdrop['menu'].add_command(label = gym[0], command = tk._setit(self.gym_id,id))
        
        #self.gymdrop['menu'].add_command(label = 'No Selection', command = tk._setit(self.gym_id,''))
        self.gymdrop.pack()
            

    def generateArgs(self):
        args = {}
        holdCons = {}
        diffCons = []

        for idx, hold in enumerate(self.holdsList):
            match self.holdStates[idx].get():
                case 0:
                    pass
                case 1:
                    holdCons[hold] = 'HAS'
                case -1:
                    holdCons[hold] = '!HAS'

        args['holdCons'] = holdCons

        for idx, diff in enumerate(self.diffs):
            match self.diffStates[idx].get():
                case 0:
                    pass
                case 1:
                    diffCons.append(diff)
        
        if diffCons:
            args['difficulties'] = diffCons
        
        if not len(self.gym_id.get()) == 0:
            args['gym_id'] = self.gym_id.get()
        
        return args


    def on_show(self):
        self.getWalls()
        self.remakeList()
        super().on_show()


