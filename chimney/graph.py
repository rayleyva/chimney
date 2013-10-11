from collections import OrderedDict
try:
    from functools import reduce
except ImportError:
    pass


class Digraph(OrderedDict):
    def __init__(self, roots=None):
        super(Digraph, self).__init__()
        if roots:
            map(self.arc, roots)

    def __missing__(self, key):
        val = set()
        self[key] = val
        return val

    def arc(self, key, *depends_on):
        if key not in self:
            self[key] = set()

        print key, 'depends_on', depends_on
        self[key] = self[key].union(depends_on)
        print 'now', key, 'depends_on', self[key]
        for value in depends_on:
            # ensure there's a key for this dependency
            if not value in self:
                self[value] = set()

    def leafs(self):
        """
        Leafs don't depend on any other objects
        """
        ret = []
        for node, deplist in self.items():
            if not deplist or len(deplist) < 1:
                ret.append(node)
        return ret

    def roots(self):
        """
        Find roots in the graph. Nothing depends on a root.
        """
        nodes = OrderedDict()
        map(nodes.__setitem__, self.keys(), [])
        for node, deplist in self.items():
            for dep in deplist:
                nodes[dep] = True
        return [node for node, color in nodes.items() if not color]

    def traverse(self):
        ret = OrderedDict()
        level = self.roots()
        while len(level) > 0:
            nextlevel = OrderedDict()
            for node in level:
                if node not in ret:
                    ret[node] = None
                    # add dependencies to the next stack
                    map(nextlevel.__setitem__, self[node], [])
            level = nextlevel.keys()
        return ret.keys()

    ## {{{ http://code.activestate.com/recipes/577413/ (r1)
    def toposort2(self):
        if len(self) > 0:
            data = Digraph()
            map(data.__setitem__, self.keys(), self.values())

            for k, v in data.items():
                v.discard(k)   # Ignore self dependencies
            extra_items_in_deps = reduce(set.union, data.values()) - set(data.keys())
            data.update(dict([(k, set()) for k in extra_items_in_deps]))
            while True:
                ordered = set(item for item, dep in data.items() if not dep)
                if not ordered:
                    break
                for el in ordered:
                    yield el
                data = dict([(item, (dep - ordered)) for item, dep in data.items()
                            if item not in ordered])
            assert not data, "Data has a cyclic dependency"
    ## end of http://code.activestate.com/recipes/577413/ }}}
