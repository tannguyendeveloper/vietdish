import json

# Add documentation for the Recipe model as well as the methods

class Recipe:
    def __init__(self, data):
        self.id = data.get('id')
        self.title = data.get('title')
        self.source = {
            'name': data.get('sourceName', data.get('creditsText', '')),
            'url': data.get('sourceUrl')
        }
        self.images = {
            'original': data.get('image'),
            'sizes': {
                '240': f"https://spoonacular.com/recipeImages/{self.id}-240x150.{data.get('imageType')}",
                '312': f"https://spoonacular.com/recipeImages/{self.id}-312x231.{data.get('imageType')}",
                '480': f"https://spoonacular.com/recipeImages/{self.id}-480x360.{data.get('imageType')}",
                '636': f"https://spoonacular.com/recipeImages/{self.id}-636x393.{data.get('imageType')}"
            }
        }
        # Think it would be good to separate some of these out into shorter variables
        # so that lines like 30 won't be too long.
        #
        # prepMins = data.get('preparationMinutes')
        # cookingMins = data.get('cookingMinutes')
        # readyMins = data.get('readyInMinutes')
        # ...
        self.cooking_times = {
            'prep': data.get('preparationMinutes'),
            'cooking': data.get('cookingMinutes'),
            'total': data.get('readyInMinutes') if not data.get('readyInMinutes') == data.get('cookingMinutes') else data.get('preparationMinutes') + data.get('cookingMinutes')
        }
        self.servings = data.get('servings')
        self.ingredients = parse_ingredients(data.get('extendedIngredients'))
        self.directions = parse_directions(data.get('analyzedInstructions')[0].get('steps')) if data.get('analyzedInstructions') else None
        self.instructions = parse_instructions(data.get('analyzedInstructions')) if data.get('analyzedInstructions') else None
        self.equipment = parse_equipment_from_directions(self.instructions) if self.instructions else None
        self.nutrients = data.get('nutrition').get('nutrients')

# These might be better as static methods that are part of the Recipe class w/ the @staticmethod
# decorator
def parse_ingredients(ingredients):
    return list(map(parse_ingredient, ingredients)) if ingredients else []

def parse_ingredient(ingredient):
    image = f"https://spoonacular.com/cdn/ingredients_100x100/{ingredient.get('image')}" if ingredient.get('image') else ''
    return {
        'id': ingredient.get('id'),
        'name': ingredient.get('name').capitalize(),
        'image': image,
        'measures': ingredient.get('measures')
    }

def parse_directions(directions):
    return list(map(parse_step, directions)) if directions else []

def parse_step(step):
    return {
        'number': step.get('number'),
        'step': step.get('step'),
        'equipment': step.get('equipment')
    }

def parse_instructions(instructions):
    instruction_sets = []
    for instruction in instructions:
        instruction_set = {
            'name': instruction.get('name'),
            'steps': parse_directions(instruction.get('steps'))
        }
        instruction_sets.append(instruction_set)
    return instruction_sets

def parse_equipment_from_directions(instructions):
    equipment_set = set()
    equipment_list = []
    # A bit hesitant on such a nested forloop. Is there a way we can use list
    # comprehension here to make it more readable?
    for instruction in instructions:
        steps = instruction.get('steps', [])
        for step in steps:
            if step.get('equipment'):
                for equipment in step.get('equipment'):
                    # Is there a need for an equipment check here if we're looping through
                    # step.get('equipment')?
                    if equipment:
                        ## Create a new object so that we can remove duplicates. Equiptment might have multiple id with the same image
                        item = {
                            'name': equipment.get('name'),
                            'image': equipment.get('image')
                        }
                        equipment_set.add(json.dumps(item))
    for equipment in equipment_set:
        equipment_list.append(parse_equipment(json.loads(equipment)))
    return equipment_list

def parse_equipment(equipment):
    images = {}
    if equipment.get('image'):
        images = {
            '100': f"https://spoonacular.com/cdn/equipment_100x100/{equipment.get('image')}",
            '250': f"https://spoonacular.com/cdn/equipment_250x250/{equipment.get('image')}",
            '500': f"https://spoonacular.com/cdn/equipment_500x500/{equipment.get('image')}"
        }
    return {
        'id': equipment.get('id'),
        'name': equipment.get('name'),
        'images': images
    }

