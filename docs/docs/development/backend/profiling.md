<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Profile Backend Routes

Profiling can be useful if you want to examine the performance of specific
backend routes.

## Enable profiling

In the `config.yaml`, set the `logging.profiling` key to `True`. Then, call the
route you want to profile with the `profile` query parameter set to `True`.

For example, to profile the `/api/v1/metadata` route, you would call
`/api/v1/metadata?profile=True` in the browser. It will return a HTML report.

!!! info

    Synchronous routes are not supported properly. If you want to profile a
    synchronous route, add `async` to the route definition.

    ```
    @router.get(...)
    def metadata():
        ...
    ```

    becomes

    ```
    @router.get(...)
    async def metadata():
        ...
    ```

    [More Information on GitHub](https://github.com/joerick/pyinstrument/issues/257)

# Enable async debugging

In the `config.yaml`, set the `logging.asyncDebug` key to `True`. This will set
`PYTHONASYNCIODEBUG=1`, which will enable asyncio debug logging. Check the
[python docs](https://docs.python.org/3/library/asyncio-dev.html) for more
information.
