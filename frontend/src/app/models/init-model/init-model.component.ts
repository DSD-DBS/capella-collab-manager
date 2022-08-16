// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { ProjectService } from 'src/app/services/project/project.service';
import { ModelService } from 'src/app/services/model/model.service';
import { SourceService } from 'src/app/services/source/source.service';
import { Tool, ToolService } from 'src/app/services/tools/tool.service';

@Component({
  selector: 'app-init-model',
  templateUrl: './init-model.component.html',
  styleUrls: ['./init-model.component.css'],
})
export class InitModelComponent implements OnInit {
  constructor(
    public projectService: ProjectService,
    public modelService: ModelService,
    public sourceService: SourceService,
    public toolService: ToolService,
    private route: ActivatedRoute,
    private router: Router
  ) {}

  public form = new FormGroup({
    version: new FormControl('', Validators.required),
    type: new FormControl('', Validators.required),
  });

  ngOnInit(): void {
    this.route.params.subscribe((params) => {
      this.modelService
        .init(params.project, params.model)
        .subscribe((model) => {
          this.form.controls.version.patchValue(model.version_id);
          this.form.controls.type.patchValue(model.type_id);
        });
      this.toolService.init();
    });
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
          this.form.value.version,
          this.form.value.type
        )
        .subscribe((_) => {
          this.router.navigate(['/project', this.projectService.project?.slug]);
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
