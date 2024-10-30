/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { NgClass, AsyncPipe } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import {
  FormControl,
  FormGroup,
  FormsModule,
  ReactiveFormsModule,
} from '@angular/forms';
import { MatChipsModule } from '@angular/material/chips';
import { MatRipple } from '@angular/material/core';
import {
  MatFormField,
  MatLabel,
  MatSuffix,
} from '@angular/material/form-field';
import { MatIcon } from '@angular/material/icon';
import { MatInput } from '@angular/material/input';
import { RouterLink } from '@angular/router';
import { map, startWith } from 'rxjs';
import { switchMap } from 'rxjs/operators';
import { MatIconComponent } from '../../helpers/mat-icon/mat-icon.component';
import { MatCardOverviewSkeletonLoaderComponent } from '../../helpers/skeleton-loaders/mat-card-overview-skeleton-loader/mat-card-overview-skeleton-loader.component';
import { ProjectWrapperService } from '../service/project.service';

@Component({
  selector: 'app-project-overview',
  templateUrl: './project-overview.component.html',
  standalone: true,
  imports: [
    RouterLink,
    MatRipple,
    MatIconComponent,
    MatCardOverviewSkeletonLoaderComponent,
    NgClass,
    MatIcon,
    AsyncPipe,
    MatFormField,
    MatInput,
    MatLabel,
    MatSuffix,
    ReactiveFormsModule,
    FormsModule,
    MatChipsModule,
  ],
})
export class ProjectOverviewComponent implements OnInit {
  form = new FormGroup({
    search: new FormControl<string>(''),
    projectType: new FormControl<string | null>(null),
  });
  public readonly filteredProjects$ = this.form.valueChanges.pipe(
    startWith(this.form.value),
    switchMap((query) =>
      this.searchAndSortProjects(
        query.search!,
        query?.projectType ?? undefined,
      ),
    ),
  );

  searchAndSortProjects(query: string, projectType?: string) {
    return this.projectService.projects$.pipe(
      map((projects) =>
        projects?.filter((project) => {
          if (projectType) {
            return project.type === projectType;
          }
          return true;
        }),
      ),
      map((projects) =>
        projects?.filter((project) =>
          project.name.toLocaleLowerCase().includes(query.toLocaleLowerCase()),
        ),
      ),
      map((projects) => projects?.sort((a, b) => a.name.localeCompare(b.name))),
    );
  }

  constructor(public projectService: ProjectWrapperService) {}

  ngOnInit() {
    this.projectService.loadProjects();
  }
}
