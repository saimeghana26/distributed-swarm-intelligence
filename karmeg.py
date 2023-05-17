import random
import numpy as np
import _thread
import panel as pn
pn.extension(template='bootstrap',theme='dark')
import holoviews as hv
import time
import pandas as pd
from holoviews.streams import Stream
import ray
hv.extension('bokeh', logo=False)  


# Ray initialized
if not ray.is_initialized():
    ray.init(_node_ip_address='', _redis_password='')       

# Particle class : Each particle will be an object of this class with all the properties defined in __init__() method
class Particle(): 
    
    # Method to initialize particle properties
	def __init__(self,initial):
		self.position=[]
		self.velocity=[]
		self.initial = initial 
		self.best_position=[] 
		self.best_error=-1 
		self.error=-1    
		self.num_dimensions = 2
		for i in range(0,self.num_dimensions): 
			self.velocity.append(random.uniform(-1,1))
			self.position.append(initial[i])
	
    # Method to update velocity of a particle object
	def update_velocity(self,global_best_position): 
		w = 0.5
		c1 = 1 
		c2 = 2 
		
		for i in range(0,self.num_dimensions): 
			r1=random.random()
			r2=random.random()
			
			cog_vel=c1*r1*(self.best_position[i]-self.position[i])
			social_vel=c2*r2*(global_best_position[i]-self.position[i])
			self.velocity[i]=w*self.velocity[i]+cog_vel+social_vel 
		
    # Method to update position of a particle object    
	def update_position(self,bounds): 
		for i in range(0,self.num_dimensions):
			self.position[i]=self.position[i]+self.velocity[i]			
			
			if self.position[i]>bounds[i][1]:
				self.position[i]=bounds[i][1]
				
			if self.position[i] < bounds[i][0]:
				self.position[i]=bounds[i][0]	
	
    # Method to evaluate fitness of a particle
	def evaluate_fitness(self,number,target,function):
		if number==1 :
			self.error=ray.get(fitness_function.remote(self.position,target))
		else:
			self.error=ray.get(cost_function.remote(self.position,function))
        
		if self.error < self.best_error or self.best_error==-1:
			self.best_position=self.position 
			self.best_error=self.error

    # Getter method to return the present error of a particle
	def get_error(self):
		return self.error
    
    # Getter method to return the best position of a particle
	def get_best_pos(self):
		return self.best_position
    
    # Getter method to return the best error of a particle
	def get_best_error(self):
		return self.best_error
    
    # Getter method to return the best position of a particle
	def get_pos(self):
		return self.position
    
    # Getter method to return the velocity of a particle
	def get_velocity(self):
		return self.velocity
        
    
# Function to calculate the euclidean distance from a particle to target
@ray.remote(num_cpus=2) # You can define the number of cpus that you want the task to run on
def fitness_function(particle_position,target):
	x_pos,y_pos = float(target[0]),float(target[1])
	return (x_pos-particle_position[0])**2 +(y_pos-particle_position[1])**2

# Function to calculate the value of the mathematical function at the position of a particle
@ray.remote(num_cpus=2) # You can define the number of cpus that you want the task to run on
def cost_function(particle_position,function):
    if(function == 'x^2+(y-100)^2'):
        return (particle_position[0]**2 + (particle_position[1]-100)**2)
    elif(function == '(x-234)^2+(y+100)^2'):
        return ((particle_position[0]-234)**2 + (particle_position[1]+100)**2)
    else:
        return 0

 
