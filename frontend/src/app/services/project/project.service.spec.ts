/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { TestBed } from '@angular/core/testing';
import {
  HttpClientTestingModule,
  HttpTestingController,
} from '@angular/common/http/testing';

import { ProjectService, Project } from './project.service';
import { environment } from 'src/environments/environment';
import { HttpParams } from '@angular/common/http';

const BACKEND_PROJECTS_URL = environment.backend_url + '/projects/';

const testProjectName = 'test-project-name';
const testProjectSlug = 'test-project-slug';
const testProjectDescription = 'test-project-description';

const mockProject: Project = {
  name: testProjectName,
  slug: testProjectSlug,
  description: testProjectDescription,
  users: {
    leads: 0,
    contributors: 0,
    subscribers: 0,
  },
};

describe('ProjectService', () => {
  let projectService: ProjectService;
  let httpTestingController: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [ProjectService],
      imports: [HttpClientTestingModule],
    });

    projectService = TestBed.inject(ProjectService);
    httpTestingController = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpTestingController.verify();
  });

  it('should return a project by its name', () => {
    projectService.getProject(testProjectName).subscribe({
      next: (project) => expect(project).toEqual(mockProject),
    });

    const req = httpTestingController.expectOne(
      BACKEND_PROJECTS_URL + testProjectName
    );
    expect(req.request.method).toEqual('GET');
    expect(req.request.params).toEqual(new HttpParams());

    req.flush(mockProject);
  });

  it('should return a project by its slug', () => {
    projectService.getProjectBySlug(testProjectSlug).subscribe({
      next: (project) => expect(project).toEqual(mockProject),
    });

    let url: URL = new URL('details/', BACKEND_PROJECTS_URL);
    url.searchParams.append('slug', testProjectSlug);

    const req = httpTestingController.expectOne(url.href);
    expect(req.request.method).toEqual('GET');
    expect(req.request.params.get('slug')).toEqual(testProjectSlug);

    req.flush(mockProject);
  });

  it('should return all projects', () => {
    projectService.list().subscribe({
      next: (projects) => expect(projects).toEqual([mockProject]),
    });

    const req = httpTestingController.expectOne(BACKEND_PROJECTS_URL);
    expect(req.request.method).toEqual('GET');
    expect(req.request.body).toBeNull();

    req.flush([mockProject]);
  });

  it('should create a project and return it', () => {
    projectService
      .createProject({
        name: testProjectName,
        description: testProjectDescription,
      })
      .subscribe({
        next: (project) => expect(project).toEqual(mockProject),
      });

    const req = httpTestingController.expectOne(BACKEND_PROJECTS_URL);
    expect(req.request.method).toEqual('POST');
    expect(req.request.body).toEqual({
      name: testProjectName,
      description: testProjectDescription,
    });

    req.flush(mockProject);
  });

  it('should update the project description', () => {
    const updatedMockProjectDescription = 'update-test-project-description';
    let updatedMockProject: Project = mockProject;
    updatedMockProject.description = updatedMockProjectDescription;

    projectService
      .updateDescription(testProjectName, updatedMockProjectDescription)
      .subscribe({
        next: (project) => expect(project).toEqual(updatedMockProject),
      });

    const req = httpTestingController.expectOne(
      BACKEND_PROJECTS_URL + testProjectName
    );
    expect(req.request.method).toEqual('PATCH');
    expect(req.request.body).toEqual({
      description: updatedMockProjectDescription,
    });
  });

  it('should return the project inserted into the BehaviorSubject', () => {
    projectService._project.next(mockProject);
    expect(projectService.project).toEqual(mockProject);
  });

  it('should return the projects inserted into BehaviorSubject', () => {
    projectService._projects.next([mockProject]);
    expect(projectService.projects).toEqual([mockProject]);
  });
});
