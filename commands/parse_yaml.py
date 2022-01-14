import pathlib

import yaml

options = yaml.safe_load(pathlib.Path("options.yaml").open())

print(int(options["database"]["deploy"]))
