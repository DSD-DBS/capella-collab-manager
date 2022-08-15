// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { Component, OnInit } from '@angular/core';
import {
  AbstractControl,
  FormControl,
  FormGroup,
  ValidationErrors,
  ValidatorFn,
  Validators,
} from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import slugify from 'slugify';
import { ProjectService } from 'src/app/projects/service/project.service';
import { ModelService, NewModel } from 'src/app/services/model/model.service';
import { ToolService } from 'src/app/services/tools/tool.service';

@Component({
  selector: 'app-create-model',
  templateUrl: './create-model.component.html',
  styleUrls: ['./create-model.component.css'],
})
export class CreateModelComponent implements OnInit {
  public form = new FormGroup({
    name: new FormControl('', Validators.required),
    description: new FormControl(''),
    tool_id: new FormControl('', Validators.required),
  });

  constructor(
    private modelService: ModelService,
    public projectService: ProjectService,
    public toolService: ToolService,
    private route: ActivatedRoute,
    private router: Router
  ) {}

  slugValidator(slugs: string[]): ValidatorFn {
    return (control: AbstractControl): ValidationErrors | null => {
      let new_slug = slugify(control.value, { lower: true });
      for (let slug of slugs) {
        if (slug == new_slug) {
          return { uniqueSlug: { value: slug } };
        }
      }
      return null;
    };
  }

  ngOnInit(): void {
    this.toolService.get_tools().subscribe();
    this.route.params.subscribe((params) => {
      this.modelService.initAll(params.project).subscribe((models) => {
        this.form.controls.name.addValidators(
          this.slugValidator(models.map((value) => value.slug))
        );
      });
    });
  }

  onSubmit(): void {
    if (this.form.valid && this.projectService.project?.slug) {
      let new_model = this.form.value as NewModel;
      this.modelService
        .createNew(this.projectService.project?.slug, new_model)
        .subscribe((result) => {
          this.router.navigate([
            '/choose-source',
            this.projectService.project?.slug,
            result.slug,
          ]);
        });
      this.modelService.list(this.projectService.project.slug).subscribe();
    }
  }
}
