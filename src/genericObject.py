class GenericObject:
    def __init__(self, **attributes):
        self.__dict__.update(attributes)
    
    def state(self):
        return self.__dict__.get('state', None)  # Assuming 'state' is a common attribute
    
    def __str__(self):
        return str(self.__dict__)