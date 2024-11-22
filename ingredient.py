


class Ingredient:

    def __init__(self, quantity, measurement, descriptor, ingredient_name, preparation):
        self.quantity = quantity
        self.measurement = measurement
        self.descriptor = descriptor
        self.ingredient_name = ingredient_name
        self.preparation = preparation

    def __str__(self):
        return " ".join(f"{self.quantity if self.quantity else ""} {self.measurement if self.measurement else ""} {self.descriptor if self.descriptor else ""} {self.ingredient_name if self.ingredient_name else ""}{", " + self.preparation if self.preparation else ""}".split())
