import datetime
import json
from jsonschema import validate, ValidationError
import requests

from genericObject import GenericObject

OCEL_SCHEMA_URL = 'https://www.ocel-standard.org/2.0/ocel20-schema-json.json'


class OCELParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.json_data = None

    def load_json(self):
        with open(self.file_path, 'r') as f:
            self.json_data = json.load(f)
        return self.json_data

    def validate_json(self):

        response = requests.get(OCEL_SCHEMA_URL)
        schema = response.json()
        try:
            validate(instance=self.json_data, schema=schema)
            print("JSON is valid against the schema.")
        except ValidationError as e:
            print(f"JSON validation error: {e.message}")
            raise

    def parse(self, validate_json=True):
        self.load_json()
        if validate_json:
            self.validate_json()
        return self.json_data


class OCEL:
    def __init__(self):
        self.event_type = {}
        self.object_type = {}
        self.events = {}
        self.objects = {}
        self.event_objects = []
        self.object_objects = []

    def add_event_type(self, event_type, event_type_map):
        self.event_type[event_type] = event_type_map

    def get_event_types(self):
        return self.event_type

    def add_object_type(self, object_type, object_type_map):
        self.object_type[object_type] = object_type_map

    def get_object_types(self):
        return self.object_type

    def add_event(self, event_id, event):
        self.events[event_id] = event

    def get_events(self):
        return self.events

    def add_object(self, object_id, object_type):
        self.objects[object_id] = object_type

    def get_objects(self):
        return self.objects

    def add_event_object(self, event_id, object_id, qualifier):
        self.event_objects.append({'ocel_event_id': event_id, 'ocel_object_id': object_id, 'ocel_qualifier': qualifier})

    def get_event_objects(self):
        return self.event_objects

    def add_object_object(self, source_id, target_id, qualifier):
        self.object_objects.append(
            {'ocel_source_id': source_id, 'ocel_target_id': target_id, 'ocel_qualifier': qualifier})

    def get_object_objects(self):
        return self.object_objects

    def parse_and_store(self, file_path, validate_json=True):
        parser = OCELParser(file_path)
        json_data = parser.parse(validate_json=validate_json)

        for event_type in json_data['eventTypes']:
            self.add_event_type(event_type['name'], event_type)

        for object_type in json_data['objectTypes']:
            self.add_object_type(object_type['name'], object_type)
        for event in json_data['events']:
            self.add_event(event['id'], event)
            for relationship in event['relationships']:
                self.add_event_object(event['id'], relationship["objectId"], relationship["qualifier"])
        for obj in json_data['objects']:
            attributes = obj['attributes']
            objectTypeAttributes = self.object_type[obj['type']]['attributes']
            new_attributes = []
            # ensure that saved object has all attributes of its type
            for object_attribute in objectTypeAttributes:
                if object_attribute['name'].lower() not in [attr['name'].lower() for attr in attributes]:
                    attribute = {'name': object_attribute['name'], 'time': None, 'value': None}
                    attributes.append(attribute)
            # ensure common null handling of attribute values
            for attribute in attributes:
                new_attributes.append(attribute)

            obj['attributes'] = new_attributes
            self.add_object(obj['id'], obj)
            if 'relationships' in obj:
                for rel_obj in obj['relationships']:
                    self.add_object_object(obj['id'], rel_obj['objectId'], rel_obj["qualifier"])

    def get_events_for_object(self, object_id):
        events = []
        events_names = {}
        for event_obj in self.event_objects:
            if object_id == event_obj["ocel_object_id"]:
                events.append(event_obj["ocel_event_id"])
        for event in events:
            events_names[event] = (self.events[event]["type"])
        return events_names

    def get_related_objects(self, object_id):
        related_objects = {}
        for obj_obj in self.object_objects:
            if object_id == obj_obj["ocel_source_id"]:
                object_type = self.objects[obj_obj["ocel_target_id"]]['type']
                related_objects.setdefault(object_type, []).append(obj_obj["ocel_target_id"])
            if object_id == obj_obj["ocel_target_id"]:
                object_type = self.objects[obj_obj["ocel_source_id"]]['type']
                related_objects.setdefault(object_type, []).append(obj_obj["ocel_source_id"])
        return related_objects

    def get_objects_with_events_and_foreign_key(self):
        objects = []
        for obj_id, obj in self.objects.items():
            current_object = GenericObject(clazz=obj['type'], id=obj_id)

            attributes = obj['attributes']
            for attribute in attributes:
                current_object.__dict__[attribute['name']] = attribute['value']

            current_object.events = self.get_events_for_object(obj_id)
            # add related objects as attribute
            current_object.related_objects = self.get_related_objects(obj_id)
            # current_object.related_objects = related_objects
            objects.append(current_object)
        return objects