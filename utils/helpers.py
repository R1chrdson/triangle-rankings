
def get_float(string):
    if not string:
        raise ValueError('Empty value!')
    return float(string.replace(',', '.'))


def change_visibility(elements, state):
    for element in elements:
        if state:
            element.show()
        else:
            element.hide()
