

class ResourceState(object):
    def __init__(self, id, free):
        self.id = id
        self.free = free

class Registry(object):

    def __init__(self)
        self.states = dict()

    def get_resources(self.job):
        return [s.id for s in states.iter_values() if s.free >= job.size]

    def update_state(self, state):
        self.states[state.id] = state


