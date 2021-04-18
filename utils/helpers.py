
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


def get_normed(r1):
    return r1 / sum(r1) if sum(r1) else 1 / len(r1)

