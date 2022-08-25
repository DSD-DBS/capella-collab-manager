// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import {
  Component,
  EventEmitter,
  Input,
  OnDestroy,
  OnInit,
  Output,
} from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { ProjectService } from 'src/app/services/project/project.service';
import { ModelService } from 'src/app/services/model/model.service';
import { SourceService } from 'src/app/services/source/source.service';
import {
  Tool,
  ToolService,
  Type,
  Version,
} from 'src/app/services/tools/tool.service';
import { filter, forkJoin, map, Subscription } from 'rxjs';

@Component({
  selector: 'app-init-model',
  templateUrl: './init-model.component.html',
  styleUrls: ['./init-model.component.css'],
})
export class InitModelComponent implements OnInit, OnDestroy {
  @Output() create = new EventEmitter<{ created: boolean; again?: boolean }>();
  @Input() as_stepper?: boolean;
  tool?: Tool;
  versions?: Version[];
  types?: Type[];

  tool_subscription?: Subscription;
  types_subscription?: Subscription;
  versions_subscription?: Subscription;

  constructor(
    public projectService: ProjectService,
    public modelService: ModelService,
    public sourceService: SourceService,
    public toolService: ToolService
  ) {}

  public form = new FormGroup({
    version: new FormControl('', Validators.required),
    type: new FormControl('', Validators.required),
  });

  ngOnInit(): void {
    this.modelService._model.pipe(filter(Boolean)).subscribe((model) => {
      this.form.controls.version.patchValue(model.version_id);
      this.form.controls.type.patchValue(model.type_id);
    });
    this.toolService.get_tools().subscribe(this.toolService._tools);
    this.toolService.get_versions().subscribe(this.toolService._versions);
    this.toolService.get_types().subscribe(this.toolService._types);

    this.tool_subscription = forkJoin([
      this.modelService._model.pipe(filter(Boolean)),
      this.toolService._tools.pipe(filter(Boolean)),
    ])
      .pipe(
        map((value) => {
          let [model, tools] = value;
          return tools.filter((tool) => model.tool_id == tool.id)[0];
        })
      )
      .subscribe((tool) => {
        this.tool = tool;
      });

    this.types_subscription = forkJoin([
      this.modelService._model.pipe(filter(Boolean)),
      this.toolService._types.pipe(filter(Boolean)),
    ])
      .pipe(
        map((value) => {
          let [model, types] = value;
          return types.filter((type) => type.tool_id === model.tool_id);
        })
      )
      .subscribe((types) => {
        this.types = types;
      });

    this.versions_subscription = forkJoin([
      this.modelService._model.pipe(filter(Boolean)),
      this.toolService._versions.pipe(filter(Boolean)),
    ])
      .pipe(
        map((value) => {
          let [model, versions] = value;
          return versions.filter(
            (version) => version.tool_id === model.tool_id
          );
        })
      )
      .subscribe((versions) => {
        this.versions = versions;
      });
  }

  ngOnDestroy(): void {
    this.tool_subscription?.unsubscribe();
    this.types_subscription?.unsubscribe();
    this.versions_subscription?.unsubscribe();
  }

  onSubmit(again: boolean): void {
    if (
      this.form.valid &&
      this.modelService.model &&
      this.projectService.project
    ) {
      this.modelService
        .setToolDetailsForModel(
          this.projectService.project.slug,
          this.modelService.model.slug,
          this.form.value.version,
          this.form.value.type
        )
        .subscribe((_) => {
          this.create.emit({ created: true, again: again });
        });
    }
  }

  getTool(): Tool {
    let tool = this.toolService.tools?.filter((tool) => {
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
