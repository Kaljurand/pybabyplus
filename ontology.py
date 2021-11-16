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


lookup_tag = dict(
    # Food
    b0=F("b0", 0, "Beba Pre"),
    bp=F("b0", 0, "Beba Pre"),
    bs0=F("bs0", 0, "Beba Supreme Pre"),
    # Shit
    mustard=S("mustard", "Mustard"),
    dgreen=S("dgreen", "Dark Green"),
    lgreen=S("lgreen", "Light Green"),
    # Bottle
    steri=B("steri", 0, "SteriFeed"),
    nuk=B("nuk", 1, "Nuk"),
    mam=B("mam", 1, "Mam"),
    avent=B("avent", 1, "Avent"),
    aventn2=B("aventn2", 2, "Avent Natural"),
)


def gen_tag_aux(tags_as_str):
    for tag_as_str in tags_as_str.split(";"):
        if tag_as_str:
            tag = lookup_tag.get(tag_as_str.lower())
            if tag:
                yield tag
            else:
                yield tag_as_str


def gen_tag(tags_as_str):
    return set(gen_tag_aux(tags_as_str))
