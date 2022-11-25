/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Input, OnInit } from '@angular/core';
import {
  FormControl,
  FormGroup,
  Validators,
  ValidationErrors,
  ValidatorFn,
  AbstractControl,
} from '@angular/forms';

import { GetGitModel } from 'src/app/projects/project-detail/model-overview/model-detail/git-model.service';
import { Revisions, GitService } from 'src/app/services/git/git.service';
import { Model } from 'src/app/services/model/model.service';

export type ModelOptions = {
  model: Model;
  primary_git_model: GetGitModel;
  include: boolean;
  revision: string;
  deepClone: boolean;
};

@Component({
  selector: 'new-readonly-model-options',
  templateUrl: './new-readonly-model-options.component.html',
})
export class NewReadonlyModelOptionsComponent implements OnInit {
  @Input() projectSlug = '';
  @Input() modelOptions: ModelOptions | undefined;

  constructor(private gitService: GitService) {}

  public filteredRevisions: Revisions = { branches: [], tags: [] };

  public availableRevisions: Revisions | undefined = {
    branches: [],
    tags: [],
  };

  public form = new FormGroup({
    include: new FormControl(true),
    revision: new FormControl({ value: '', disabled: true }, [
      Validators.required,
      this.existingRevisionValidator(),
    ]),
  });

  get model(): Model {
    return this.modelOptions!.model;
  }

  private existingRevisionValidator(): ValidatorFn {
    return (controls: AbstractControl): ValidationErrors | null => {
      let value: string = controls.value;
      if (!value) return null;

      if (
        this.availableRevisions?.branches.includes(value) ||
        this.availableRevisions?.tags.includes(value)
      ) {
        return null;
      }

      return {
        revisionNotFoundError: `${value} does not exist`,
      };
    };
  }

  ngOnInit(): void {
    const model = this.model;
    const primary_git_model = get_primary_git_model(model);
    if (!primary_git_model) {
      return;
    }

    this.gitService
      .privateRevisions(
        model.git_models[0].path,
        this.projectSlug,
        model.slug,
        model.git_models[0].id
      )
      .subscribe((revisions) => {
        this.availableRevisions = revisions;
        if (revisions) this.filteredRevisions = revisions;

        this.form.controls.revision.enable();
        this.form.controls.revision.setValue(primary_git_model?.revision || '');
        this.form.controls.revision.updateValueAndValidity();
      });
  }
}

function get_primary_git_model(model: Model): GetGitModel | undefined {
  return model.git_models.find((gm) => gm.primary);
}
