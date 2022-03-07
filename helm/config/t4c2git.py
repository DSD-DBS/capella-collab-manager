# onStartup: 0
"""EASE script to sync (one-directional) from a T4C Capella model to a Git model.

.. note::

    The module expects, that Eclipse/ Capella is set to English language.


.. seealso::

    The acronym EASE stands for "Eclipse Advanced Scripting Environment".
    Further information: https://www.eclipse.org/ease/

One can optionally set an environment variable named ``DEBUG`` to ``"1"`` to get
a debug level logging with more detailed information (module, function, line no).

Before this script can be run within an EASE context (see below), one must set an
environment variable named ``EASE_WORKSPACE`` pointing to a workspace directory that
will be created/ overwritten.

Then one executes the installed module ``pyease.ease.py`` using a Python3 interpreter to
create a workspace for the execution of Python EASE scripts:

.. code-block:: bash

    python3 -m pyease.ease


The script logs what it does into a log file named ``t4c2git.log`` in the workspace
defined in the environment variable ``EASE_WORKSPACE``.

How to run the current script in EASE is further described with step 2 below.

***************************************************
Three steps to get this Python module to do the job
***************************************************

Step 1
======

The following preconditions must be fulfilled on the computer running this module:

* A Python3 interpreter must be installed
* A Git client (including git-lfs) must be installed
* The current script must be available so that it can be executed
* A Capella client including a configured (license key
  ``DOBEO_LICENSE_SERVER_CONFIGURATION`` in the file
  ``/path/to/Capella/Contents/Eclipse/capella.ini``) T4C client must be available.
* In addition to the set of the common Capella plugins that are used at "Digitale
  Schiene Deutschland" there are other plugins needed and a list can be found on
  Confluence at
  https://rmt.jaas.service.deutschebahn.com/confluence/display/SSI/T4C+-+How+to+Script+Capella

Step 2
======

To get EASE doing the synchronisation for a model in T4C to GitLab:

The script will be run automatically when Capella is started in the workspace that has
been prepared (see above)

The following environment variables must be set:

* ``EASE_WORKSPACE`` (see step 2 from above)
* ``GIT_REPO_URL``
* ``GIT_REPO_BRANCH`` (e. g. ``nightly``)
* ``T4C_REPO_HOST`` (e.g. 10.107.242.175)
* ``T4C_REPO_PORT_NO`` (e.g. 2036)
* ``T4C_REPO_NAME``
* ``T4C_USERNAME``
* ``T4C_PASSWORD``

In the file ``capella.ini`` we need to set a JVM system property by ensuring the
following line some where in the ``.ini`` file:

.. code-block:: ini

    -Dorg.eclipse.swtbot.search.timeout=1000

Capella must then be started via:

.. code-block:: bash

    /path/to/capella -data $EASE_WORKSPACE

Capella will fire up and auto execute this script because of the magic comment
in line 1.

EASE will run through and shutdown Capella at the end.

"""
# Standard library:
import datetime
import os
import shutil
import subprocess
import sys
import typing as t
from pathlib import Path
from tempfile import gettempdir

MODULE_DIR: Path = Path(__file__).parents[0]

try:
    # 1st party:
    import pyease.ease as ease  # noqa: E402
    import pyease.easeexceptions as exp  # noqa: E402
except Exception:  # catching NameError does not work with EASE
    # Local modules are not found because EASE manipulates sys.path:
    # 3rd party:
    from eclipse.system.environment import getScriptEngine  # type: ignore

    MODULE_DIR = Path(str(getScriptEngine().getExecutedFile())).parent
    sys.path.insert(0, str(MODULE_DIR))

    # 1st party:
    import pyease.ease as ease  # noqa: E402
    import pyease.easeexceptions as exp  # noqa: E402

BOT: t.Any = ease.BOT
DEBUG = ease.DEBUG

logger = ease.logger
log_file_dir: Path = ease.workspace_path()
ease.log_to_file(
    log_file_path=os.environ.get("EASE_LOG_LOCATION", log_file_dir / "t4c2git.log")
)


