/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { NgIf, NgFor } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import {
  AbstractControl,
  AsyncValidatorFn,
  FormBuilder,
  ValidationErrors,
  Validators,
  FormsModule,
  ReactiveFormsModule,
} from '@angular/forms';
import { MatButton } from '@angular/material/button';
import { MatOption } from '@angular/material/core';
import { MatDialog } from '@angular/material/dialog';
import { MatFormField, MatLabel } from '@angular/material/form-field';
import { MatIcon } from '@angular/material/icon';
import { MatSelect } from '@angular/material/select';
import { RouterLink } from '@angular/router';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { NgxSkeletonLoaderModule } from 'ngx-skeleton-loader';
import { combineLatest, filter, map, Observable, take, tap } from 'rxjs';
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
  ToolVersionWithTool,
} from 'src/app/settings/core/tools-settings/tool.service';
import { CreateReadonlySessionDialogComponent } from '../../create-sessions/create-readonly-session/create-readonly-session-dialog.component';

@UntilDestroy()
@Component({
  selector: 'app-create-readonly-session',
  templateUrl: './create-readonly-session.component.html',
  styleUrls: ['./create-readonly-session.component.css'],
  standalone: true,
  imports: [
    FormsModule,
    ReactiveFormsModule,
    NgIf,
    NgFor,
    NgxSkeletonLoaderModule,
    MatFormField,
    MatLabel,
    MatSelect,
    MatOption,
    MatButton,
    MatIcon,
    RouterLink,
  ],
})
export class CreateReadonlySessionComponent implements OnInit {
  projectSlug?: string;
  models?: ModelWithCompatibility[];

  relevantToolVersions?: ToolVersion[];
  allToolVersions?: ToolVersionWithTool[];

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
    this.projectService.project$
      .pipe(untilDestroyed(this), filter(Boolean))
      .subscribe((project) => (this.projectSlug = project.slug));

    this.loadToolsAndModels().subscribe(([models, allVersions]) => {
      this.resolveVersionCompatibility(models, allVersions);
    });

    this.userSessionService.loadSessions();
  }

  loadToolsAndModels(): Observable<[Model[], ToolVersionWithTool[]]> {
    return combineLatest([
      this.modelService.models$.pipe(untilDestroyed(this), filter(Boolean)),
      this.toolService.getVersionsForTools(),
    ]).pipe(
      tap(([_, versions]) => {
        this.allToolVersions = versions;
      }),
    );
  }

  resolveVersionCompatibility(
    models: Model[],
    allVersions: ToolVersionWithTool[],
  ): void {
    this.models = [];

    for (const model of models) {
      if (!model.version) {
        continue;
      }
      const extendedModel = model as ModelWithCompatibility;
      extendedModel.compatibleVersions = [
        this.findVersionByID(model.version!.id, allVersions)!,
      ];

      for (const version of allVersions!) {
        if (version.config.compatible_versions.includes(model.version!.id)) {
          extendedModel.compatibleVersions.push(version);
        }
      }

      this.models?.push(extendedModel);
    }
  }

  findVersionByID(id: number, allVersions: ToolVersionWithTool[]) {
    return allVersions.find((v) => v.id === id);
  }

  get tools(): Tool[] | undefined {
    if (this.models === undefined) {
      return undefined;
    }
    return this.removesToolDuplicates(
      this.models
        ?.map((m) => m.compatibleVersions.map((version) => version.tool))
        .flat(),
    );
  }

  removesToolDuplicates(tools: Tool[]): Tool[] {
    return tools.filter(
      (value, index, self) =>
        index === self.findIndex((tool) => tool.id === value.id),
    );
  }

  requestReadonlySession(): void {
    if (this.toolSelectionForm.valid) {
      const dialogRef = this.dialog.open(CreateReadonlySessionDialogComponent, {
        data: {
          projectSlug: this.projectSlug,
          models: this.models?.filter((model) =>
            this.isCompatibleWithSelectedVersion(model),
          ),
          toolVersion: this.toolSelectionForm.value.version,
          tool: this.toolSelectionForm.value.tool,
        },
      });

      dialogRef
        .afterClosed()
        .subscribe(() => this.userSessionService.loadSessions());
    }
  }

  isCompatibleWithSelectedVersion(model: ModelWithCompatibility): boolean {
    return (
      model.compatibleVersions.findIndex(
        (version) => this.toolSelectionForm.value.version!.id === version.id,
      ) !== -1
    );
  }

  onToolChange(tool: Tool): void {
    this.toolSelectionForm.controls.version.enable();
    this.toolSelectionForm.controls.version.patchValue(null);

    this.relevantToolVersions = this.removeVersionDuplicates(
      this.models
        ?.map((m) => m.compatibleVersions)
        .flat()
        .filter((v) => v.tool.id === tool.id),
    );
  }

  removeVersionDuplicates(
    versions: ToolVersionWithTool[] | undefined,
  ): ToolVersionWithTool[] | undefined {
    if (versions === undefined) {
      return undefined;
    }
    return versions.filter(
      (value, index, self) =>
        index === self.findIndex((version) => version.id === value.id),
    );
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

type ModelWithCompatibility = {
  compatibleVersions: ToolVersionWithTool[];
} & Model;
