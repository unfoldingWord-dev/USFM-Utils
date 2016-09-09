

class Element(object):
    def accept(self, visitor):
        """
        :param ElementVisitor visitor:
        """
        raise NotImplementedError()  # must be implemented by subclasses


class MaybeIntroductoryElement(Element):
    def __init__(self, introductory=False):
        """
        :param bool introductory:
        """
        self._introductory = introductory

    @property
    def introductory(self):
        """
        :rtype: bool
        """
        return self._introductory


class WeightedElement(Element):
    def __init__(self, weight=1):
        """
        :param int weight:
        """
        self._weight = weight

    @property
    def weight(self):
        return self._weight


class ParentElement(Element):
    def __init__(self, children):
        """
        :param Iterable[Element] children:
        """
        self._children = tuple(children)

    @property
    def children(self):
        """
        :rtype: Tuple[Element]
        """
        return self._children

    def visit_children(self, visitor):
        for child in self._children:
            child.accept(visitor)


class KindedElement(Element):
    def __init__(self, kind):
        self._kind = kind

    @property
    def kind(self):
        return self._kind
