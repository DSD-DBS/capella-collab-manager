/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component } from '@angular/core';
import {
  AbstractControl,
  FormControl,
  FormGroup,
  ValidationErrors,
  ValidatorFn,
  Validators,
} from '@angular/forms';
import { MatDialog } from '@angular/material/dialog';
import { ActivatedRoute, Router } from '@angular/router';
import { combineLatest, filter, map, mergeMap, of, switchMap, tap } from 'rxjs';
import { BreadcrumbsService } from 'src/app/general/breadcrumbs/breadcrumbs.service';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import { Tool, ToolDockerimages, ToolService } from '../tool.service';
import { ToolDeletionDialogComponent } from './tool-deletion-dialog/tool-deletion-dialog.component';

@Component({
  selector: 'app-tool-details',
  templateUrl: './tool-details.component.html',
  styleUrls: ['./tool-details.component.css'],
})
export class ToolDetailsComponent {
  editing = false;
  existing = false;

  selectedTool?: Tool;
  dockerimages?: ToolDockerimages;

  public form = new FormGroup({
    name: new FormControl('', Validators.required),
    dockerimages: new FormGroup({
      persistent: new FormControl('', [
        Validators.required,
        Validators.maxLength(4096),
        this.validDockerImageNameValidator(),
      ]),
      readonly: new FormControl('', [
        Validators.maxLength(4096),
        this.validDockerImageNameValidator(),
      ]),
      backup: new FormControl('', [
        Validators.maxLength(4096),
        this.validDockerImageNameValidator(),
      ]),
    }),
  });

  constructor(
    private route: ActivatedRoute,
    private toolService: ToolService,
    private toastService: ToastService,
    private breadcrumbsService: BreadcrumbsService,
    private router: Router,
    private dialog: MatDialog,
  ) {
    this.toolService.getTools().subscribe();

    this.route.params
      .pipe(
        map((params) => params.toolID),
        filter((toolID) => toolID !== undefined),
        mergeMap((toolID) => {
          return combineLatest([
            of(toolID),
            this.toolService._tools,
            this.toolService.getDockerimagesForTool(toolID),
          ]);
        }),
        tap(([_toolID, _tools, dockerimages]) => {
          this.dockerimages = dockerimages;
        }),
        map(([toolID, tools, _dockerimages]) => {
          return tools?.find((tool: Tool) => {
            return tool.id == toolID;
          });
        }),
      )
      .subscribe({
        next: (tool) => {
          this.breadcrumbsService.updatePlaceholder({ tool });
          this.existing = true;
          this.selectedTool = tool;
          this.updateForm();
        },
      });
  }

  enableEditing(): void {
    this.editing = true;
    this.form.enable();
  }

  cancelEditing(): void {
    this.editing = false;
    this.form.disable();
  }

  updateForm(): void {
    this.form.patchValue({
      name: this.selectedTool?.name,
      dockerimages: this.dockerimages,
    });
    this.cancelEditing();
  }

  validDockerImageNameValidator(): ValidatorFn {
    return (control: AbstractControl): ValidationErrors | null => {
      /*
        Name components may contain lowercase letters, digits and separators.
        A separator is defined as a period, one or two underscores, or one or more dashes.
        A name component may not start or end with a separator.

        https://docs.docker.com/engine/reference/commandline/tag/#extended-description

        In addition, we allow $ (to use the $version syntax) and : for the tag.
      */
      if (
        control.value &&
        !/^[a-zA-Z0-9][a-zA-Z0-9_\-/\.:\$]*$/.test(control.value)
      ) {
        return { validDockerImageNameInvalid: true };
      }
      return {};
    };
  }

  create(): void {
    if (this.form.valid) {
      const name = this.form.controls.name.value!;

      this.toolService
        .createTool(name)
        .pipe(
          tap((tool) => {
            this.toastService.showSuccess(
              'Tool created',
              `The tool with name ${tool.name} was created.`,
            );

            this.selectedTool = tool;
          }),
          switchMap((tool) => {
            return this.toolService.updateDockerimagesForTool(
              tool.id,
              this.form.controls.dockerimages.value as ToolDockerimages,
            );
          }),
          tap((_) => {
            this.toastService.showSuccess(
              'Docker images updated',
              `The Docker images for the tool '${name}' were updated.`,
            );
          }),
        )
        .subscribe(() => {
          this.router.navigate(['../..', 'tool', this.selectedTool?.id], {
            relativeTo: this.route,
          });
        });
    }
  }

  update(): void {
    if (this.form.valid) {
      this.toolService
        .updateTool(this.selectedTool!.id, this.form.controls.name.value!)
        .pipe(
          tap((tool) => {
            this.toastService.showSuccess(
              'Tool updated',
              `The tool name changed from '${this.selectedTool?.name}' to '${tool.name}'.`,
            );
          }),
        )
        .subscribe((tool) => {
          this.selectedTool = tool;
        });

      this.toolService
        .updateDockerimagesForTool(
          this.selectedTool!.id,
          this.form.controls.dockerimages.value as ToolDockerimages,
        )
        .pipe(
          tap((dockerimages) => {
            this.dockerimages = dockerimages;
          }),
        )
        .subscribe((_) => {
          this.toastService.showSuccess(
            'Docker images for Tool updated',
            `The Docker images for the tool with id ${
              this.selectedTool!.id
            } were updated.`,
          );
          this.cancelEditing();
        });
    }
  }

  deleteTool(): void {
    this.dialog
      .open(ToolDeletionDialogComponent, {
        data: this.selectedTool,
      })
      .afterClosed()
      .pipe(filter((res: boolean) => res))
      .subscribe(() => {
        this.router.navigate(['../..', 'tools'], {
          relativeTo: this.route,
        });
        this.toastService.showSuccess(
          'Tool deleted',
          `The tool '${this.selectedTool?.name}' was deleted successfully`,
        );
      });
  }

  submit(): void {
    if (this.existing) {
      this.update();
    } else {
      this.create();
    }
  }
}
