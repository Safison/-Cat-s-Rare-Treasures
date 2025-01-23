from pg8000.native import identifier
def add_colour_condition(string, colour):
    return string + f" WHERE colour = {identifier(colour)}"