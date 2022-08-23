// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { Component, EventEmitter, OnInit, Output } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { ProjectService } from 'src/app/services/project/project.service';
import {
  Credentials,
  GitService,
  Instance,
} from 'src/app/services/git/git.service';
import { ModelService } from 'src/app/services/model/model.service';
import { Source, SourceService } from 'src/app/services/source/source.service';

@Component({
  selector: 'app-create-coworking-method',
  templateUrl: './create-coworking-method.component.html',
  styleUrls: ['./create-coworking-method.component.css'],
})
export class CreateCoworkingMethodComponent implements OnInit {
  @Output() create = new EventEmitter<boolean>();

  public form = new FormGroup({
    credentials: new FormGroup({
      url: new FormControl('', Validators.required),
      username: new FormControl(''),
      password: new FormControl(''),
    }),
    revision: new FormControl('', Validators.required),
    entrypoint: new FormControl('/'),
  });

  public filteredRevisions: Instance = { branches: [], tags: [] };

  constructor(
    public projectService: ProjectService,
    public modelService: ModelService,
    private gitService: GitService,
    private sourceService: SourceService
  ) {}

  ngOnInit(): void {
    this.form.controls.revision.valueChanges.subscribe((value) => {
      if (!this.gitService.instance) {
        this.filteredRevisions = { branches: [], tags: [] };
      } else {
        this.filteredRevisions = {
          branches: this.gitService.instance.branches.filter((branch) =>
            branch.startsWith(value)
          ),
          tags: this.gitService.instance.tags.filter((tag) =>
            tag.startsWith(value)
          ),
        };
      }
    });
  }

  onRevisionFocus(): void {
    this.gitService
      .fetch('', this.form.controls.credentials.value as Credentials)
      .subscribe((instance) => {
        this.filteredRevisions = instance;
      });
  }

  onSubmit(): void {
    if (
      this.projectService.project &&
      this.modelService.model &&
      this.form.valid
    ) {
      let form_result = this.form.value;
      let source: Source = {
        path: form_result.credentials.url,
        entrypoint: form_result.entrypoint,
        revision: form_result.revision,
        username: form_result.credentials.username,
        password: form_result.credentials.password,
      };
      this.sourceService
        .addGitSource(
          this.projectService.project.slug,
          this.modelService.model.slug,
          source
        )
        .subscribe((_) => {
          this.create.emit(true);
        });
    }
  }
}
