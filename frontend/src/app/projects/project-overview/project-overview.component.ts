/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { NgClass, AsyncPipe } from '@angular/common';
import {
  Component,
  ElementRef,
  OnInit,
  QueryList,
  ViewChildren,
  inject,
} from '@angular/core';
import {
  FormControl,
  FormGroup,
  FormsModule,
  ReactiveFormsModule,
} from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
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
import { filter, switchMap } from 'rxjs/operators';
import { TagDisplayComponent } from 'src/app/helpers/tag-display/tag-display.component';
import { Project } from 'src/app/openapi';
import { MatIconComponent } from '../../helpers/mat-icon/mat-icon.component';
import { MatCardOverviewSkeletonLoaderComponent } from '../../helpers/skeleton-loaders/mat-card-overview-skeleton-loader/mat-card-overview-skeleton-loader.component';
import {
  getProjectTags,
  ProjectWrapperService,
} from '../service/project.service';

@Component({
  selector: 'app-project-overview',
  templateUrl: './project-overview.component.html',
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
    TagDisplayComponent,
    MatButtonModule,
  ],
  styles: ``,
})
export class ProjectOverviewComponent implements OnInit {
  projectService = inject(ProjectWrapperService);

  @ViewChildren('tagsWidgets') tagsWidgets?: QueryList<ElementRef> = undefined;

  scrollPosition: Record<number, number> = {};

  getProjectTags = getProjectTags;

  form = new FormGroup({
    search: new FormControl<string>(''),
    projectType: new FormControl<string | null>(null),
    projectVisibility: new FormControl<string | null>(null),
  });
  public readonly filteredProjects$ = this.form.valueChanges.pipe(
    startWith(this.form.value),
    switchMap((query) =>
      this.searchAndSortProjects(
        query.search!,
        query?.projectType ?? undefined,
        query?.projectVisibility ?? undefined,
      ),
    ),
  );

  searchAndSortProjects(
    query: string,
    projectType?: string,
    projectVisibility?: string,
  ) {
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
        projects?.filter((project) => {
          if (projectVisibility) {
            return project.visibility === projectVisibility;
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

  ngOnInit() {
    this.projectService.loadProjects();
    this.projectService.projects$
      .pipe(filter(Boolean))
      .subscribe((projects) => {
        for (const project of projects) {
          this.scrollPosition[project.id] = 0;
        }
      });
  }

  getTagsWidgetByProject(project: Project) {
    if (!this.tagsWidgets) return null;
    const tagsWidgets = this.tagsWidgets.toArray();
    const index = tagsWidgets.findIndex(
      (widget) => widget.nativeElement.id === 'tags-' + project.id,
    );
    if (index !== -1) {
      return tagsWidgets[index];
    }
    return null;
  }

  scroll(project: Project, event: Event, distance: number) {
    event.stopPropagation();
    event.preventDefault();
    const tagsWidget = this.getTagsWidgetByProject(project);
    if (!tagsWidget) return;
    if (!this.isScrollable(project, distance > 0 ? 'right' : 'left')) return;
    this.scrollPosition[project.id] += distance;
    tagsWidget.nativeElement.scrollTo({
      left: this.scrollPosition[project.id] + distance,
      behavior: 'smooth',
    });
  }

  isScrollable(project: Project, direction: 'left' | 'right') {
    const tagsWidget = this.getTagsWidgetByProject(project);
    if (!tagsWidget) return false;
    if (direction === 'left') {
      return this.scrollPosition[project.id] > 0;
    } else {
      return (
        this.scrollPosition[project.id] + tagsWidget.nativeElement.clientWidth <
        tagsWidget.nativeElement.scrollWidth
      );
    }
  }
}
