// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { Component, OnInit } from '@angular/core';
import {
  AbstractControl,
  FormControl,
  FormGroup,
  ValidationErrors,
  Validators,
} from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { merge, Observable } from 'rxjs';
import { ProjectService } from 'src/app/projects/service/project.service';
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
  validateCredentials = (
    control: AbstractControl
  ): Observable<ValidationErrors | null> => {
    let credentials = control.value as Credentials;

    return new Observable<ValidationErrors | null>((subscriber) => {
      setTimeout(() => {
        if ((control.value as Credentials) === credentials) {
          this.gitService.fetch('', credentials).subscribe({
            next: (instance) => {
              this.filteredRevisions = instance;
              subscriber.next(null);
              subscriber.complete();
            },
            error: (e) => {
              this.filteredRevisions = { branches: [], tags: [] };
              subscriber.next({ credentials: { value: e.name } });
              subscriber.complete();
            },
          });
        }
      }, 500);
    });
  };

  public gitForm = new FormGroup({
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
    private route: ActivatedRoute,
    public projectService: ProjectService,
    public modelService: ModelService,
    private gitService: GitService,
    private sourceService: SourceService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.route.params.subscribe((params) => {
      this.modelService.init(params.project, params.model).subscribe();
    });

    this.gitForm.controls.revision.valueChanges.subscribe((value) => {
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

  createDependency(
    form: FormGroup,
    sources: string[],
    targets: string[]
  ): void {
    merge(
      ...sources.map((field) => form.controls[field].valueChanges)
    ).subscribe((_) => {
      if (sources.map((field) => form.get(field)?.valid).every(Boolean)) {
        targets.forEach((field) => form.controls[field].enable());
      } else {
        targets.forEach((field) => form.controls[field].disable());
      }
    });
  }

  chainDependencies(form: FormGroup, ...chain: string[][]) {
    for (let i = 0; i < chain.length - 1; i++) {
      this.createDependency(form, chain[i], chain[i + 1]);
    }
  }

  onRevisionFocus(): void {
    this.gitService
      .fetch('', this.gitForm.controls.credentials.value as Credentials)
      .subscribe((instance) => {
        this.filteredRevisions = instance;
      });
  }

  onSubmit(): void {
    if (
      this.projectService.project &&
      this.modelService.model &&
      this.gitForm.valid
    ) {
      let form_result = this.gitForm.value;
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
          this.router.navigate([
            '/init-model',
            this.projectService.project?.slug,
            this.modelService.model?.slug,
          ]);
        });
    }
  }
}
