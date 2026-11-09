from proofledger.contracts.values import board_cells, cell_position


def resolve_region(raw: dict, size: int) -> tuple[str, ...]:
    if not isinstance(raw, dict):
        raise ValueError("Region must be an object")
    kind = str(raw.get("kind", "")).upper()
    board = board_cells(size)
    if kind == "ROW":
        index = raw.get("index")
        if type(index) is not int:
            raise ValueError("Row index must be an integer")
        members = tuple(c for c in board if int(c[1:]) == index)
    elif kind == "COLUMN":
        index = str(raw.get("index", "")).upper()
        members = tuple(c for c in board if c[0] == index)
    elif kind == "NEIGHBORS":
        center = str(raw.get("cell", "")).upper()
        y, x = cell_position(center, size)
        members = tuple(c for c in board if c != center
                        and max(abs(cell_position(c, size)[0] - y),
                                abs(cell_position(c, size)[1] - x)) == 1)
    elif kind == "EXPLICIT":
        listed = raw.get("cells")
        if not isinstance(listed, list) or not all(isinstance(c, str) for c in listed):
            raise ValueError("Explicit region needs a list of coordinates")
        members = tuple(c.upper() for c in listed)
    elif kind == "CORNERS":
        members = tuple(c for c in board if cell_position(c, size)[0] in (0, size - 1)
                        and cell_position(c, size)[1] in (0, size - 1))
    elif kind == "BOUNDARY":
        members = tuple(c for c in board if 0 in cell_position(c, size)
                        or size - 1 in cell_position(c, size))
    else:
        raise ValueError(f"Unknown region selector: {kind}")
    if not members or len(set(members)) != len(members):
        raise ValueError("Region must be nonempty and cannot repeat coordinates")
    for cell in members:
        cell_position(cell, size)
    return members
