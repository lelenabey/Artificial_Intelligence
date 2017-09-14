#Look for #IMPLEMENT tags in this file. These tags indicate what has
#to be implemented to complete the bicycle domain.

#999890097 Lelen Abeywardena g3abewyb

NAME = 0
PICKUP = 1
TIME = 2
DROPOFF = 3
WEIGHT = 4
PAY = 5
'''
bicycle STATESPACE 
'''
#   You may add only standard python imports---i.e., ones that are automatically
#   available on CDF.
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files

from search import *
from random import randint
from math import sqrt

class bicycle(StateSpace):
    def __init__(self, action, gval, current_jobs, location, time, money, weight, unstarted_jobs, map, parent=None):
        #IMPLEMENT
        '''Initialize a bicycle search state object.'''
        if action == 'START':   #NOTE action = 'START' is treated as starting the search space
            StateSpace.n = 0
        StateSpace.__init__(self, action, gval, parent)
        #implement the rest of this function.
        self.current_jobs = current_jobs
        self.location = location
        self.time = time
        self.money = money
        self.weight = weight
        self.unstarted_jobs = unstarted_jobs
        self.map = map

    def successors(self):
        #IMPLEMENT
        '''Return list of bicycle objects that are the successors of the current object'''
    
        
        States = []
        if self.location =='home':
            for job in self.unstarted_jobs:
                index = self.unstarted_jobs.index(job)
                States.append(bicycle("first_pickup({})".format(job[NAME]), self.gval, [job], job[PICKUP], job[TIME], 0, job[WEIGHT],
                                      self.unstarted_jobs[:index]+self.unstarted_jobs[index+1:], self.map, self))
                              
            return States
    
        dropoff_locs=[]    
        for job in self.current_jobs:
            dropoff_locs.append(job[DROPOFF])
            dropoff_time = self.time+dist(self.location, job[DROPOFF], self.map)
            if dropoff_time <= 1140:
                for payment in job[PAY]:
                    if payment[0] >= dropoff_time:
                        money = payment[1]
                        break
                    else:
                        money = 0
                cost = job[PAY][0][1] - money
                #print ("cost: {}, max: {}, money: {}, job: {}".format(cost, job[PAY][0][1], money, job[0]))
                index = self.current_jobs.index(job)
                States.append(bicycle("deliver({})".format(job[NAME]), self.gval+cost, self.current_jobs[:index]+self.current_jobs[index+1:],
                                      job[DROPOFF], dropoff_time, self.money+money, self.weight-job[WEIGHT], self.unstarted_jobs, self.map, self))

        for job in self.unstarted_jobs:
            pickup_time = self.time+dist(self.location, job[PICKUP], self.map)
            if job[WEIGHT]+self.weight <=10000 and job[PICKUP] not in dropoff_locs and pickup_time <= 1140:
                index = self.unstarted_jobs.index(job)
                if job[TIME] <= pickup_time:
                    States.append(bicycle("pickup({})".format(job[NAME]), self.gval, self.current_jobs+[job],
                                      job[PICKUP], pickup_time, self.money, self.weight+job[WEIGHT], self.unstarted_jobs[:index]+self.unstarted_jobs[index+1:],
                                      self.map, self))
                else:
                    States.append(bicycle("pickup({})".format(job[NAME]), self.gval, self.current_jobs+[job],
                                      job[PICKUP], job[TIME], self.money, self.weight+job[WEIGHT], self.unstarted_jobs[:index]+self.unstarted_jobs[index+1:],
                                      self.map, self))
                
        return States

    def hashable_state(self) :
#IMPLEMENT
        '''Return a data item that can be used as a dictionary key to UNIQUELY represent the state.'''
        return (tuple(self.get_carrying()), tuple(self.get_unstarted()), self.location, self.money)
        
    def print_state(self):
        #DO NOT CHANGE THIS FUNCTION---it will be used in auto marking
        #and in generating sample trace output. 
        #Note that if you implement the "get" routines below properly, 
        #This function should work irrespective of how you represent
        #your state. 

        if self.parent:
            print("Action= \"{}\", S{}, g-value = {}, (From S{})".format(self.action, self.index, self.gval, self.parent.index))
        else:
            print("Action= \"{}\", S{}, g-value = {}, (Initial State)".format(self.action, self.index, self.gval))
            
        print("    Carrying: {} (load {} grams)".format(
                      self.get_carrying(), self.get_load()))
        print("    State time = {} loc = {} earned so far = {}".format(
                      self.get_time(), self.get_loc(), self.get_earned()))
        print("    Unstarted Jobs.{}".format(self.get_unstarted()))

    def get_loc(self):
#IMPLEMENT-ED
        '''Return location of courier in this state'''
        return self.location

    def get_carrying(self):
#IMPLEMENT-ED
        '''Return list of NAMES of jobs being carried in this state'''
        return [job[0] for job in self.current_jobs]

    
    def get_load(self):
#IMPLEMENT-ED
        '''Return total weight being carried in this state'''
        weight =0 
        for job in self.current_jobs:
            weight+= job[4]
        return weight

    def get_time(self):
#IMPLEMENT-ED
        '''Return current time in this state'''
        return self.time

    def get_earned(self):
#IMPLEMENT-ED
        '''Return amount earned so far in this state'''
        return self.money

    def get_unstarted(self):
#IMPLEMENT-ED
        '''Return list of NAMES of jobs not yet stated in this state'''
        return [job[0] for job in self.unstarted_jobs]
    
