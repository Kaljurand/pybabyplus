"""
Ontology of tags
"""

# TODO: refactor
class B:
    """Bottle"""

    def __init__(self, id: str, level: int, pp: str):
        self.id = id
        self.level = level
        self.pp = pp

    def __str__(self):
        return self.pp


class F:
    """Food"""

    def __init__(self, id: str, level: int, pp: str):
        self.id = id
        self.level = level
        self.pp = pp

    def __str__(self):
        return self.pp


class S:
    """Shit"""

    def __init__(self, id: str, pp: str):
        self.id = id
        self.pp = pp

    def __str__(self):
        return self.pp


rename_tag = dict(bp="b0", nuk="nuks", steri="nuk0")

lookup_tag = dict(
    # Food
    b0=F("b0", 0, "Beba Pre"),
    b01=F("b01", 0.5, "Beba Pre + Beba 1"),
    bop1=F("bop1", 1, "Beba Opti Pro 1"),
    bs0=F("bs0", 0, "Beba Supreme Pre"),
    bseha0=F("bseha0", 0, "Beba Supreme Pre + Beba Expert HA Pre"),
    # Shit
    mustard=S("mustard", "Mustard"),
    dgreen=S("dgreen", "Dark Green"),
    lgreen=S("lgreen", "Light Green"),
    # Bottle
    nuk0=B("nuk0", 0, "Nuk0"),  # TODO: is "Nuk0" the most official name?
    nuks=B("nuks", 1, "Nuk S"),
    nukm=B("nukm", 1, "Nuk M"),
    mam=B("mam", 1, "Mam"),
    mam2=B("mam2", 2, "Mam 2"),
    avent=B("avent", 1, "Avent 1"),
    avent2=B("avent2", 2, "Avent 2"),
    aventn2=B("aventn2", 2, "Avent Natural 2"),
)


def gen_tag_aux(tags_as_str):
    """
    """
    for tag_as_str in tags_as_str.split(";"):
        if tag_as_str:
            tag_as_str = tag_as_str.lower()
            tag_as_str = rename_tag.get(tag_as_str, tag_as_str)
            tag = lookup_tag.get(tag_as_str)
            if tag:
                yield tag
            else:
                yield tag_as_str


def gen_tag(tags_as_str):
    return set(gen_tag_aux(tags_as_str))
