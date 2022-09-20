/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
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
  public gitForm = new FormGroup({
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
    private sourceService: SourceService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.gitForm.controls.revision.valueChanges.subscribe((value) => {
      if (!this.gitService.instance) {
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
      .fetch('', this.gitForm.controls.credentials.value as Credentials)
      .subscribe((instance) => {
        this.filteredRevisions = instance;
      });
  }

  onSubmit(): void {
    if (this.gitForm.valid) {
      let source: Source = {
        path: this.gitForm.value.credentials!.path!,
        username: this.gitForm.value.credentials!.username || '',
        password: this.gitForm.value.credentials!.password || '',
        revision: this.gitForm.value.revision!,
        entrypoint: this.gitForm.value.entrypoint || '',
      };
      combineLatest([
        this.projectService._project.pipe(
          filter(Boolean),
          map((project) => project.name)
        ),
        this.modelService._model.pipe(
          filter(Boolean),
          map((model) => model.slug)
        ),
      ])
        .pipe(
          switchMap((args) => this.sourceService.addGitSource(...args, source))
        )
        .subscribe((_) => {
          this.router.navigate([
            'project',
            this.projectService.project!.slug,
            'model',
            this.modelService.model?.slug,
            'init-model',
          ]);
        });
    }
  }
}
