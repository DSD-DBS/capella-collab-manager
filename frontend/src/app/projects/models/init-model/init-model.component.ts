/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { ProjectService } from 'src/app/services/project/project.service';
import { Model, ModelService } from 'src/app/services/model/model.service';
import { SourceService } from 'src/app/services/source/source.service';
import { combineLatest, filter, map, switchMap, tap } from 'rxjs';
import {
  Tool,
  ToolService,
  ToolType,
  ToolVersion,
} from 'src/app/services/tools/tool.service';

@Component({
  selector: 'app-init-model',
  templateUrl: './init-model.component.html',
  styleUrls: ['./init-model.component.css'],
})
export class InitModelComponent implements OnInit {
  @Output() create = new EventEmitter<{ created: boolean; again?: boolean }>();
  @Input() asStepper?: boolean;

  toolVersions: ToolVersion[] = [];
  toolTypes: ToolType[] = [];

  constructor(
    public projectService: ProjectService,
    public modelService: ModelService,
    public sourceService: SourceService,
    public toolService: ToolService
  ) {}

  public form = new FormGroup({
    version: new FormControl(-1, Validators.required),
    type: new FormControl(-1, Validators.required),
  });

  ngOnInit(): void {
    this.modelService._model
      .pipe(filter(Boolean))
      .pipe(
        tap((model) => {
          if (model.version) {
            this.form.controls.version.patchValue(model.version.id);
          }
          if (model.type) {
            this.form.controls.type.patchValue(model.type.id);
          }
        }),
        map((model: Model) => model.tool),
        switchMap((tool: Tool) =>
          combineLatest([
            this.toolService.getVersionsForTool(tool.id),
            this.toolService.getTypesForTool(tool.id),
          ])
        )
      )
      .subscribe((result: [ToolVersion[], ToolType[]]) => {
        this.toolVersions = result[0];
        this.toolTypes = result[1];
      });
  }

  onSubmit(): void {
    if (
      this.form.valid &&
      this.modelService.model &&
      this.projectService.project &&
      this.form.value.version &&
      this.form.value.type
    ) {
      this.modelService
        .setToolDetailsForModel(
          this.projectService.project.slug,
          this.modelService.model.slug,
          this.form.value.version,
          this.form.value.type
        )
        .subscribe((_) => {
          this.create.emit({ created: true });
        });
    }
  }

  getTool(): Tool {
    let tool = this.toolService.tools!.filter((tool) => {
      return tool.id == this.modelService.model?.tool_id;
    })[0];
    return tool || ({} as Tool);
  }

  getForToolId<Type>(nested_list: { [id: number]: Type[] } | null): Type[] {
    let tool_id: number | null | undefined = this.modelService.model?.tool_id;
    if (tool_id && nested_list) {
      return nested_list[tool_id];
    }
    return [];
  }
}
