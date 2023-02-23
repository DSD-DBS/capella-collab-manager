/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Input, OnInit } from '@angular/core';
import { Validators, FormBuilder } from '@angular/forms';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { filter } from 'rxjs';
import {
  getPrimaryGitModel,
  Model,
} from 'src/app/projects/models/service/model.service';
import { GetGitModel } from 'src/app/projects/project-detail/model-overview/model-detail/git-model.service';
import { Revisions, GitService } from 'src/app/services/git/git.service';

export type ModelOptions = {
  model: Model;
  primaryGitModel: GetGitModel;
  include: boolean;
  revision: string;
  deepClone: boolean;
};

@UntilDestroy()
@Component({
  selector: 'create-readonly-model-options',
  templateUrl: './create-readonly-model-options.component.html',
  styleUrls: ['./create-readonly-model-options.component.css'],
})
export class CreateReadonlyModelOptionsComponent implements OnInit {
  @Input() projectSlug!: string;
  @Input() modelOptions!: ModelOptions;

  constructor(private gitService: GitService, private fb: FormBuilder) {}

  private revision?: Revisions;
  public filteredRevisions?: Revisions;

  public form = this.fb.group({
    include: this.fb.control(true),
    revision: this.fb.control('', {
      validators: Validators.required,
      asyncValidators: this.gitService.asyncExistingRevisionValidator(),
    }),
    deepClone: this.fb.control(false),
  });

  get model(): Model {
    return this.modelOptions!.model;
  }

  ngOnInit(): void {
    const primaryGitModel = getPrimaryGitModel(this.model);
    if (!primaryGitModel) {
      return;
    }

    this.form.controls.deepClone.setValue(this.modelOptions.deepClone);
    this.form.controls.include.setValue(this.modelOptions.include);

    // Okay, this is kinda lame, but I need the modelOptions to be up to date with the form
    this.form.controls.deepClone.valueChanges.subscribe((value) => {
      this.modelOptions.deepClone = value || false;
    });
    this.form.controls.include.valueChanges.subscribe((value) => {
      this.modelOptions.include = value || false;
    });

    this.gitService.revisions
      .pipe(untilDestroyed(this), filter(Boolean))
      .subscribe({
        next: (revisions) => {
          this.revision = revisions;
          this.filteredRevisions = revisions;

          this.form.controls.revision.enable();
          this.form.controls.revision.setValue(primaryGitModel?.revision || '');
          this.form.controls.revision.updateValueAndValidity();
        },
        complete: () => this.gitService.clearRevision(),
      });

    this.gitService.loadPrivateRevisions(
      primaryGitModel.path,
      this.projectSlug,
      this.model.slug,
      primaryGitModel.id
    );
  }

  filterRevisionsByPrefix(prefix: string): void {
    if (!this.revision) {
      this.filteredRevisions = undefined;
      return;
    }

    this.filteredRevisions = {
      branches: this.revision!.branches.filter((branch) =>
        branch.toLowerCase().startsWith(prefix.toLowerCase())
      ),
      tags: this.revision!.tags.filter((tag) =>
        tag.toLowerCase().startsWith(prefix.toLowerCase())
      ),
    };
  }
}
