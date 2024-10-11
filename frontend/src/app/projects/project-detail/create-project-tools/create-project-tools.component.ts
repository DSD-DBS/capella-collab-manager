/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component, OnInit } from '@angular/core';
import {
  FormControl,
  FormGroup,
  ReactiveFormsModule,
  Validators,
} from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatSelectModule } from '@angular/material/select';
import { ActivatedRoute, Router } from '@angular/router';
import { BehaviorSubject, filter, switchMap, take } from 'rxjs';
import {
  PostProjectToolRequest,
  ProjectsToolsService,
  Tool,
  ToolsService,
  ToolVersion,
} from 'src/app/openapi';
import { ProjectWrapperService } from 'src/app/projects/service/project.service';

@Component({
  selector: 'app-create-project-tools',
  standalone: true,
  imports: [
    CommonModule,
    MatFormFieldModule,
    ReactiveFormsModule,
    MatSelectModule,
    MatIconModule,
    MatButtonModule,
  ],
  templateUrl: './create-project-tools.component.html',
  styles: `
    :host {
      display: block;
    }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class CreateProjectToolsComponent implements OnInit {
  form = new FormGroup({
    tool_id: new FormControl<number>(-1, [Validators.min(0)]),
    tool_version_id: new FormControl<number>(-1, [Validators.min(0)]),
  });

  private readonly availableTools = new BehaviorSubject<Tool[] | undefined>(
    undefined,
  );
  availableTools$ = this.availableTools.asObservable();

  private readonly availableToolVersions = new BehaviorSubject<
    ToolVersion[] | undefined
  >(undefined);
  availableToolVersions$ = this.availableToolVersions.asObservable();

  constructor(
    public projectWrapperService: ProjectWrapperService,
    private projectsToolService: ProjectsToolsService,
    private toolsService: ToolsService,
    private router: Router,
    private route: ActivatedRoute,
  ) {}

  ngOnInit(): void {
    this.loadTools();
    this.form.controls.tool_id.valueChanges.subscribe((value) => {
      if (!value) return;
      this.loadToolVersions(value);
    });
  }

  loadTools() {
    this.availableTools.next(undefined);
    this.toolsService
      .getTools()
      .subscribe((tools) => this.availableTools.next(tools));
  }

  loadToolVersions(toolID: number) {
    this.availableToolVersions.next(undefined);
    this.toolsService
      .getToolVersions(toolID)
      .subscribe((versions) => this.availableToolVersions.next(versions));
  }

  onSubmit() {
    this.projectWrapperService.project$
      .pipe(
        take(1),
        filter(Boolean),
        switchMap((project) =>
          this.projectsToolService.linkToolToProject(
            project.slug,
            this.form.value as PostProjectToolRequest,
          ),
        ),
      )
      .subscribe(() =>
        this.router.navigate(['../..'], {
          relativeTo: this.route,
        }),
      );
  }
}
