/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { ChangeDetectionStrategy, Component } from '@angular/core';
import {
  FormControl,
  FormGroup,
  FormsModule,
  ReactiveFormsModule,
  Validators,
} from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { ActivatedRoute, Router } from '@angular/router';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import { absoluteUrlValidator } from 'src/app/helpers/validators/url-validator';
import { PostGitInstance } from 'src/app/openapi';
import { GitInstancesWrapperService } from 'src/app/settings/modelsources/git-settings/service/git-instances.service';

@Component({
  selector: 'app-add-git-instance',
  imports: [
    MatButtonModule,
    MatSelectModule,
    ReactiveFormsModule,
    FormsModule,
    MatInputModule,
  ],
  templateUrl: './add-git-instance.component.html',
  styles: `
    :host {
      display: block;
    }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AddGitInstanceComponent {
  constructor(
    public gitInstancesService: GitInstancesWrapperService,
    private toastService: ToastService,
    private router: Router,
    private route: ActivatedRoute,
  ) {}

  gitInstancesForm = new FormGroup({
    type: new FormControl('', Validators.required),
    name: new FormControl('', {
      validators: Validators.required,
      asyncValidators: this.gitInstancesService.asyncNameValidator(),
    }),
    url: new FormControl('', [Validators.required, absoluteUrlValidator()]),
    api_url: new FormControl('', absoluteUrlValidator()),
  });

  createGitInstance(): void {
    if (this.gitInstancesForm.valid) {
      let url = this.gitInstancesForm.value.url!;
      if (url.endsWith('/')) {
        url = url.slice(0, -1);
      }

      this.gitInstancesService
        .createGitInstance(this.gitInstancesForm.value as PostGitInstance)
        .subscribe(() => {
          this.router.navigate(['../../git-instances'], {
            relativeTo: this.route,
          });
          this.toastService.showSuccess(
            '',
            `Git instance ${this.gitInstancesForm.value.name} successfully created`,
          );
        });
    }
  }
}
