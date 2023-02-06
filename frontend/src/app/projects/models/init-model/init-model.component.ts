/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import {
  Component,
  EventEmitter,
  Input,
  OnDestroy,
  OnInit,
  Output,
} from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { combineLatest, filter, map, Subscription, switchMap, tap } from 'rxjs';
import {
  Model,
  ModelService,
} from 'src/app/projects/models/service/model.service';
import {
  Tool,
  ToolService,
  ToolNature,
  ToolVersion,
} from 'src/app/settings/core/tools-settings/tool.service';
import { GitModelService } from '../../project-detail/model-overview/model-detail/git-model.service';
import { ProjectService } from '../../service/project.service';

@Component({
  selector: 'app-init-model',
  templateUrl: './init-model.component.html',
  styleUrls: ['./init-model.component.css'],
})
export class InitModelComponent implements OnInit, OnDestroy {
  @Output() create = new EventEmitter<{ created: boolean }>();
  @Input() asStepper?: boolean;

  toolVersions: ToolVersion[] = [];
  toolNatures: ToolNature[] = [];

  buttonDisabled: boolean = false;

  private modelSubscription?: Subscription;

  constructor(
    public projectService: ProjectService,
    public modelService: ModelService,
    public gitModelService: GitModelService,
    public toolService: ToolService
  ) {}

  public form = new FormGroup({
    version: new FormControl<number | undefined>(
      undefined,
      Validators.required
    ),
    nature: new FormControl<number | undefined>(undefined, Validators.required),
  });

  ngOnInit(): void {
    this.modelSubscription = this.modelService._model
      .pipe(filter(Boolean))
      .pipe(
        tap((model) => {
          if (model.version) {
            this.form.controls.version.patchValue(model.version.id);
          }
          if (model.nature) {
            this.form.controls.nature.patchValue(model.nature.id);
          }
        }),
        map((model: Model) => model.tool),
        switchMap((tool: Tool) =>
          combineLatest([
            this.toolService.getVersionsForTool(tool.id),
            this.toolService.getNaturesForTool(tool.id),
          ])
        )
      )
      .subscribe((result: [ToolVersion[], ToolNature[]]) => {
        this.toolVersions = result[0];
        this.toolNatures = result[1];
      });
  }

  ngOnDestroy(): void {
    this.modelSubscription?.unsubscribe();
  }

  onSubmit(): void {
    if (
      this.form.valid &&
      this.modelService.model &&
      this.projectService.project
    ) {
      this.modelService
        .setToolDetailsForModel(
          this.projectService.project.slug,
          this.modelService.model.slug,
          this.form.value.version!,
          this.form.value.nature!
        )
        .subscribe((_) => {
          this.create.emit({ created: true });
          this.buttonDisabled = true;
        });
    }
  }
}
