/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { SpyLocation } from '@angular/common/testing';
import { NO_ERRORS_SCHEMA } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ReactiveFormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatStepperModule } from '@angular/material/stepper';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { RouterTestingModule } from '@angular/router/testing';
import { BehaviorSubject, Observable, of } from 'rxjs';
import {
  Project,
  ProjectService,
} from 'src/app/services/project/project.service';

import {
  click,
  findComponent,
  findElByTestId,
  setFieldValue,
} from '../../helpers/spec-helper/element.spec-helper';
import { ToastService } from '../../helpers/toast/toast.service';
import { CreateProjectComponent } from './create-project.component';

const mockProjects: Project[] = [
  {
    name: 'existing-test-project-name',
    slug: 'existing-test-project-name',
    description: 'existing-test-project-description',
    users: {
      leads: 1,
      contributors: 0,
      subscribers: 0,
    },
  },
];

const testProjectName = 'test-project-name';
const testProjectSlug = 'test-project-name';
const testProjectDescription = 'test-project-description';

describe('CreateProjectComponent', () => {
  let fixture: ComponentFixture<CreateProjectComponent>;
  let component: CreateProjectComponent;

  const fakeToastService: Pick<ToastService, 'showSuccess'> = {
    showSuccess(): void {},
  };

  const fakeProjectService: Pick<
    ProjectService,
    '_project' | '_projects' | 'list' | 'createProject' | 'project' | 'projects'
  > = {
    _project: new BehaviorSubject<Project | undefined>(undefined),
    _projects: new BehaviorSubject<Project[] | undefined>(undefined),
    list() {
      this._projects.next(mockProjects);
      return of(mockProjects);
    },
    createProject(project: Project): Observable<Project> {
      let projectToCreate: Project = {
        name: project.name,
        description: project.description,
        slug: project.name,
        users: { leads: 1, contributors: 0, subscribers: 0 },
      };
      this._project.next(projectToCreate);
      return of(projectToCreate);
    },
    get projects(): Project[] | undefined {
      return this._projects.value;
    },
    get project(): Project | undefined {
      return this._project.value;
    },
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      providers: [
        { provide: ProjectService, useValue: fakeProjectService },
        { provide: ToastService, useValue: fakeToastService },
        { provide: Location, useClass: SpyLocation },
      ],
      declarations: [CreateProjectComponent],
      imports: [
        RouterTestingModule,
        MatFormFieldModule,
        MatInputModule,
        MatStepperModule,
        MatCardModule,
        ReactiveFormsModule,
        BrowserAnimationsModule,
      ],
      schemas: [NO_ERRORS_SCHEMA],
    }).compileComponents();
    fixture = TestBed.createComponent(CreateProjectComponent);
    component = fixture.componentInstance;

    fixture.detectChanges();
  });

  it('creates', () => {
    expect(component).toBeTruthy();
  });

  it('should not be possible to click on create project when project name already exists', () => {
    const existingTestProjectName = mockProjects[0].name;

    setFieldValue(fixture, 'input-name', existingTestProjectName);
    fixture.detectChanges();

    const createButton: HTMLButtonElement = findElByTestId(
      fixture,
      'button-create-project'
    ).nativeElement;
    expect(createButton.disabled).toBeTruthy();
  });

  it('calls create project with input name and empty input description when clicked on create project button', () => {
    spyOn(fakeProjectService, 'createProject').and.callThrough();
    spyOn(fakeToastService, 'showSuccess').and.callThrough();

    setFieldValue(fixture, 'input-name', testProjectName);
    click(fixture, 'button-create-project');

    fixture.detectChanges();

    expect(fakeProjectService.createProject).toHaveBeenCalledOnceWith(
      {
        name: testProjectName,
        description: '',
      },
      true
    );
    expect(fakeToastService.showSuccess).toHaveBeenCalledTimes(1);
  });

  it('calls create project with input name and input description when clicked on create project button', () => {
    spyOn(fakeProjectService, 'createProject').and.callThrough();
    spyOn(fakeToastService, 'showSuccess').and.callThrough();

    setFieldValue(fixture, 'input-name', testProjectName);
    setFieldValue(fixture, 'textarea-description', testProjectDescription);
    click(fixture, 'button-create-project');

    fixture.detectChanges();

    expect(fakeProjectService.createProject).toHaveBeenCalledOnceWith(
      {
        name: testProjectName,
        description: testProjectDescription,
      },
      true
    );
    expect(fakeToastService.showSuccess).toHaveBeenCalledTimes(1);
  });

  it('loads the app-project-user-settings when clicked on create project button', () => {
    setFieldValue(fixture, 'input-name', testProjectName);
    click(fixture, 'button-create-project');

    fixture.detectChanges();

    const appProjectUserSettingComponent = findComponent(
      fixture,
      'app-project-user-settings'
    );

    expect(appProjectUserSettingComponent).toBeTruthy();
  });

  it('loads the app-create-model when clicked on skip button in add member step', () => {
    setFieldValue(fixture, 'input-name', testProjectName);
    click(fixture, 'button-create-project');

    fixture.detectChanges();

    click(fixture, 'button-skipAddMembers');
    fixture.detectChanges();

    const appCreateModelComponent = findComponent(fixture, 'app-create-model');

    expect(appCreateModelComponent).toBeTruthy();
  });

  it('renders routerLink to /projects', () => {
    let cancelEl: HTMLElement = findElByTestId(
      fixture,
      'a-cancel'
    ).nativeElement;

    expect(cancelEl.getAttribute('href')).toEqual('/projects');
  });

  it('gets redirected to project/:projectName after clicking on finish', () => {
    setFieldValue(fixture, 'input-name', testProjectName);
    click(fixture, 'button-create-project');
    fixture.detectChanges();

    click(fixture, 'button-skipAddMembers');
    fixture.detectChanges();

    let skipEl: HTMLElement = findElByTestId(
      fixture,
      'a-skipModelAndFinishProjectCreation'
    ).nativeElement;

    expect(skipEl.getAttribute('href')).toEqual(`/project/${testProjectSlug}`);
  });
});
