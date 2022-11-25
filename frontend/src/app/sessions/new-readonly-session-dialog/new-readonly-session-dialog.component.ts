/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Inject, OnInit } from '@angular/core';
import {
  FormControl,
  FormGroup,
  Validators,
  ValidationErrors,
  ValidatorFn,
  AbstractControl,
  FormArray,
} from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { Router } from '@angular/router';

import { GetGitModel } from 'src/app/projects/project-detail/model-overview/model-detail/git-model.service';
import { Revisions, GitService } from 'src/app/services/git/git.service';
import { Model } from 'src/app/services/model/model.service';
import { Project } from 'src/app/services/project/project.service';
import { SessionService } from 'src/app/services/session/session.service';

@Component({
  selector: 'new-readonly-session-dialog',
  templateUrl: './new-readonly-session-dialog.component.html',
})
export class NewReadonlySessionDialogComponent implements OnInit {
  constructor(
    public sessionService: SessionService,
    private gitService: GitService,
    private router: Router,
    private dialogRef: MatDialogRef<NewReadonlySessionDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: { project: Project; model: Model }
  ) {}

  public filteredRevisions: Revisions = { branches: [], tags: [] };

  public availableRevisions: Revisions | undefined = {
    branches: [],
    tags: [],
  };

  public form = new FormGroup({
    models: new FormArray([]),
  });

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
    [this.data.model, this.data.model].forEach((model) => {
      const primary_git_model = get_primary_git_model(model);
      if (!primary_git_model) {
        return;
      }

      const subgroup = new FormGroup({
        revision: new FormControl({ value: '', disabled: true }, [
          Validators.required,
          this.existingRevisionValidator(),
        ]),
      });

      (this.form.get('models') as FormArray).push(subgroup);

      this.gitService
        .privateRevisions(
          this.data.model.git_models[0].path,
          this.data.project.slug,
          this.data.model.slug,
          this.data.model.git_models[0].id
        )
        .subscribe((revisions) => {
          // TODO: This will become problematic:
          this.availableRevisions = revisions;
          if (revisions) this.filteredRevisions = revisions;

          subgroup.controls.revision.enable();
          subgroup.controls.revision.setValue(
            primary_git_model?.revision || ''
          );
          subgroup.controls.revision.updateValueAndValidity();
        });
    });
  }

  get subforms(): FormArray<FormGroup> {
    return this.form.get('models') as FormArray;
  }

  requestSession(model: Model): void {
    if (!model.version) {
      return;
    }

    /// TODO: Open dialog with model details -> repo & checkout depth

    this.sessionService
      .createReadonlySession(this.data.project.slug, this.data.model.slug)
      .subscribe(() => {
        this.router.navigateByUrl('/');
      });
  }
}

function get_primary_git_model(model: Model): GetGitModel | undefined {
  return model.git_models.find((gm) => gm.primary);
}
