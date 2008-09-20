class ResourceState(object):
    def __init__(self, agent, free):
        self.agent = agent
        self.free = free

class Registry(object):

    def __init__(self):
        self.states = dict()

    def get_resources(self, allocation):
        return [s for s in self.states.itervalues() 
                if s.free >= allocation.job.size]

    def update_state(self, state):
        self.states[state.agent] = state


