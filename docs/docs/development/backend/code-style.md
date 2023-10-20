<!--
 ~ SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

## General

We base our code style on a modified version of the [Google style guide] for
Python code. The key differences are:

- **Docstrings**: The [Numpy style guide] applies here.

      When writing docstrings for functions, use the imperative style, as
      per [PEP-257]. For example, write "Do X and Y" instead of "Does X and Y".

- **Overridden methods**: If the documentation did not change from the base
  class (i.e. the base class' method's docstring still applies without
  modification), do not add a short docstring á la "See base class". This lets
  automated tools pick up the full base class docstring instead, and is
  therefore more useful in IDEs etc.

- **Linting**: Use [pylint] for static code analysis, and [mypy] for static
  type checking.

- **Formatting**: Use [black] as code auto-formatter. The maximum line length
  is 79, as per [PEP-8]. This setting should be automatically picked up from
  the `pyproject.toml` file. The reason for the shorter line length is that it
  avoids wrapping and overflows in side-by-side split views (e.g. diffs) if
  there's also information displayed to the side of it (e.g. a tree view of the
  modified files).

      Be aware of the different line length of 72 for docstrings. We
      currently do not have a satisfactory solution to automatically apply
      or enforce this.

      Note that, while you're encouraged to do so in general, it is not a hard
      requirement to break up long strings into smaller parts. Additionally, never
      break up strings that are presented to the user in e.g. log messages, as that
      makes it significantly harder to grep for them.

      Use [isort] for automatic sorting of imports. Its settings should automatically
      be picked up from the `pyproject.toml` file as well.

- **Typing**: We do not make an exception for `typing` imports. Instead of
  writing `from typing import SomeName`, use `import typing as t` and access
  typing related classes like `t.TypedDict`.

      Use the new syntax and classes for typing introduced with Python 3.10.

      - Instead of `t.Tuple`, `t.List` etc. use the builtin classes `tuple`, `list`
        etc.
      - For classes that are not builtin (e.g. `Iterable`), `import collections.abc
        as cabc` and then use them like `cabc.Iterable`.
      - Use [PEP-604]-style unions, e.g. `int | float` instead of `t.Union[int, float]`.
      - Use `... | None` (with `None` always as the last union member) instead of
        `t.Optional[...]` and always explicitly annotate where `None` is possible.

- **Python style rules**: For conflicting parts, the [black] code style wins.
  If you have set up `black` correctly, you don't need to worry about this
  though :)
- When working with `dict`s, consider using `t.TypedDict` instead of a more
  generic `dict[str, float|int|str]`-like annotation where possible, as the
  latter is much less precise (often requiring additional `assert`s or
  `isinstance` checks to pass) and can grow unwieldy very quickly.
- Prefer `t.NamedTuple` over `collections.namedtuple`, because the former uses
  a more convenient `class ...:` syntax and also supports type annotations.

## Conventions

### Imports

1.  Always use `from x import y` or `from x import y as z` when importing
    modules. The only exception is when you are importing a high-level package
    or module, such as `import fastapi`

1.  Given that we often have identical file names across our modules and
    submodules, adhering to the Google style guide can lead to naming conflicts
    during imports. To address this, we distinguish between the following two
    cases:

    1. _Importing a module from the current directory_: In this case, we do not
       need to rename the module and can use it as is. For instance, if we are
       in `capellacollab.projects.toolsmodels`, we can simply import the `crud`
       and `model` modules like this: `from . import crud, model`.

    2. _Importing a module from a different directory_: In this scenario, we
       must add an `as xy` suffix to avoid naming conflicts with the first
       case. We follow this pattern:

       `from capellacollab.extensions.<extension> import submodule as <extension>_<submodule>`

       For example, if we are in `capellacollab.sessions` and want to import
       `crud` from `capellacollab.projects.toolsmodels`, we would do it like
       this:

       `from capellacollab.projects.toolmodels import crud as toolmodels_crud`

1.  Only use relative imports up to one level above the current one. This means
    you should use `from . import y` for the current module and
    `from .. import y as z` for one level above. For all other imports beyond
    this level, use the full path as described in 3.

### Naming conventions

- All SQLAlchemy models should have `Database` as a prefix, e.g.,
  `DatabaseProject` or `DatabaseUser`.

[google style guide]: https://google.github.io/styleguide/pyguide.html
[numpy style guide]: https://numpydoc.readthedocs.io/en/latest/format.html
[pep-8]: https://peps.python.org/pep-0008/
[pep-257]: https://peps.python.org/pep-0257/
[pep-604]: https://www.python.org/dev/peps/pep-0604/
[mypy]: https://github.com/python/mypy
[pylint]: https://github.com/PyCQA/pylint
[isort]: https://github.com/PyCQA/isort
[black]:
  https://black.readthedocs.io/en/stable/the_black_code_style/current_style.html
