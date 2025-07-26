#######################
# Stores commands to construct the app views 
#######################
import tkinter as tk
import tkinter.ttk as ttk

# Custom Query Handling Import
from db_funcs import autoQuery as aQ


# Maintains list of pages, makes sure that all other pages are hidden when a new page is shown / raised
class pageManager():
    def __init__(self):
        self.pages = []

    def register(self, pg):
        self.pages.append(pg)
    
    def clear(self):
        [pg.grid_forget() for pg in self.pages]


# Superclass for pages, provides default behaivour to append pages to pageManager, hook to the autoQuery system and raising
# also sets the default background color.
class page(tk.Frame):
    manager = pageManager()
    autoQuery = aQ()

    def __init__(self, root, title):
        super().__init__(root, bg = "lightgrey")
        self.title = title
        self.manager.register(self)

        self.bg = "lightgrey"

    def on_show(self):
        self.manager.clear()
        self.grid(row=0, column=0, sticky="nsew")
        self.tkraise()
        

# Basic frontpage
class front_page(page):
    def __init__(self, root, title):
        super().__init__(root, title)
        self.info = tk.Label(self, text = "Welcome, please pick a tab to continue!", bg=self.bg)
        self.info.pack(expand=True)
        

# Presents list of wall, and allows filtering
class wall_page(page):
    # Initialize and generate subframes for showing the walls, filtering by holds, etc.
    def __init__(self, root, title):
        super().__init__(root, title)

        # Create the two most central frames, showing what the page is and creating the wall frame w/ scrollbar
        self.infoFrame = tk.Frame(self, bg=self.bg)
        self.infoFrame.pack(side=tk.TOP)

        self.info = tk.Label(self.infoFrame, text = "You got to the wall page! Filter by holds, difficulty, gym and rating", bg=self.bg)   
        self.info.pack(expand=True, side = 'top')    

        self.wallFrame = tk.Frame(self)
        self.wallFrame.pack(side=tk.BOTTOM)
        self.scrollbar = tk.Scrollbar(self.wallFrame)
        self.scrollbar.pack(side = "right", fill="both")
        
        # Internal list for storing walls
        self.walls = []
        self.wall_list = None

        # Create the three filtering subframes, and a button to refresh the list
        self.holdStates= []
        self.createHoldSubframe()

        self.diffStates = []
        self.createDiffSubframe()

        self.gym_id = None
        self.createGymSubframe()

        self.filterButton = tk.Button(self, text="Apply Filter", command = self.remakeList)
        self.filterButton.pack()

    # Pass query to autoQuery and store results in walls        
    def getWalls(self, args = {}):
        self.walls = self.autoQuery.getWalls(args = args)

    # Regenerate wall table based on filter args
    def remakeList(self, fill = True):
        args = self.generateArgs()
        self.getWalls(args)

        # Empty out the list if one exists, or create a list (Treeview) otherwise
        if not self.wall_list is None: 
            [self.wall_list.delete(item) for item in self.wall_list.get_children()]
        else:
            self.wall_list = ttk.Treeview(self.wallFrame)
            self.wall_list.pack(expand=True, side = "left", fill = "both")
            self.wall_list.config(yscrollcommand = self.scrollbar.set)
            self.scrollbar.config(command = self.wall_list.yview)

        # Fill the list with the current list (pd.Dataframe) of walls
        if fill:
            self.wall_list["columns"] = self.walls.columns.tolist() # type: ignore
            for idx, ele in enumerate(self.wall_list["columns"]):
                self.wall_list.heading(column=idx, text=ele)

            for wall in self.walls.values: # type: ignore
                self.wall_list.insert("", 0, values=tuple(wall))

    # Create a Hold filtering subframe with a triplet (neutral, on, off) of radio buttonsf for each hold
    def createHoldSubframe(self):
        # Get Holds
        self.holdsList = sum(self.autoQuery.getHolds().values.tolist(), []) # type: ignore

        # Create the subframe
        self.holdSubFrame = tk.Frame(self.infoFrame, bg=self.bg, padx = 0.5, pady=0.5)
        self.holdSubFrame.pack()

        # Add Labels and place them to the left of a grid
        holdGuideFree = tk.Label(self.holdSubFrame, text = "Free Holds", bg=self.bg)  
        holdGuideOn = tk.Label(self.holdSubFrame, text = "Select holds to mandate", bg=self.bg)   
        holdGuideOff = tk.Label(self.holdSubFrame, text = "Select holds to exclude", bg=self.bg)  
        holdGuideFree.grid(row=1, column=0, sticky='n')
        holdGuideOn.grid(row=2, column=0)   
        holdGuideOff.grid(row=3, column=0, sticky='s')
        
        # Loop over holds, creating buttons and filling the grid
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

    # Difficulty Checkboxes
    def createDiffSubframe(self):
        self.diffSubFrame = tk.Frame(self.infoFrame, bg=self.bg)
        self.diffSubFrame.pack(side = tk.BOTTOM, padx = 0.5, pady=0.5)

        # Generate the list of possible difficulties
        self.diffs = ['V' + a for a in ['B'] + [str(num) for num in range(0,13)]]

        # Label
        diffGuide = tk.Label(self.diffSubFrame, text = "Pick your difficulties", bg=self.bg)   
        diffGuide.grid(row = 0, column=0, columnspan=len(self.diffs),sticky='n')

        # Fill 
        for idx, diff in enumerate(self.diffs):
            diffState = tk.IntVar(value = 0) # 0 include, 1 exclude
            self.diffStates.append(diffState)
            diffCB = ttk.Checkbutton(self.diffSubFrame, variable=diffState, offvalue = 0, onvalue='1', text=diff)
            diffCB.grid(row = 1, column=idx, sticky='s')           

    # Create a dropdown list of gyms for filtering
    def createGymSubframe(self):
        # Create frame
        self.gymSubframe = tk.Frame(self.infoFrame, bg = self.bg)
        self.gymSubframe.pack(padx=0.5, pady=0.5)

        # Create list of gyms and associated id in SQL list
        self.gyms = self.autoQuery.getGyms()
        self.gym_id = tk.StringVar(value = None)

        # Helptext
        self.gymText = tk.Label(self.gymSubframe, text="Select which Gym to Filter By")
        self.gymText.pack(side='top', pady=0.1)

        # Create the gym list and let it store the currently selected gym
        self.gymdrop = tk.OptionMenu(self.gymSubframe, variable= self.gym_id, value='')

        for gym, id in zip(self.gyms.values, self.gyms.index): # type: ignore 
            self.gymdrop['menu'].add_command(label = gym[0], command = tk._setit(self.gym_id,id))
        
        #self.gymdrop['menu'].add_command(label = 'No Selection', command = tk._setit(self.gym_id,''))
        self.gymdrop.pack()
            
    # Builds the filter dictionary to pass to the autoQuery(), converts both lists of buttons (state and difficulty) into dict entries, and passes the selected gym_id as a dict entry
    def generateArgs(self):
        args = {}
        holdCons = {}
        diffCons = []

        # Creates a dict linking holds to HAS / !HAS based on the hold buttons
        for idx, hold in enumerate(self.holdsList):
            match self.holdStates[idx].get():
                case 0:
                    pass
                case 1:
                    holdCons[hold] = 'HAS'
                case -1:
                    holdCons[hold] = '!HAS'

        args['holdCons'] = holdCons

        # Creates a list of acceptable difficulties, and appends if it's not empty
        for idx, diff in enumerate(self.diffs):
            match self.diffStates[idx].get():
                case 0:
                    pass
                case 1:
                    diffCons.append(diff)
        
        if diffCons:
            args['difficulties'] = diffCons
        
        # Creates a 'list', (only ever one element in current implementation), of accetable gyms based on dropdown
        if not len(self.gym_id.get()) == 0: # type: ignore
            args['gym_id'] = self.gym_id.get() # type: ignore
        
        # Return generated dictionary of dicts/lists.
        return args

    # Custom on_show override to force the list to always be up to date and filled when you open the page
    def on_show(self):
        self.getWalls()
        self.remakeList()
        super().on_show()


# Debug window showing the latest passed SQL query
class sql_viewer():
    def __init__(self, root):
        # Create window and set up text display
        self.root = root
        self.window = tk.Toplevel(root)
        self.window.title("SQL Command Display")
        self.window.geometry("800x800")

        self.text = tk.StringVar()
        self.text.set("No Commands Sent")

        self.textdisp = tk.Text(self.window, font='Consolas', wrap="word", height=72)
        self.textdisp.pack()

        # Inject self into the connection system
        self.managedConnection = aQ().getMC()
        self.managedConnection.setTracker(self)

    # When the connection systems asks to track a query, replace text in window with query text.
    def track(self, str):
        self.textdisp.delete("1.0", tk.END)
        self.textdisp.insert("1.0", str)