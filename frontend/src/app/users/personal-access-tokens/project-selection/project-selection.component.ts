/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { AsyncPipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, Inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatAutocompleteModule } from '@angular/material/autocomplete';
import { MatButtonModule } from '@angular/material/button';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { ProjectWrapperService } from 'src/app/projects/service/project.service';

@Component({
  selector: 'app-project-selection',
  imports: [
    MatAutocompleteModule,
    MatFormFieldModule,
    AsyncPipe,
    MatInputModule,
    FormsModule,
    MatSelectModule,
    MatButtonModule,
  ],
  templateUrl: './project-selection.component.html',
  styles: `
    :host {
      display: block;
    }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ProjectSelectionComponent {
  selectedProject: string | undefined;

  constructor(
    public projectWrapperService: ProjectWrapperService,
    public matDialogRef: MatDialogRef<ProjectSelectionComponent>,
    @Inject(MAT_DIALOG_DATA) public data: { excludeProjects: string[] },
  ) {
    this.projectWrapperService.loadProjects();
  }
}
