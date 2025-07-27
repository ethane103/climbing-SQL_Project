#######################
# Stores commands to construct the app views 
#######################
import tkinter as tk
import tkinter.ttk as ttk

# Custom Query Handling Import
from db_funcs import autoQuery as aQ

# Import int limiter
from numpy import clip


# Maintains list of pages, current user, makes sure that all other pages are hidden when a new page is shown / raised
class pageManager():
    def __init__(self):
        self.pages = []
        self.active_user = None

    def register(self, pg):
        self.pages.append(pg)
    
    def clear(self):
        [pg.grid_forget() for pg in self.pages]
        
    def setUser(self, usr):
        self.active_user = usr

    def getUser(self):
        return self.active_user

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
        

# Basic frontpage, allows user selection
class front_page(page):
    def __init__(self, root, title):
        super().__init__(root, title)
        self.infoFrame = tk.Frame(self, bg = self.bg)
        self.info = tk.Label(self.infoFrame, text = "Welcome, please pick a tab to continue!", bg=self.bg)
        self.info.pack(expand=True)
        
        self.infoFrame.pack()
        self.createUserSubframe()  # Create userr selection dropdown    

    def createUserSubframe(self):
        # Create frame
        self.userSubFrame = tk.Frame(self, bg=self.bg)
        self.userSubFrame.pack(padx=0.5, pady=0.5)
        self.manager.setUser(tk.StringVar())

        # Helptext
        self.userText = tk.Label(self.userSubFrame, text="Select User", background=self.bg)
        self.userText.pack(side='top', pady=0.1)

        # Create the user list and let it store the currently selected user
        self.users = self.autoQuery.getUsers(full=False)
        self.userdrop = tk.OptionMenu(self.userSubFrame, variable= self.manager.getUser(), value='') # type: ignore

        for user, id in zip(self.users.values, self.users.index): # type: ignore 
            self.userdrop['menu'].add_command(label = user[0], command = tk._setit(self.manager.active_user,id))
        
        self.userdrop.pack(expand=True)

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
            self.wall_list['show'] = 'headings'
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