def read_and_log_environment_variables() -> t.Tuple[str, ...]:
    """Read environment variables and log read values.

    Returns
    -------
    t.Tuple[str, ...]
        Tuple with variables that have been read from the environment

    """
    logger.info("Read parameters from environment variables...")
    git_repo_url: str = os.getenv("GIT_REPO_URL", "")
    git_repo_branch: str = os.getenv("GIT_REPO_BRANCH", "")
    t4c_repo_host: str = os.getenv("T4C_REPO_HOST", "")
    t4c_repo_port_no: str = os.getenv("T4C_REPO_PORT_NO", "")

    t4c_repo_name: str = os.getenv("T4C_REPO_NAME", "")
    t4c_project_name: str = os.getenv("T4C_PROJECT_NAME", "")

    t4c_username: str = os.getenv("T4C_USERNAME", "")
    t4c_password: str = os.getenv("T4C_PASSWORD", "")
    logger.info(f"\tGIT_REPO_URL         : '{git_repo_url}'")
    logger.info(f"\tGIT_REPO_BRANCH      : '{git_repo_branch}'")
    logger.info(f"\tT4C_REPO_HOST        : '{t4c_repo_host}'")
    logger.info(f"\tT4C_REPO_PORT_NO     : '{t4c_repo_port_no}'")
    logger.info(f"\tT4C_REPO_NAME        : '{t4c_repo_name}'")
    logger.info(f"\tT4C_PROJECT_NAME     : '{t4c_project_name}'")
    logger.info(f"\tT4C_USERNAME         : '{t4c_username}'")
    logger.info(
        "\tT4C_PASSWORD     : WILL NOT BE LOGGED HERE. Check env var 'T4C_PASSWORD'"
    )
    return (
        git_repo_url,
        git_repo_branch,
        t4c_repo_host,
        t4c_repo_port_no,
        t4c_repo_name,
        t4c_project_name,
        t4c_username,
        t4c_password,
    )


if __name__ == "__main__":
    ease.log_intro_messages()
    if BOT is None:
        raise exp.EaseNoSWTWorkbenchBotError
    (
        git_repo_url,
        git_repo_branch,
        t4c_repo_host,
        t4c_repo_port_no,
        t4c_repo_name,
        t4c_project_name,
        t4c_username,
        t4c_password,
    ) = read_and_log_environment_variables()

    logger.info(
        f"Name of project to one-way-synchronise (T4C to Git): '{t4c_project_name}'."
    )

    # When this script is run in a CI pipeline we want that generic exceptions
    # and the according traceback will be written into the log file.
    # Hence, the next try/ except block is a dirty hack to achieve that :-)
    try:
        # to have Capella GUI actions available:
        ease.open_eclipse_perspective("Capella")
        if DEBUG:
            # to have the view available for quick re-execution of this EASE script:
            ease.open_eclipse_view("Scripting", "Script Explorer")
            # to have the view in the foreground to look at logging output:
            ease.open_eclipse_view("General", "Console")

        tmp_git_clone_dir: Path = Path(gettempdir()) / t4c_project_name
        ease.import_model_from_remote_repository(
            t4c_repo_host=t4c_repo_host,
            t4c_repo_port_no=t4c_repo_port_no,
            t4c_repo_name=t4c_repo_name,
            t4c_project_name=t4c_project_name,
            t4c_username=t4c_username,
            t4c_password=t4c_password,
        )
        ease.clone_project_from_git(
            git_repo_url=git_repo_url,
            git_repo_branch=git_repo_branch,
            target_git_clone_dir=tmp_git_clone_dir,
            depth=None,
        )
        shutil.copytree(
            src=Path(f"/workspace/{t4c_project_name}"),
            dst=tmp_git_clone_dir,
            dirs_exist_ok=True,
        )
        try:
            cmd: list[str] = ["git", "add", "."]
            cmd_str: str = " ".join(cmd)
            logger.info(f"Execute command '{cmd_str}'...")
            subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                cwd=tmp_git_clone_dir,
            )
            if "nothing to commit" in subprocess.check_output(
                ["git", "status"], cwd=tmp_git_clone_dir
            ).decode("utf8"):
                logger.info("No changes to backup")
            else:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
                cmd = ["git", "commit", "-m", f"Backup {timestamp}"]
                cmd_str = " ".join(cmd)
                logger.info(f"Execute command '{cmd_str}'...")
                subprocess.run(
                    cmd,
                    check=True,
                    capture_output=True,
                    cwd=tmp_git_clone_dir,
                )
                cmd = ["git", "push", "origin", git_repo_branch]
                cmd_str = " ".join(cmd)
                logger.info(f"Execute command '{cmd_str}'...")
                subprocess.run(
                    cmd,
                    check=True,
                    capture_output=True,
                    cwd=tmp_git_clone_dir,
                )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"Git command failed in directory '{tmp_git_clone_dir}': "
                + str(e.stderr)
            ) from e
        exit_signal = 30
    except Exception:
        logger.exception("An unexpected error occured:")
        exit_signal = 9
    if DEBUG:
        ease.open_eclipse_view("Scripting", "Script Explorer")
        logger.info(
            "Capella will be kept open when the environment "
            "variable 'DEBUG' is set to '1'!"
        )
    else:
        logger.info("Exit Capella.")
        ease.kill_capella_process(exit_signal)  # type: ignore # noqa
    logger.info("Done.")
