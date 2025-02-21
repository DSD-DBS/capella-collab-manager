# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import logging
import pathlib

from capellacollab.core import models as core_models
from capellacollab.permissions import models as permissions_models
from capellacollab.projects.permissions import (
    injectables as projects_permissions_injectables,
)
from capellacollab.projects.permissions import (
    models as projects_permissions_models,
)
from capellacollab.projects.volumes import crud as projects_volumes_crud
from capellacollab.projects.volumes import models as projects_volumes_models
from capellacollab.sessions import models as sessions_models
from capellacollab.sessions import operators
from capellacollab.sessions.operators import models as operators_models

from . import interface

log = logging.getLogger(__name__)


class ProjectVolumeIntegration(interface.HookRegistration):
    """Mount project volumes into related sessions

    Persistent sessions without provisioning:
    - Mount all shared volumes of projects according to the users or tokens permission.
      If `shared_volumes:UPDATE` is granted, the volume is mounted read-write.
      If `shared_volumes:GET` is granted, the volume is mounted read-only.
      Otherwise, the volume is not mounted.

    Persistent session with provisioning:
    - Same as persistent sessions without provisioning,
      but only consider projects that are part of the provisioning.

    Read-only sessions:
    - Same as persistent sessions with provisioning, but all volumes are mounted read-only.
    """

    def configuration_hook(
        self,
        request: interface.ConfigurationHookRequest,
    ) -> interface.ConfigurationHookResult:
        volumes = self._get_all_project_volumes_with_access(request)

        if request.provisioning:
            volumes = self._filter_volumes_for_provisioning(request, volumes)
        operator_volumes, warnings = (
            self._transform_volumes_to_operator_format(
                request.operator, volumes
            )
        )

        readme_volume = self._create_readme_file(
            request.session_id, request.operator
        )

        return interface.ConfigurationHookResult(
            volumes=[*operator_volumes, readme_volume], warnings=warnings
        )

    def pre_session_termination_hook(
        self,
        request: interface.PreSessionTerminationHookRequest,
    ) -> interface.PreSessionTerminationHookResult:
        request.operator.delete_config_map(
            name=f"{request.session.id}-project-volume-readme"
        )

        return interface.PreSessionTerminationHookResult()

    @classmethod
    def _get_all_project_volumes_with_access(
        cls,
        request: interface.ConfigurationHookRequest,
    ) -> list[tuple[projects_volumes_models.DatabaseProjectVolume, bool]]:
        """Get all project volumes the user / token has access to

        Returns
        -------
        list[tuple[projects_volumes_models.DatabaseProjectVolume, bool]]
            List of volumes with a boolean indicating if the volume should be mounted read-only
        """

        project_volumes = []
        for volume in projects_volumes_crud.get_all_project_volumes(
            request.db
        ):
            project_scope = projects_permissions_injectables.get_scope(
                request.user,
                request.pat,
                request.global_scope,
                volume.project,
                request.db,
            )

            if (
                permissions_models.UserTokenVerb.GET
                not in project_scope.shared_volumes
            ):
                # No access to volume, continue
                continue

            project_volumes.append(
                (volume, cls._is_read_only_mount(request, project_scope))
            )

        return project_volumes

    @classmethod
    def _is_read_only_mount(
        cls,
        request: interface.ConfigurationHookRequest,
        project_scope: projects_permissions_models.ProjectUserScopes,
    ) -> bool:
        return (
            request.session_type == sessions_models.SessionType.READONLY
            or permissions_models.UserTokenVerb.UPDATE
            not in project_scope.shared_volumes
        )

    @classmethod
    def _filter_volumes_for_provisioning(
        cls,
        request: interface.ConfigurationHookRequest,
        volumes: list[
            tuple[projects_volumes_models.DatabaseProjectVolume, bool]
        ],
    ) -> list[tuple[projects_volumes_models.DatabaseProjectVolume, bool]]:
        provisioning_project_slugs = [
            provisioning.project_slug for provisioning in request.provisioning
        ]
        return [
            volume
            for volume in volumes
            if volume[0].project.slug in provisioning_project_slugs
        ]

    def _transform_volumes_to_operator_format(
        self,
        operator: operators.KubernetesOperator,
        volumes: list[
            tuple[projects_volumes_models.DatabaseProjectVolume, bool]
        ],
    ) -> tuple[list[operators_models.Volume], list[core_models.Message]]:
        operator_volumes: list[operators_models.Volume] = []
        warnings: list[core_models.Message] = []

        for volume in volumes:
            if not operator.persistent_volume_exists(volume[0].pvc_name):
                warnings.append(
                    core_models.Message(
                        err_code="PROJECT_FILE_SHARE_VOLUME_NOT_FOUND",
                        title="Project volume not found",
                        reason=(
                            f"The shared volume in the project '{volume[0].project.name}' couldn't be located. "
                            "Please contact your system administrator or recreate the project volume (this will erase all data in the file-share)."
                        ),
                    )
                )
                continue

            operator_volumes.append(
                operators_models.PersistentVolume(
                    name=volume[0].pvc_name,
                    read_only=volume[1],
                    container_path=pathlib.PurePosixPath("/shared")
                    / volume[0].project.slug,
                    volume_name=volume[0].pvc_name,
                    sub_path=None,
                )
            )

        return operator_volumes, warnings

    def _create_readme_file(
        self, session_id: str, operator: operators.KubernetesOperator
    ) -> operators_models.ConfigMapReferenceVolume:
        readme = (
            "Do not create files in this directory directly!"
            "\nFor technical reasons, it's not possible to restrict write access to this directory."
            "\nContent in this directory will not persisted."
            "\nOnly files in `/shared/<project_slug>` and `/workspace` will be persisted, not files directly in `/shared`."
        )

        name = f"{session_id}-project-volume-readme"

        operator.create_config_map(
            name=name,
            data={"README.txt": readme},
        )

        return operators_models.ConfigMapReferenceVolume(
            name=name,
            read_only=True,
            container_path=pathlib.PurePosixPath("/shared") / "README.txt",
            config_map_name=name,
            sub_path="README.txt",
            optional=False,
        )
