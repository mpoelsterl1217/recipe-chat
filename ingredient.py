


class Ingredient:

    def __init__(self, quantity, measurement, descriptors, ingredient_name, preparations):
        self.quantity = quantity
        self.measurement = measurement
        self.descriptors = descriptors
        self.ingredient_name = ingredient_name
        self.preparations = preparations

    def __str__(self):
        str = ""
        str += self.quantity + " "
        str += self.measurement + " "
        str += " ".join(self.descriptors) + " "
        str += self.ingredient_name
        str += self.get_formated_preparation()
        return " ".join(str.split())

    def get_formated_preparation(self):
        if len(self.preparations) == 0:
            return ""
        elif len(self.preparations) == 1:
            return f", {self.preparations[0]}"
        elif len(self.preparations) == 2:
            return f", {self.preparations[0]} and {self.preparations[1]}"
        else:
            return ", " + ", ".join(self.preparations)

    def __repr__(self):
        return self.__str__()