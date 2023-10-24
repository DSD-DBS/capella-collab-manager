/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { SpyLocation } from '@angular/common/testing';
import { NO_ERRORS_SCHEMA } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import {
  AbstractControl,
  AsyncValidatorFn,
  ReactiveFormsModule,
  ValidationErrors,
} from '@angular/forms';
import { MatLegacyCardModule as MatCardModule } from '@angular/material/legacy-card';
import { MatLegacyFormFieldModule as MatFormFieldModule } from '@angular/material/legacy-form-field';
import { MatLegacyInputModule as MatInputModule } from '@angular/material/legacy-input';
import { MatRadioModule } from '@angular/material/radio';
import { MatStepperModule } from '@angular/material/stepper';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { RouterTestingModule } from '@angular/router/testing';
import { BehaviorSubject, map, Observable, of, take } from 'rxjs';
import slugify from 'slugify';
import {
  click,
  findComponent,
  findElByTestId,
  setFieldValue,
} from 'src/../tests/spec-helper/element.spec-helper';

import { ToastService } from '../../helpers/toast/toast.service';
import { ProjectUserService } from '../project-detail/project-users/service/project-user.service';
import {
  PatchProject,
  Project,
  ProjectService,
  ProjectVisibility,
} from '../service/project.service';
import { CreateProjectComponent } from './create-project.component';

const mockProjects: Project[] = [
  {
    name: 'existing-test-project-name',
    slug: 'existing-test-project-name',
    description: 'existing-test-project-description',
    visibility: 'private',
    type: 'general',
    users: {
      leads: 1,
      contributors: 0,
      subscribers: 0,
    },
    is_archived: false,
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

  const fakeProjectUserService = {
    get nonAdminProjectUsers$(): Observable<any> {
      return of(undefined);
    },

    resetProjectUserOnProjectReset(): void {},
    resetProjectUsersOnProjectReset(): void {},
    loadProjectUsersOnProjectChange(): void {},
    loadProjectUserOnProjectChange(): void {},
  };

  const fakeProjectService = {
    _project: new BehaviorSubject<Project | undefined>(undefined),
    _projects: new BehaviorSubject<Project[] | undefined>(undefined),

    get project$(): Observable<Project | undefined> {
      return this._project.asObservable();
    },

    get projects$(): Observable<Project[] | undefined> {
      return this._projects.asObservable();
    },

    loadProjects() {
      this._projects.next(mockProjects);
      return of(mockProjects);
    },
    createProject(project: PatchProject): Observable<Project> {
      const projectToCreate: Project = {
        name: project.name!,
        description: project.description!,
        slug: project.name!,
        visibility: project.visibility!,
        type: project.type!,
        users: { leads: 1, contributors: 0, subscribers: 0 },
        is_archived: false,
      };
      this._project.next(projectToCreate);
      return of(projectToCreate);
    },
    clearProject(): void {
      this._project.next(undefined);
    },
    asyncSlugValidator(): AsyncValidatorFn {
      return (
        control: AbstractControl,
      ): Observable<ValidationErrors | null> => {
        const projectSlug = slugify(control.value, { lower: true });
        return this.projects$.pipe(
          take(1),
          map((projects) => {
            return projects?.find((project) => project.slug === projectSlug)
              ? { uniqueSlug: { value: projectSlug } }
              : null;
          }),
        );
      };
    },
    getProjectVisibilityDescription(visibility: ProjectVisibility): string {
      return ProjectVisibility[visibility];
    },
    getAvailableVisibilities(): ProjectVisibility[] {
      return Object.keys(ProjectVisibility) as ProjectVisibility[];
    },
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      providers: [
        { provide: ProjectService, useValue: fakeProjectService },
        { provide: ToastService, useValue: fakeToastService },
        { provide: ProjectUserService, useValue: fakeProjectUserService },
        { provide: Location, useClass: SpyLocation },
      ],
      declarations: [CreateProjectComponent],
      imports: [
        RouterTestingModule,
        MatFormFieldModule,
        MatInputModule,
        MatStepperModule,
        MatCardModule,
        MatRadioModule,
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
      'button-create-project',
    ).nativeElement;
    expect(createButton.disabled).toBeTruthy();
  });

  it('calls create project with input name and empty input description when clicked on create project button', () => {
    spyOn(fakeProjectService, 'createProject').and.callThrough();
    spyOn(fakeToastService, 'showSuccess').and.callThrough();

    setFieldValue(fixture, 'input-name', testProjectName);
    click(fixture, 'button-create-project');

    fixture.detectChanges();

    expect(fakeProjectService.createProject).toHaveBeenCalledOnceWith({
      name: testProjectName,
      description: '',
      visibility: 'private',
      type: 'general',
    });
    expect(fakeToastService.showSuccess).toHaveBeenCalledTimes(1);
  });

  it('calls create project with input name and input description when clicked on create project button', () => {
    spyOn(fakeProjectService, 'createProject').and.callThrough();
    spyOn(fakeToastService, 'showSuccess').and.callThrough();

    setFieldValue(fixture, 'input-name', testProjectName);
    setFieldValue(fixture, 'textarea-description', testProjectDescription);
    click(fixture, 'button-create-project');

    fixture.detectChanges();

    expect(fakeProjectService.createProject).toHaveBeenCalledOnceWith({
      name: testProjectName,
      description: testProjectDescription,
      visibility: 'private',
      type: 'general',
    });
    expect(fakeToastService.showSuccess).toHaveBeenCalledTimes(1);
  });

  it('loads the app-project-user-settings when clicked on create project button', () => {
    setFieldValue(fixture, 'input-name', testProjectName);
    click(fixture, 'button-create-project');

    fixture.detectChanges();

    const appProjectUserSettingComponent = findComponent(
      fixture,
      'app-project-user-settings',
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

  it('gets redirected to project/:projectName after clicking on finish', () => {
    setFieldValue(fixture, 'input-name', testProjectName);
    click(fixture, 'button-create-project');
    fixture.detectChanges();

    click(fixture, 'button-skipAddMembers');
    fixture.detectChanges();

    const skipEl: HTMLElement = findElByTestId(
      fixture,
      'a-skipModelAndFinishProjectCreation',
    ).nativeElement;

    expect(skipEl.getAttribute('href')).toEqual(`/project/${testProjectSlug}`);
  });
});
