/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { AsyncValidatorFn, ValidationErrors } from '@angular/forms';
import { BehaviorSubject, Observable, of } from 'rxjs';
import { Project, ProjectType, Visibility } from 'src/app/openapi';
import {
  ProjectTypeDescriptions,
  ProjectVisibilityDescriptions,
  ProjectWrapperService,
} from 'src/app/projects/service/project.service';

export const mockProject: Readonly<Project> = {
  id: 1,
  name: 'mockProject',
  description:
    'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.',
  type: 'general',
  visibility: 'internal',
  is_archived: false,
  slug: 'mockProject',
  users: {
    leads: 1,
    contributors: 1,
    subscribers: 1,
  },
};

export class MockProjectWrapperService
  implements Partial<ProjectWrapperService>
{
  private _project = new BehaviorSubject<Project | undefined>(undefined);
  private _projects = new BehaviorSubject<Project[] | undefined>(undefined);

  public readonly project$ = this._project.asObservable();
  public readonly projects$ = this._projects.asObservable();

  constructor(project: Project | undefined, projects: Project[] | undefined) {
    this._project.next(project);
    this._projects.next(projects);
  }
  asyncSlugValidator(): AsyncValidatorFn {
    return (): Observable<ValidationErrors | null> => {
      return of(null);
    };
  }
  getProjectVisibilityDescription(visibility: Visibility): string {
    return ProjectVisibilityDescriptions[visibility];
  }

  getAvailableVisibilities(): Visibility[] {
    return Object.keys(ProjectVisibilityDescriptions) as Visibility[];
  }

  getProjectTypeDescription(type: ProjectType): string {
    return ProjectTypeDescriptions[type];
  }

  getAvailableProjectTypes(): ProjectType[] {
    return Object.keys(ProjectTypeDescriptions) as ProjectType[];
  }
  createProject(project: Project): Observable<Project> {
    return of(project);
  }
  clearProject(): void {
    return;
  }
}
