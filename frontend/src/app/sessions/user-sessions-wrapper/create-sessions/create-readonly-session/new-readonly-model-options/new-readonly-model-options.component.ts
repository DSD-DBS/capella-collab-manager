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

import { Model } from 'src/app/projects/models/service/model.service';
import { GetGitModel } from 'src/app/projects/project-detail/model-overview/model-detail/git-model.service';
import { Revisions, GitService } from 'src/app/services/git/git.service';

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
  styleUrls: ['./new-readonly-model-options.component.css'],
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
    deepClone: new FormControl(false),
  });

  get model(): Model {
    return this.modelOptions!.model;
  }

  get options(): ModelOptions {
    return this.modelOptions!;
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
    const primary_git_model = get_primary_git_model(this.model);
    if (!primary_git_model) {
      return;
    }

    this.form.controls.deepClone.setValue(this.options.deepClone);
    this.form.controls.include.setValue(this.options.include);

    // Okay, this is kinda lame, but I need the modelOptions to be up to date with the form
    this.form.controls.deepClone.valueChanges.subscribe((value) => {
      this.options.deepClone = value || false;
    });
    this.form.controls.include.valueChanges.subscribe((value) => {
      this.options.include = value || false;
    });
    this.form.controls.revision.valueChanges.subscribe((value) =>
      this.filteredRevisionsByPrefix(value as string)
    );

    this.gitService
      .privateRevisions(
        primary_git_model.path,
        this.projectSlug,
        this.model.slug,
        primary_git_model.id
      )
      .subscribe((revisions) => {
        this.availableRevisions = revisions;
        if (revisions) this.filteredRevisions = revisions;

        this.form.controls.revision.enable();
        this.form.controls.revision.setValue(primary_git_model?.revision || '');
        this.form.controls.revision.updateValueAndValidity();
      });
  }

  private filteredRevisionsByPrefix(prefix: string): void {
    this.filteredRevisions = {
      branches: [],
      tags: [],
    };

    if (this.availableRevisions) {
      this.filteredRevisions = {
        branches: this.availableRevisions!.branches.filter((branch) =>
          branch.startsWith(prefix)
        ),
        tags: this.availableRevisions!.tags.filter((tag) =>
          tag.startsWith(prefix)
        ),
      };
    }
  }
}

function get_primary_git_model(model: Model): GetGitModel | undefined {
  return model.git_models.find((gm) => gm.primary);
}
