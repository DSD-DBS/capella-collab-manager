# onStartup: 0
"""EASE script to prepare the workspace for read-only Containers.

.. note:
    The module expects that the scripts runs inside the EASE Docker Container.

.. seealso:

    The acronym EASE stands for "Eclipse Advanced Scripting Environment".
    Further information: https://www.eclipse.org/ease/

Environment variables
======

The following environment variables must be set:

* ``GIT_USERNAME`` (if authentication is required)
* ``GIT_PASSWORD`` (if authentication is required)
* ``GIT_ENTRYPOINT`` (optional)

"""
# Standard library:
import os
import pathlib
import typing as t

# 1st party:
import pyease.ease as ease
import pyease.easeexceptions as exp

BOT = ease.BOT

logger = ease.logger
ease.log_to_file(
    log_file_path=os.environ.get(
        "EASE_LOG_LOCATION", ease.workspace_path() / "prepare_workspace.log"
    )
)


def import_git_project_from_folder():
    """Import cloned Git project from folder into Capella workspace."""
    entrypoint = os.environ.get("GIT_ENTRYPOINT", "")
    base_path = pathlib.Path("/home/techuser/model")
    if entrypoint:
        path = (base_path / entrypoint).parent
    else:
        path = base_path
    logger.info(f"Import Git project from folder ('{path}')...")
    BOT.menu("File").menu("Import...").click()
    git_node: t.Any = BOT.tree().getTreeItem("General")
    git_node.select()
    git_node.expand()
    git_node.getNode("Projects from Folder or Archive").doubleClick()
    combo_box: t.Any = BOT.comboBox(0)
    combo_box.setText(str(path))
    ease.click_button_with_label(label="Finish", timeout=60000, interval=500)
    BOT.waitUntil(ease.MenuIsAvailable("File"), 600000, 500)


if __name__ == "__main__":
    ease.log_intro_messages()
    if BOT is None:
        raise exp.EaseNoSWTWorkbenchBotError

    try:
        ease.open_eclipse_perspective("Capella")
        import_git_project_from_folder()
        ease.close_eclipse_view("Console")
        exit_signal = 30
    except Exception:
        logger.exception("An unexpected error occured:")
        exit_signal = 9

    logger.info("Exit Capella.")
    ease.kill_capella_process(exit_signal)
    logger.info("Done.")
