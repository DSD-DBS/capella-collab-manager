/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnInit } from '@angular/core';
import {
  AbstractControl,
  AsyncValidatorFn,
  FormBuilder,
  ValidationErrors,
  Validators,
} from '@angular/forms';
import { MatDialog } from '@angular/material/dialog';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { filter, map, Observable, take } from 'rxjs';
import {
  Model,
  ModelService,
} from 'src/app/projects/models/service/model.service';
import { ProjectService } from 'src/app/projects/service/project.service';
import { UserSessionService } from 'src/app/sessions/service/user-session.service';
import {
  Tool,
  ToolService,
  ToolVersion,
} from 'src/app/settings/core/tools-settings/tool.service';
import { CreateReadonlySessionDialogComponent } from '../../create-sessions/create-readonly-session/create-readonly-session-dialog.component';

@UntilDestroy()
@Component({
  selector: 'app-create-readonly-session',
  templateUrl: './create-readonly-session.component.html',
  styleUrls: ['./create-readonly-session.component.css'],
})
export class CreateReadonlySessionComponent implements OnInit {
  projectSlug?: string;
  models?: Model[];

  toolVersions?: ToolVersion[];

  public toolSelectionForm = this.fb.group(
    {
      tool: this.fb.control<Tool | null>(null, Validators.required),
      version: this.fb.control<ToolVersion | null>(
        { value: null, disabled: true },
        Validators.required,
      ),
    },
    { asyncValidators: this.asyncReadonlyValidator() },
  );

  constructor(
    public toolService: ToolService,
    private userSessionService: UserSessionService,
    private projectService: ProjectService,
    private modelService: ModelService,
    private dialog: MatDialog,
    private fb: FormBuilder,
  ) {}

  ngOnInit(): void {
    this.modelService.models$
      .pipe(untilDestroyed(this), filter(Boolean))
      .subscribe((models) => (this.models = models));

    this.projectService.project$
      .pipe(untilDestroyed(this), filter(Boolean))
      .subscribe((project) => (this.projectSlug = project.slug));

    this.userSessionService.loadSessions();
    this.toolService.getTools().subscribe();
  }

  get tools(): Tool[] | undefined {
    if (this.models === undefined || this.toolService.tools === undefined) {
      return undefined;
    }
    const toolIds = this.models.map((m) => m.tool.id);
    return this.toolService.tools.filter((t) => toolIds?.includes(t.id));
  }

  requestReadonlySession(): void {
    if (this.toolSelectionForm.valid) {
      const dialogRef = this.dialog.open(CreateReadonlySessionDialogComponent, {
        data: {
          projectSlug: this.projectSlug,
          models: this.models,
          modelVersionId: this.toolSelectionForm.value.version!.id,
        },
      });

      dialogRef
        .afterClosed()
        .subscribe(() => this.userSessionService.loadSessions());
    }
  }

  onToolChange(tool: Tool): void {
    this.toolSelectionForm.controls.version.enable();
    this.toolSelectionForm.controls.version.patchValue(null);
    this.toolVersions = undefined;

    this.toolService.getVersionsForTool(tool.id).subscribe((toolVersions) => {
      const toolVersionIds = this.models?.map((m) => m.version?.id);
      this.toolVersions = toolVersions.filter(
        (v) => toolVersionIds?.includes(v.id),
      );
    });
  }

  asyncReadonlyValidator(): AsyncValidatorFn {
    return (_: AbstractControl): Observable<ValidationErrors | null> => {
      return this.userSessionService.readonlySessions$.pipe(
        take(1),
        map((readOnlySessions) => {
          return readOnlySessions?.find(
            (session) =>
              session.project?.slug === this.projectSlug &&
              session.version?.id ===
                this.toolSelectionForm.value.version!.id &&
              session.version?.tool.id ===
                this.toolSelectionForm.value.tool!.id,
          )
            ? {
                uniqueReadonlySession:
                  'Readonly session with these settings already exists',
              }
            : null;
        }),
      );
    };
  }
}
