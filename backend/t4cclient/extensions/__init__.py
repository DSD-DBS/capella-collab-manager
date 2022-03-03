from importlib import metadata


def load_modelsource(name: str):
    try:
        ep = next(
            i
            for i in metadata.entry_points()["capellacollab.extensions.modelsources"]
            if i.name == name
        )
    except StopIteration:
        raise ValueError(f"Unknown modelsource {name}")

    return ep.load()
