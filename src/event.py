import json
import time
import uuid

class EventLog:
    
    def __init__(self):
        # list of events as type Event
        self.events = []
        
    def add_event(self, event):
        self.events.append(event)

    def import_json(self, json_file):
        with open(json_file) as f:
            data = json.load(f)
            for event in data:
                self.add_event(event)
                
                
    def export_json(self, json_file):
        with open(json_file, 'w') as f:
            json.dump([event.__dict__ for event in self.events], f)
            
            
    def __str__(self):
        return str(self.events)

class Event:
    def __init__(self, timestamp, attributes):
        self.timestamp = timestamp
        self.id = str(uuid.uuid4())
        self.attributes = attributes
        
    def __str__(self):
        return str(self.__dict__)
    
    @staticmethod
    def create_event( attributes):
        timestamp = int(time.time())
        return Event(timestamp, attributes)
