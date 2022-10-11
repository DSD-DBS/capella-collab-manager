/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

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
import { filter, switchMap, map, combineLatest } from 'rxjs';

@Component({
  selector: 'app-create-coworking-method',
  templateUrl: './create-coworking-method.component.html',
  styleUrls: ['./create-coworking-method.component.css'],
})
export class CreateCoworkingMethodComponent implements OnInit {
  @Output() create = new EventEmitter<boolean>();

  public form = new FormGroup({
    credentials: new FormGroup({
      path: new FormControl('', Validators.required),
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
      if (this.gitService.instance == null) {
        this.filteredRevisions = { branches: [], tags: [] };
      } else {
        this.filteredRevisions = {
          branches: this.gitService.instance.branches.filter((branch) =>
            branch.startsWith(value as string)
          ),
          tags: this.gitService.instance.tags.filter((tag) =>
            tag.startsWith(value as string)
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
      this.form.valid &&
      this.projectService.project != null &&
      this.modelService.model != null
    ) {
      const source: Source = {
        path: this.form.value.credentials!.path!,
        username: this.form.value.credentials!.username || '',
        password: this.form.value.credentials!.password || '',
        revision: this.form.value.revision!,
        entrypoint: this.form.value.entrypoint || '',
      };
      this.sourceService
        .addGitSource(
          this.projectService.project.name,
          this.modelService.model.slug,
          source
        )
        .subscribe((_) => {
          this.create.emit(true);
        });
    }
  }
}