def heur_null(state):
    '''Null Heuristic use to make A* search perform uniform cost search'''
    return 0



def deliver_loss(state):
    losses = []
    for job in state.current_jobs:
        dropoff_time = state.time + dist(state.location, job[DROPOFF], state.map)
        for payment in job[PAY]:
            if payment[0] >= dropoff_time:
                money = payment[1]
                break
            else:
                money = 0
        losses.append(job[PAY][0][1]-money)

    if losses: return losses
    else: return [0]

def pickup_loss(state):
    losses=[]
    for job in state.unstarted_jobs:
        travel = dist(state.location, job[PICKUP], state.map)
        if state.time+travel <= job[TIME]:
            dropoff_time = job[TIME]+dist(job[PICKUP], job[DROPOFF], state.map)
        else:
            dropoff_time = state.time+travel+dist(job[PICKUP], job[DROPOFF], state.map)
        for payment in job[PAY]:
            if payment[0] >= dropoff_time:
                money = payment[1]
                break
            else:
                money = 0
        losses.append(job[PAY][0][1]-money)
        
    if losses: return losses
    else: return [0]

def heur_sum_delivery_costs(state):
#IMPLEMENT
    '''Bicycle Heuristic sum of delivery costs.'''
    #Sum over every job J being carried: Lost revenue if we
    #immediately travel to J's dropoff point and deliver J.
    #Plus 
    #Sum over every unstarted job J: Lost revenue if we immediately travel to J's pickup 
    #point then to J's dropoff poing and then deliver J.
    
    #print (deliver_loss(state)+pickup_loss(state))
    return sum(deliver_loss(state)+pickup_loss(state))


def heur_max_delivery_costs(state):
#IMPLEMENT
    '''Bicycle Heuristic sum of delivery costs.'''
    #m1 = Max over every job J being carried: Lost revenue if we immediately travel to J's dropoff
    #point and deliver J.
    #m2 = Max over every unstarted job J: Lost revenue if we immediately travel to J's pickup 
    #point then to J's dropoff poing and then deliver J.
    #heur_max_delivery_costs(state) = max(m1, m2)
    #print (deliver_loss(state)+pickup_loss(state))
    return max(deliver_loss(state)+ pickup_loss(state))

def bicycle_goal_fn(state):
#IMPLEMENT-ED
    '''Have we reached the goal (where all jobs have been delivered)?'''
    return (not state.unstarted_jobs) and (not state.current_jobs)

def make_start_state(map, job_list):
#IMPLEMENT-ED
    '''Input a map list and a job_list. Return a bicycle StateSpace object
    with action "START", gval = 0, and initial location "home" that represents the 
    starting configuration for the scheduling problem specified'''

    return bicycle("START", 0, [], "home", 0, 0, 0, job_list, map)

########################################################
#   Functions provided so that you can more easily     #
#   Test your implementation                           #
########################################################

def make_rand_map(nlocs):
    '''Generate a random collection of locations and distances 
    in input format'''
    lpairs = [(randint(0,50), randint(0,50)) for i in range(nlocs)]
    lpairs = list(set(lpairs))  #remove duplicates
    nlocs = len(lpairs)
    lnames = ["loc{}".format(i) for i in range(nlocs)]
    ldists = list()

    for i in range(nlocs):
        for j in range(i+1, nlocs):
            ldists.append([lnames[i], lnames[j],
                           int(round(euclideandist(lpairs[i], lpairs[j])))])
    return [lnames, ldists]

def dist(l1, l2, map):
    '''Return distance from l1 to l2 in map (as output by make_rand_map)'''
    ldist = map[1]
    if l1 == l2:
        return 0
    for [n1, n2, d] in ldist:
        if (n1 == l1 and n2 == l2) or (n1 == l2 and n2 == l1):
            return d
    return 0
    
def euclideandist(p1, p2):
    return sqrt((p1[0]-p2[0])*(p1[0]-p2[0]) + (p1[1]-p2[1])*(p1[1]-p2[1]))

def make_rand_jobs(map, njobs):
    '''input a map (as output by make_rand_map) object and output n jobs in input format'''
    jobs = list()
    for i in range(njobs):
        name = 'Job{}'.format(i)
        ploc = map[0][randint(0,len(map[0])-1)]
        ptime = randint(7*60, 16*60 + 30) #no pickups after 16:30
        dloci = randint(0, len(map[0])-1)
        if map[0][dloci] == ploc:
            dloci = (dloci + 1) % len(map[0])
        dloc = map[0][dloci]
        weight = randint(10, 5000)
        job = [name, ploc, ptime, dloc, weight]
        payoffs = list()
        amount = 50
        #earliest delivery time
        time = ptime + dist(ploc, dloc, map)
        for j in range(randint(1,5)): #max of 5 payoffs
            time = time + randint(5, 120) #max of 120mins between payoffs
            amount = amount - randint(5, 25)
            if amount <= 0 or time >= 19*60:
                break
            payoffs.append([time, amount])
        job.append(payoffs)
        jobs.append(job)
    return jobs

def test(nloc, njobs):
    map = make_rand_map(nloc)
    jobs = make_rand_jobs(map, njobs)
    print("Map = ", map)
    print("jobs = ", jobs)
    s0 = make_start_state(map, jobs)
    print("heur Sum = ", heur_sum_delivery_costs(s0))
    print("heur max = ", heur_max_delivery_costs(s0))
    se = SearchEngine('astar', 'full')
    #se.trace_on(2)
    final = se.search(s0, bicycle_goal_fn, heur_max_delivery_costs)
    

