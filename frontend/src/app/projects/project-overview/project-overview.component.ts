/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { NgIf, NgFor, NgClass, AsyncPipe } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormControl, FormsModule, ReactiveFormsModule } from '@angular/forms';
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
  styleUrls: ['./project-overview.component.css'],
  standalone: true,
  imports: [
    RouterLink,
    MatRipple,
    MatIconComponent,
    MatCardOverviewSkeletonLoaderComponent,
    NgIf,
    NgFor,
    NgClass,
    MatIcon,
    AsyncPipe,
    MatFormField,
    MatInput,
    MatLabel,
    MatSuffix,
    ReactiveFormsModule,
    FormsModule,
  ],
})
export class ProjectOverviewComponent implements OnInit {
  searchControl = new FormControl('');
  public readonly filteredProjects$ = this.searchControl.valueChanges.pipe(
    startWith(''),
    switchMap((query) => this.searchAndSortProjects(query!)),
  );

  searchAndSortProjects(query: string) {
    return this.projectService.projects$.pipe(
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