# Shows user information and lists statewise / citywise local gyms.
class user_page(page):
    def __init__(self, root, title):
        # Create the basic window
        super().__init__(root, title)
        self.infoFrame = tk.Frame(self, bg = self.bg)
        self.infoMSG = tk.Label(self.infoFrame, text="Welcome to the User Page, here you can see your data and find local gyms!", bg = self.bg)
        self.infoMSG.pack()
        self.infoFrame.pack(side='top', pady=0.1)
        
        # Create list of gyms in state/city
        self.city_list = None
        self.state_list = None

        # Create frames for details or errors
        self.createDetailFrame()
        self.createErrFrame()
        # Subframe to DetailFrame
        self.createGymFrame()

        
    
    # When the page shows, grab the user data, and if that fails, show an error page
    def on_show(self):
        # Get the user data
        try:
            self.userInfo = aQ().getUser(self.manager.getUser().get()).iloc[0] # type: ignore  // The userInfo will have fields ['email', 'gym', 'favorite hold', 'city', 'state', 'location'] and index ['id']                                                                  
        except:
            self.userInfo = None
        
        # Present the user data in a grid, each row to a field
        if not self.userInfo is None:
            # Hide error frame and show details frame
            self.errFrame.forget()
            self.detailsFrame.pack()

            # Fill out details
            self.id.config(text = self.userInfo.name) # type: ignore
            self.email.config(text = self.userInfo['email'])
            self.loc.config(text = self.userInfo['location'])
            self.gym.config(text = self.userInfo['gym'])
            self.hld.config(text = self.userInfo['favorite hold'])  

            # Refresh the WallFrame
            self.remakeList(self.userInfo)        

        # Except on no data
        else:
            # Hide details frame and show error frame
            self.detailsFrame.forget()
            self.errFrame.pack()

        super().on_show()

    # Creates a grid of Labels for the userinfo
    def createDetailFrame(self):
        # Create Frame
        self.detailsFrame = tk.Frame(self, bg = self.bg)
        ##### ID
        t_id = tk.Label(self.detailsFrame, text = "User ID")
        t_id.grid(column=0, row=0)
        self.id = tk.Label(self.detailsFrame, text='') 
        self.id.grid(column=1,row=0)
        ##### Email
        t_email = tk.Label(self.detailsFrame, text = "Email")
        t_email.grid(column=0, row=1)
        self.email = tk.Label(self.detailsFrame, text='')
        self.email.grid(column=1,row=1)
        ##### Location
        t_loc= tk.Label(self.detailsFrame, text = "Location")
        t_loc.grid(column=0, row=2)
        self.loc = tk.Label(self.detailsFrame, text='')
        self.loc.grid(column=1,row=2)
        #### Gym
        t_gym = tk.Label(self.detailsFrame, text = "Favorite Gym")
        t_gym.grid(column=0, row=3)
        self.gym = tk.Label(self.detailsFrame, text='')
        self.gym.grid(column=1,row=3)
        #### Hold
        t_hld = tk.Label(self.detailsFrame, text = "Favorite Hold")
        t_hld.grid(column=0, row=4)
        self.hld = tk.Label(self.detailsFrame, text='')
        self.hld.grid(column=1,row=4)

    # Create a gym Frame
    def createGymFrame(self):
        self.gymFrame = tk.Frame(self.detailsFrame, background=self.bg)
        self.gymFrame.grid(column = 0, columnspan=2, row=5)

    # Regenerate gym tables
    def remakeList(self, userInfo):
        cityGyms = aQ().getGymsIn(('city', userInfo['city']))
        stateGyms =  aQ().getGymsIn(('state', userInfo['state']))

        # Empty out the list if one exists, or create a list (Treeview) otherwise
        if not self.city_list is None: 
            [self.city_list.delete(item) for item in self.city_list.get_children()]
        else:
            self.city_list = ttk.Treeview(self.gymFrame)
            self.cityLabel = ttk.Label(self.gymFrame, text="Gyms in your City")
            self.city_list['show'] = 'headings'
            self.cityLabel.grid(row = 0, column = 0)
            self.city_list.grid(row = 1, column = 0)

        if not self.state_list is None:
            [self.state_list.delete(item) for item in self.state_list.get_children()]
        else:
            self.state_list = ttk.Treeview(self.gymFrame)
            self.stateLabel = ttk.Label(self.gymFrame, text="Gyms in your State")
            self.state_list['show'] = 'headings'
            self.stateLabel.grid(row = 0, column = 1)
            self.state_list.grid(row = 1, column=1)

        # Fill the lists with the current list (pd.Dataframe) of gyms
        self.state_list["columns"] = stateGyms.columns.tolist() # type: ignore
        for idx, ele in enumerate(self.state_list["columns"]):
            self.state_list.heading(column=idx, text=ele)
        for gym in stateGyms.values: # type: ignore
            self.state_list.insert("", 0, values=tuple(gym))

        self.city_list["columns"] = cityGyms.columns.tolist() # type: ignore
        for idx, ele in enumerate(self.city_list["columns"]):
            self.city_list.heading(column=idx, text=ele)
        for gym in cityGyms.values: # type: ignore
            self.city_list.insert("", 0, values=tuple(gym))

    # Creates a simple error message to display if no user is found
    def createErrFrame(self):
        # Create Frame
        self.errFrame = tk.Frame(self, bg = self.bg)
        # Show error message
        errMsg = tk.Label(self.errFrame, text = "User data failed to load, please select a user and try again!", bg=self.bg)
        errMsg.pack()
    
        

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
        self.textdisp.pack(side='bottom')

        # Inject self into the connection system
        self.managedConnection = aQ().getMC()
        self.managedConnection.setTracker(self)

        # Create a list of previous commands, we'll let this grow forever in a session, but it's ok for this demo
        self.idx = 0
        self.stringHistory = []

        # Create a button to step forwards, and one to step back
        menu = tk.Menu(self.window)
        menu.add_command(label='<-', command = self.backstep)
        menu.add_command(label='->', command = self.forwardstep)
        self.window.config(menu=menu)

    # When the connection systems asks to track a query, replace text in window with query text.
    def track(self, str):
        self.stringHistory.append(str)
        self.textdisp.delete("1.0", tk.END)
        self.textdisp.insert("1.0", str)
        self.idx = len(self.stringHistory) - 1

    # Step backwards in tracked history
    def backstep(self):
        self.idx = clip(self.idx - 1, 0, len(self.stringHistory)-1)
        self.textdisp.delete("1.0", tk.END)
        self.textdisp.insert("1.0", self.stringHistory[self.idx])

    # Step forwards in tracked history
    def forwardstep(self):
        self.idx = clip(self.idx + 1, 0, len(self.stringHistory)-1)
        self.textdisp.delete("1.0", tk.END)
        self.textdisp.insert("1.0", self.stringHistory[self.idx])