class State:
    def __init__(self, steps_list, ingredient_list):
        self.steps_list = steps_list
        self.ingredient_list = ingredient_list
        self.in_steps = False
        self.current_step = None
        self.input_history = []
        self.output_history = []