# Interactive Class : to create a swarm of particles and an interative pso
class Interactive_PSO():
    
    # Method to initialize properties of an Interactive PSO
    def __init__(self):
        self._running = False
        self.num_particles = 25
        self.initial = [5,5]
        self.bounds = [(-500,500),(-500,500)]
        self.x_axis=[]
        self.y_axis=[]      
        self.target=[5]*2
        self.global_best_error = -1
        self.update_particles_position_lists_with_random_values()
        self.global_best_position=[0,0]
        
        
    # Method to initialize swarm of particles and find an optimal solution to a problem    
    def swarm_initilization(self,number):
        swarm=[]
        global update_table
        self.global_best_position=[0,0]
        self.global_best_error = -1
        self.gamma = 0.0001
        function = function_select.value

        for i in range(0,self.num_particles): # For loop to intilize the swarm of particles
                swarm.append(Particle([self.x_axis[i],self.y_axis[i]]))
            
        i=0
        while self._running == True: # Loop to identify the best solution depending upon the problem
            if 0.0 <= self.global_best_error <= 0.00001:
                self.global_best_error = 0
                break
        
            for j in range(0,self.num_particles):
                swarm[j].evaluate_fitness(number,self.target,function)                
        				
                if swarm[j].get_error() < self.global_best_error or self.global_best_error == -1:
        		        self.global_best_position=list(swarm[j].get_pos())
        		        self.global_best_error=float(swarm[j].get_error())
        					
                if i%2==0:	
        		        self.global_best_error=-1
        		        self.global_best_position = list([swarm[j].get_pos()[0]+self.gamma*(swarm[j].get_error())*random.random() ,swarm[j].get_pos()[-1]+self.gamma*(swarm[j].get_error())*random.random()])
        		        
            for j in range(0,self.num_particles): 
        		        swarm[j].update_velocity(self.global_best_position)
        		        swarm[j].update_position(self.bounds)
        		        self.x_axis[j]=(swarm[j].get_pos()[0]);
        		        self.y_axis[j]=(swarm[j].get_pos()[-1]);
        		        
            i=i+1
        if(number==2):
            update_table = True
        self.initial = self.global_best_position
        self._running=False
        print ('Best Position:',self.global_best_position)
        print( 'Best Error:',self.global_best_error)
        
      
    # Method to terminate finding the solution of a problem
    def terminate(self):
        self._running = False
        
    # Method to set _running parameter before initializing the swarm
    def starting(self):
        self._running = True
        
    # Method to check if the swarm of particles are in action
    def isrunning(self):
        return self._running 
    
    # Getter method to return the number of particles
    def get_num_particles(self):
        return self.num_particles;
    
    # Setter method to update the number of particles
    def update_num_particles(self,newValue):
        self.num_particles = newValue
    
    # Getter method to return the x_axis position list for particles in a swarm
    def get_xaxis(self):
        return self.x_axis
    
    # Getter method to return the y_axis position list for particles in a swarm
    def get_yaxis(self):
        return self.y_axis
    
    # Setter method to update the target position
    def set_target(self,x,y):
        self.target = [x,y]
       
    # Getter method to return the target position
    def get_target(self):
        return self.target
           
    # Method to update the length of particles position lists if there is a change in num of particles
    def update_particles_position_lists(self,updated_num_particles):
        old_x_value = self.x_axis[0]
        old_y_value = self.y_axis[0]        
        if(updated_num_particles > self.num_particles):
            for i in range(self.num_particles, updated_num_particles):
                self.x_axis.append(old_x_value)
                self.y_axis.append(old_y_value)
        else:
            for i in range((self.num_particles)-1, updated_num_particles-1, -1):
                self.x_axis.pop(i)
                self.y_axis.pop(i)
     
    # Method to initialize the particles positions randomly
    def update_particles_position_lists_with_random_values(self):
        self.x_axis = random.sample(range(-500, 500), self.num_particles)
        self.y_axis = random.sample(range(-500, 500), self.num_particles)
                


pso_swarm = Interactive_PSO() # Creating an interactive pso to find the target
pso_computation_swarm = Interactive_PSO() # Creating an interactive pso to find the optimal solution of a mathematical function
         
update_table = False

# Method to initialize swarm to find the target in a given search space
def start_finding_the_target():
    pso_swarm.swarm_initilization(1)
    
# Method to initialize swarm to computate an optimal solution for a given problem
def start_computation():
    pso_computation_swarm.swarm_initilization(2)

# On event function for single tap to create and return the target with updated position
def create_target_element(x,y):
    pso_swarm.terminate()
    if x is not None:
        pso_swarm.set_target(x,y)
    return hv.Points((x,y,1), label='Target').opts(color='w', marker='^', size=10)


# Function to stream the particles of pso_swarm to dynamic map in regular intervals
def update():        
    x_axis = (pso_swarm.get_xaxis())
    y_axis = (pso_swarm.get_yaxis())
    data = (x_axis,y_axis, np.random.random(size= len(x_axis)))
    pop_scatter = hv.Scatter(data ,vdims = [ 'y_axis', 'z'] )    
    pop_scatter.opts(size = 8,color = 'z', cmap = 'Coolwarm_r')
    return pop_scatter

# On event function for update button click to udpate the number of particles in both the swarms
def computational_update():    
    x_axis = (pso_computation_swarm.get_xaxis())
    y_axis = (pso_computation_swarm.get_yaxis())
    data = (x_axis,y_axis, np.random.random(size= len(x_axis)))
    pop_scatter1 = hv.Scatter(data ,vdims = ['y_axis','z'])  
    pop_scatter1.opts(size = 8,color = 'z', cmap = 'Coolwarm_r')
    return pop_scatter1



