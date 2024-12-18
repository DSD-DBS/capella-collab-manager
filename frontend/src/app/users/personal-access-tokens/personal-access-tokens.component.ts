/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { AsyncPipe, KeyValuePipe } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import {
  FormBuilder,
  Validators,
  FormsModule,
  ReactiveFormsModule,
} from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { provideNativeDateAdapter } from '@angular/material/core';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatDialog } from '@angular/material/dialog';
import { MatFormField } from '@angular/material/form-field';
import { MatIcon } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { BehaviorSubject, tap } from 'rxjs';
import { RelativeTimeComponent } from 'src/app/general/relative-time/relative-time.component';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import {
  FineGrainedResource,
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
    RelativeTimeComponent,
  ],
  providers: [provideNativeDateAdapter()],
})
export class PersonalAccessTokensComponent implements OnInit {
  generatedToken?: string;
  minDate: Date;
  maxDate: Date;

  permissionsSchema?: Scopes;
  projectPermissionsSchema?: ProjectScopes;
  expandedTokenScopes: Record<string, boolean> = {};

  projectScopes: string[] = [];

  selectedScopes: FineGrainedResource = {
    user: {},
    admin: {},
    projects: {},
  };

  private _tokens = new BehaviorSubject<UserToken[] | undefined>(undefined);
  readonly tokens$ = this._tokens.asObservable();

  tokenForm = this.formBuilder.group({
    description: ['', [Validators.required, Validators.minLength(1)]],
    date: [this.getTomorrow(), [Validators.required]],
  });
  constructor(
    public tokenService: UsersTokenService,
    private toastService: ToastService,
    private formBuilder: FormBuilder,
    private permissionsService: PermissionsService,
    private matDialog: MatDialog,
    private projectsPermissionService: ProjectsPermissionsService,
  ) {
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
        scopeRoot[event.permission] = new Set<UserTokenVerb>();
      }
      scopeRoot[event.permission]!.add(event.verb);
    } else {
      scopeRoot[event.permission]!.delete(event.verb);
    }
  }

  private getRootScope(
    scope: string,
  ): Record<string, undefined | Set<UserTokenVerb>> {
    if (scope === 'admin' || scope === 'user') {
      return this.selectedScopes[scope];
    }

    if (!this.selectedScopes.projects[scope]) {
      this.selectedScopes.projects[scope] = {};
    }

    return this.selectedScopes.projects[scope];
  }

  countSelectedPermissions(scope: string): number {
    const scopeRoot = this.getRootScope(scope);
    let count = 0;

    for (const permission in scopeRoot) {
      if (scopeRoot[permission]) {
        count += scopeRoot[permission]?.size;
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
          description: this.tokenForm.value.description!,
          expiration_date: this.tokenForm.value
            .date!.toISOString()
            .substring(0, 10),
          source: 'token overview',
          // Transform Set to Array since Set isn't JSON serializable
          scopes: JSON.parse(
            JSON.stringify(this.selectedScopes, (_key, value) =>
              value instanceof Set ? [...value] : value,
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

  isTokenExpired(expirationDate: string): boolean {
    return new Date(expirationDate) < new Date();
  }

  showClipboardMessage(): void {
    this.toastService.showSuccess(
      'Token copied',
      'The token was copied to your clipboard.',
    );
  }

  loadTokens(): void {
    this.tokenService.getAllTokensOfUser().subscribe({
      next: (token) => this._tokens.next(token),
      error: () => this._tokens.next(undefined),
    });
  }

  deleteToken(token: UserToken) {
    this.generatedToken = undefined;
    this.tokenService
      .deleteTokenForUser(token.id)
      .pipe(tap(() => this.loadTokens()))
      .subscribe(() => {
        this.toastService.showSuccess(
          'Token deleted',
          `The token ${token.description} was successfully deleted!`,
        );
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
