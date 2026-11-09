from proofledger.contracts.values import board_cells


def puzzle(size=3):
    cells = board_cells(size)
    return {
        "id": "fixture", "title": "Test investigation", "size": size,
        "characters": [{"cell": c, "name": f"Person {i:02}", "profession": "Maker"}
                       for i, c in enumerate(cells)],
        "solution": {c: "INNOCENT" for c in cells},
        "clues": {c: {"id": f"e{i}", "type": "FACT", "data": {
            "cell": cells[(i + 1) % len(cells)], "status": "INNOCENT"}}
            for i, c in enumerate(cells)},
        "initially_revealed": ["A1"],
    }
