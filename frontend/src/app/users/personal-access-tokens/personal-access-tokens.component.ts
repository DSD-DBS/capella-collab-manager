/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { AsyncPipe, KeyValuePipe } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import {
  FormBuilder,
  Validators,
  FormsModule,
  ReactiveFormsModule,
} from '@angular/forms';
import { provideMomentDateAdapter } from '@angular/material-moment-adapter';
import { MatButtonModule } from '@angular/material/button';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatDialog } from '@angular/material/dialog';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatFormField } from '@angular/material/form-field';
import { MatIcon } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatTooltipModule } from '@angular/material/tooltip';
import { NgxSkeletonLoaderComponent } from 'ngx-skeleton-loader';
import { BehaviorSubject, tap } from 'rxjs';
import {
  FineGrainedResourceOutput,
  PermissionsService,
  ProjectsPermissionsService,
  UsersTokenService,
  UserToken,
} from 'src/app/openapi';
import { ProjectSelectionComponent } from 'src/app/users/personal-access-tokens/project-selection/project-selection.component';
import {
  TokenProperties,
  TokenPermissionSelectionComponent,
  UserTokenVerb,
  TokenPermissionSelectionEvent,
} from 'src/app/users/personal-access-tokens/token-permission-selection/token-permission-selection.component';
import { DisplayValueComponent } from '../../helpers/display-value/display-value.component';
import { TokenCardComponent } from './token-card/token-card.component';

@Component({
  selector: 'app-personal-access-tokens',
  templateUrl: './personal-access-tokens.component.html',
  imports: [
    FormsModule,
    ReactiveFormsModule,
    MatFormField,
    DisplayValueComponent,
    MatIcon,
    AsyncPipe,
    MatButtonModule,
    MatDatepickerModule,
    MatInputModule,
    MatCheckboxModule,
    KeyValuePipe,
    TokenPermissionSelectionComponent,
    MatExpansionModule,
    MatTooltipModule,
    TokenCardComponent,
    NgxSkeletonLoaderComponent,
  ],
  providers: [
    provideMomentDateAdapter({
      parse: {
        dateInput: 'LL',
      },
      display: {
        dateInput: 'LL',
        monthYearLabel: 'MMM YYYY',
        dateA11yLabel: 'LL',
        monthYearA11yLabel: 'MMMM YYYY',
      },
    }),
  ],
})
export class PersonalAccessTokensComponent implements OnInit {
  tokenService = inject(UsersTokenService);
  private formBuilder = inject(FormBuilder);
  private permissionsService = inject(PermissionsService);
  private matDialog = inject(MatDialog);
  private projectsPermissionService = inject(ProjectsPermissionsService);

  generatedToken?: string;
  minDate: Date;
  maxDate: Date;

  permissionsSchema?: Scopes;
  projectPermissionsSchema?: ProjectScopes;
  expandedTokenScopes: Record<string, boolean> = {};

  projectScopes: string[] = [];

  selectedScopes: FineGrainedResourceOutput = {
    user: {
      sessions: [],
      projects: [],
      tokens: [],
      feedback: [],
    },
    admin: {
      users: [],
      projects: [],
      tools: [],
      announcements: [],
      monitoring: [],
      configuration: [],
      git_servers: [],
      t4c_servers: [],
      t4c_repositories: [],
      pv_configuration: [],
      events: [],
      sessions: [],
      workspaces: [],
      personal_access_tokens: [],
      tags: [],
      pipelines: [],
    },
    projects: {},
  };

  private _tokens = new BehaviorSubject<UserToken[] | undefined>(undefined);
  readonly tokens$ = this._tokens.asObservable();

  tokenForm = this.formBuilder.group({
    title: [
      '',
      [Validators.required, Validators.minLength(1), Validators.maxLength(50)],
    ],
    description: [''],
    date: [this.getTomorrow(), [Validators.required]],
  });
  constructor() {
    this.minDate = this.getTomorrow();
    this.maxDate = new Date(
      this.minDate.getFullYear() + 1,
      this.minDate.getMonth(),
      this.minDate.getDate(),
    );
  }

