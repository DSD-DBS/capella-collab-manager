/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { BehaviorSubject } from 'rxjs';
import { ProjectTool } from 'src/app/openapi';
import { ProjectToolsWrapperService } from 'src/app/projects/project-detail/project-tools/project-tools-wrapper.service';
import { mockModel } from 'src/storybook/model';
import {
  mockCapellaTool,
  mockCapellaToolVersion,
  mockOtherToolVersion,
  mockTrainingControllerTool,
} from 'src/storybook/tool';

class MockProjectToolsService implements Partial<ProjectToolsWrapperService> {
  private readonly _projectTools = new BehaviorSubject<
    ProjectTool[] | undefined
  >(undefined);
  readonly projectTools$ = this._projectTools.asObservable();

  constructor(projectTools: ProjectTool[] | undefined) {
    this._projectTools.next(projectTools);
  }
}

export const projectToolServiceProvider = (
  projectTools: ProjectTool[] | undefined,
) => {
  return {
    provide: ProjectToolsWrapperService,
    useValue: new MockProjectToolsService(projectTools),
  };
};

export const mockProjectTool: ProjectTool = {
  id: 1,
  tool_version: mockCapellaToolVersion,
  tool: mockCapellaTool,
  used_by: [mockModel],
};

export const mockTrainingTool: ProjectTool = {
  id: 2,
  tool_version: mockOtherToolVersion,
  tool: mockTrainingControllerTool,
  used_by: [],
};
