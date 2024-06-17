/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { BehaviorSubject } from 'rxjs';
import { Project } from 'src/app/openapi';
import { ProjectWrapperService } from 'src/app/projects/service/project.service';

export const mockProject: Readonly<Project> = {
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

  constructor(project: Project, projects: Project[]) {
    this._project.next(project);
    this._projects.next(projects);
  }
}