  onSelectionChange(event: TokenPermissionSelectionEvent) {
    const scopeRoot = this.getRootScope(event.scope);

    if (event.checked) {
      if (!scopeRoot[event.permission]) {
        scopeRoot[event.permission] = [];
      }
      scopeRoot[event.permission]!.push(event.verb);
    } else {
      scopeRoot[event.permission] = scopeRoot[event.permission]!.filter(
        (element) => element !== event.verb,
      );
    }
  }

  private getRootScope(
    scope: string,
  ): Record<string, undefined | UserTokenVerb[]> {
    if (scope === 'admin' || scope === 'user') {
      return this.selectedScopes[scope];
    }

    if (!this.selectedScopes.projects[scope]) {
      this.selectedScopes.projects[scope] = {
        root: [],
        pipelines: [],
        pipeline_runs: [],
        diagram_cache: [],
        t4c_model_links: [],
        git_model_links: [],
        tool_models: [],
        used_tools: [],
        project_users: [],
        access_log: [],
        provisioning: [],
        t4c_access: [],
        restrictions: [],
        shared_volumes: [],
      };
    }

    return this.selectedScopes.projects[scope];
  }

  countSelectedPermissions(scope: string): number {
    const scopeRoot = this.getRootScope(scope);
    let count = 0;

    for (const permission in scopeRoot) {
      if (scopeRoot[permission]) {
        count += scopeRoot[permission]?.length;
      }
    }

    return count;
  }

  ngOnInit() {
    this.loadTokens();
    this.permissionsService
      .getAvailablePermissions()
      .subscribe((permissions) => {
        this.permissionsSchema = permissions;
      });
    this.projectsPermissionService
      .getAvailableProjectPermissions()
      .subscribe((permissions) => {
        this.projectPermissionsSchema = permissions;
      });
  }

  getTomorrow(): Date {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    return tomorrow;
  }

  createToken(): void {
    this.generatedToken = undefined;
    if (this.tokenForm.valid) {
      this.tokenService
        .createTokenForUser({
          title: this.tokenForm.value.title!,
          description: this.tokenForm.value.description!,
          expiration_date: this.tokenForm.value
            .date!.toISOString()
            .substring(0, 10),
          source: 'token overview',
          // Transform Array to Array since Array isn't JSON serializable
          scopes: JSON.parse(
            JSON.stringify(this.selectedScopes, (_key, value) =>
              value instanceof Array ? [...value] : value,
            ),
          ),
        })
        .pipe(tap(() => this.loadTokens()))
        .subscribe((token) => {
          this.generatedToken = token.password;
          this.tokenForm.controls.date.setValue(this.getTomorrow());
        });
    }
  }

  loadTokens(): void {
    this.tokenService.getAllTokensOfUser().subscribe({
      next: (token) => this._tokens.next(token),
      error: () => this._tokens.next(undefined),
    });
  }

  getPermissionByRef(ref: string) {
    return this.permissionsSchema?.$defs[ref.split('/').pop()!];
  }

  openProjectDialog() {
    this.matDialog
      .open(ProjectSelectionComponent, {
        data: {
          excludeProjects: this.projectScopes,
        },
      })
      .afterClosed()
      .subscribe((project) => {
        if (project) {
          this.projectScopes.push(project.slug);
        }
      });
  }

  unselectProject(projectSlug: string) {
    this.projectScopes = this.projectScopes.filter(
      (slug) => slug !== projectSlug,
    );
    delete this.selectedScopes.projects[projectSlug];
  }

  protected readonly Array = Array;
}

export interface Scopes {
  $defs: Record<
    string,
    {
      properties: TokenProperties;
      title: string;
    }
  >;
  properties: Record<
    string,
    {
      title: string;
      $ref: string;
    }
  >;
}

export interface ProjectScopes {
  properties: TokenProperties;
  title: string;
}
