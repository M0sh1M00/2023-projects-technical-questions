from dataclasses import dataclass
from enum import Enum
from typing import Union, NamedTuple, List
from flask import Flask, request, Response, jsonify
import json

# SpaceCowboy models a cowboy in our super amazing system
@dataclass
class SpaceCowboy:
    name: str
    lassoLength: int

# SpaceAnimal models a single animal in our amazing system
@dataclass
class SpaceAnimal:
    # SpaceAnimalType is an enum of all possible space animals we may encounter
    class SpaceAnimalType(Enum):
        PIG = "pig"
        COW = "cow"
        FLYING_BURGER = "flying_burger"

    type: SpaceAnimalType

def GetDistance(entity_1, entity_2):
    return ((entity_1.location['x'] - entity_2.location['x'])**2 + (entity_1.location['y'] - entity_2.location['y'])**2)**0.5

# SpaceEntity models an entity in the super amazing (ROUND UPPER 100) system
@dataclass
class SpaceEntity:
    class Location(NamedTuple):
        x: int
        y: int

    metadata: Union[SpaceCowboy, SpaceAnimal]
    location: Location

# ==== HTTP Endpoint Stubs ====
app = Flask(__name__)
space_database: List[SpaceEntity] = []

# the POST /entity endpoint adds an entity to your global space database
@app.route('/entity', methods=['POST'])
def create_entity():
    try:
        entities = json.loads(json.dumps(request.get_json()))['entities']
    except:
        return Response(response="Incorrect parameters", status=400)

    for entitiy in entities:
        try:
            if entitiy['type'] == "space_cowboy":
                space_database.append(SpaceEntity(SpaceCowboy(entitiy['metadata']['name'], entitiy['metadata']['lassoLength']), entitiy['location']))
            elif entitiy['type'] == "space_animal":
                space_database.append(SpaceEntity(SpaceAnimal(entitiy['metadata']['type']), entitiy['location']))
        except:
            return Response(response="Incorrect formatting for entity: "+ str(entitiy), status=400)

    return {}

# lasooable returns all the space animals a space cowboy can lasso given their name

# Assume the space_database is correct formatting so dont need to do much error checking
@app.route('/lassoable', methods=['GET'])
def lassoable():
    # Time complexity is O(N)
    cowboy_name = request.args.get('cowboy_name')
    if not cowboy_name:
        
        return Response(response="No Cowboy specified", status=400)

    for cowboy_entity in space_database:
        if type(cowboy_entity.metadata) == SpaceCowboy and cowboy_entity.metadata.name == cowboy_name:
            animal_list = []
            
            for animal_entity in space_database:
                
                # Short circut 'and' to check type then distance, if valid add and return
                if type(animal_entity.metadata) == SpaceAnimal and GetDistance(cowboy_entity, animal_entity) <= cowboy_entity.metadata.lassoLength:
                    
                    animal_list.append({
                        "type":animal_entity.metadata.type,
                        "location":{'x':animal_entity.location['x'], 'y':animal_entity.location['y']}})

            return {"space_animals": animal_list}
            
    return Response(response="Cowboy not found", status=400)


# DO NOT TOUCH ME, thanks :D
if __name__ == '__main__':
    app.run(debug=True, port=8080)
