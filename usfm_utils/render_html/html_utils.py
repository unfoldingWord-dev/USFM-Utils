

def add_class(attributes, clazz):
    if "class" in attributes:
        attributes["class"] += " " + clazz
    else:
        attributes["class"] = clazz


def open_tag(name, clazz=None, classes=None, **attributes):
    if clazz is not None:
        attributes["class"] = clazz
    if classes is not None:
        attributes["class"] = " ".join(classes)
    if len(attributes) == 0:
        return "<{}>".format(name)
    return "<{} {}>".format(name, " ".join(
        attr + "=\"" + val + "\"" for attr, val in attributes.items()))


def close_tag(name):
    return "</{}>".format(name)


def open_close(name, classes=None, identifier=None):
    return open_tag(name, classes=classes, identifier=identifier), close_tag(name)


def open_span(clazz=None, classes=None, **attributes):
    return open_tag("span", clazz=clazz, classes=classes, **attributes)


def close_span():
    return close_tag("span")
