/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

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
import {
  Project,
  ProjectService,
} from 'src/app/services/project/project.service';
import {
  Model,
  ModelService,
  NewModel,
} from 'src/app/services/model/model.service';
import { ToolService } from 'src/app/services/tools/tool.service';
import { connectable, filter, first, single, Subject, switchMap } from 'rxjs';

@Component({
  selector: 'app-create-model-base',
  templateUrl: './create-model-base.component.html',
  styleUrls: ['./create-model-base.component.css'],
})
export class CreateModelBaseComponent implements OnInit {
  public form = new FormGroup({
    name: new FormControl('', Validators.required),
    description: new FormControl(''),
    tool_id: new FormControl(-1, Validators.required),
  });

  constructor(
    private modelService: ModelService,
    public projectService: ProjectService,
    public toolService: ToolService,
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
    this.modelService._models.pipe(filter(Boolean)).subscribe((models) => {
      this.form.controls.name.addValidators(
        this.slugValidator(models.map((model) => model.slug))
      );
    });
  }

  onSubmit(): void {
    if (this.form.valid && this.projectService.project!.slug) {
      let new_model = this.form.value as NewModel;

      const modelConnectable = connectable<Model>(
        this.modelService.createNewModel(
          this.projectService.project!.slug,
          new_model
        ),
        {
          connector: () => new Subject(),
          resetOnDisconnect: false,
        }
      );

      modelConnectable.subscribe((model) => {
        this.router.navigate([
          'project',
          this.projectService.project!.slug,
          'model',
          model.slug,
          'choose-source',
        ]);
      });

      modelConnectable
        .pipe(
          switchMap((_) =>
            this.modelService.list(this.projectService.project!.slug)
          )
        )
        .subscribe((value) => {
          this.modelService._models.next(value);
        });

      modelConnectable.connect();
    }
  }
}