# On event function for update button click to udpate the number of particles in both the swarms
def update_num_particles_event(event):
    if(population_slider.value == (pso_swarm.get_num_particles())):
        return;
    pso_swarm.terminate()
    pso_computation_swarm.terminate()
    time.sleep(1)
    updated_num_particles = population_slider.value
    pso_swarm.update_particles_position_lists(updated_num_particles)
    pso_swarm.update_num_particles(updated_num_particles)    
    pso_computation_swarm.update_num_particles(updated_num_particles)
    pso_computation_swarm.update_particles_position_lists_with_random_values()
    hv.streams.Stream.trigger(pso_scatter1.streams)
    hv.streams.Stream.trigger(pso_scatter.streams)

# Periodic Callback function for every 3 seconds to stream the data to dynamic maps
def trigger_streams():
    global update_table
    hv.streams.Stream.trigger(pso_scatter.streams)
    hv.streams.Stream.trigger(pso_scatter1.streams)
    if update_table : 
        update_table = False
        hv.streams.Stream.trigger(table_dmap.streams)

# On event function for begin the hunting button click to start hunting for the target
def hunting_button_event(event):
    if not pso_swarm.isrunning():
        pso_swarm.starting()
        _thread.start_new_thread(start_finding_the_target,())

# On event function for start the computation button click to start computation for a mathematical function 
def computation_button_event(event):
    if not pso_computation_swarm.isrunning():
        pso_computation_swarm.starting()
        _thread.start_new_thread(start_computation,())
        

# Function to return the data of particles positions to dynamic map in regular intervals                
def table():
    position = pso_computation_swarm.global_best_position

    df = pd.DataFrame({
        'x_position' : [round(position[0])],
        'y_position': [round(position[1])]        
        })

    hv_table = hv.Table(df).opts(width=300, height=100)
    return hv_table
    
# Function to update the mathematical function for which swarm finds the optimal solution
def update_function(event):
    pso_computation_swarm.terminate()
    time.sleep(1)
    pso_computation_swarm.update_particles_position_lists_with_random_values()


# Two dynamic maps for two interactive pso, one for finding a target and one for computation of mathematical function
pso_scatter = hv.DynamicMap(update, streams=[Stream.define('Next')()]).opts(xlim=(-500,500), ylim=(-500,500), title="Plot 2 : PSO for target finding ")
pso_scatter1 = hv.DynamicMap(computational_update, streams=[Stream.define('Next')()]).opts(xlim=(-500,500), ylim=(-500,500),title="Plot 1 : PSO for a mathematical computation")

# Dynamic map to update and display target
tap = hv.streams.SingleTap(x=pso_swarm.get_target()[0], y=pso_swarm.get_target()[1])
target_dmap = hv.DynamicMap(create_target_element, streams=[tap])

# Dynamic map to update the table with continuous global best position of the swarm
table_dmap = hv.DynamicMap(table,streams=[Stream.define('Next')()])
table_label = pn.pane.Markdown("Once an optimal solution is found in plot 1 it is updated in the below table")

# Button to order the swarm of particles to start finding the target
start_hunting_button = pn.widgets.Button(name=' Click to find target for plot 2 ', width=50)
start_hunting_button.on_click(hunting_button_event)

# Button to order the swarm of particles to start computation for selected mathematical function
start_finding_button = pn.widgets.Button(name=' Click to start computation for plot 1', width=50)
start_finding_button.on_click(computation_button_event)

# Button to update number of particles 
update_num_particles_button = pn.widgets.Button(name='Update number of particles', width=50)
update_num_particles_button.on_click(update_num_particles_event)

# periodic callback for every three seconds to trigger streams method
pn.state.add_periodic_callback(trigger_streams, 3)

# Slider to change the number of particles
population_slider = pn.widgets.IntSlider(name='Number of praticles', start=10, end=100, value=25)

# Dropdown list to select a mathematical function
function_select = pn.widgets.Select(name='Select', options=['x^2+(y-100)^2','(x-234)^2+(y+100)^2'])
function_select.param.watch(update_function,'value')

#combining the dynamic maps with particles and target into one dynamicmap
plot_for_finding_the_target = pso_scatter*target_dmap    
    
# Building the layout and returning the dashboard     
dashboard =  pn.Column(pn.Row(pn.Row(pso_scatter1.opts(width=500, height=500)), pn.Column(plot_for_finding_the_target.opts(width=500, height=500)),
                             pn.Column(pn.Column(table_label,table_dmap), start_finding_button, start_hunting_button, update_num_particles_button, population_slider,function_select)))

#Bokeh server launch of dashboard
pn.panel(dashboard).servable(title='Swarm Particles Visualization')



