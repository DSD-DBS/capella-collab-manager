/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { COMMA, ENTER } from '@angular/cdk/keycodes';
import {
  Component,
  inject,
  model,
  OnChanges,
  OnInit,
  signal,
  SimpleChanges,
} from '@angular/core';
import {
  FormControl,
  FormGroup,
  Validators,
  FormsModule,
  ReactiveFormsModule,
} from '@angular/forms';
import {
  MatAutocompleteModule,
  MatAutocompleteSelectedEvent,
} from '@angular/material/autocomplete';
import { MatButton } from '@angular/material/button';
import { MatChipsModule } from '@angular/material/chips';
import { MatFormField, MatLabel, MatError } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInput } from '@angular/material/input';
import { MatRadioGroup, MatRadioButton } from '@angular/material/radio';
import { MatTooltip } from '@angular/material/tooltip';
import { Router } from '@angular/router';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { filter } from 'rxjs';
import { TagDisplayComponent } from 'src/app/helpers/tag-display/tag-display.component';
import { TagHelperService } from 'src/app/helpers/tag/tag.service';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import { PatchProject, Project, Tag, TagsService } from 'src/app/openapi';
import { ProjectUserService } from 'src/app/projects/project-detail/project-users/service/project-user.service';
import { ProjectWrapperService } from '../../service/project.service';

@UntilDestroy()
@Component({
  selector: 'app-edit-project-metadata',
  templateUrl: './edit-project-metadata.component.html',
  imports: [
    FormsModule,
    ReactiveFormsModule,
    MatFormField,
    MatLabel,
    MatInput,
    MatError,
    MatRadioGroup,
    MatRadioButton,
    MatTooltip,
    MatButton,
    MatChipsModule,
    MatAutocompleteModule,
    MatIconModule,
    TagDisplayComponent,
  ],
})
export class EditProjectMetadataComponent implements OnInit, OnChanges {
  projectService = inject(ProjectWrapperService);
  projectUserService = inject(ProjectUserService);
  private toastService = inject(ToastService);
  private router = inject(Router);
  private tagsService = inject(TagsService);
  tagHelperService = inject(TagHelperService);

  readonly separatorKeysCodes: number[] = [ENTER, COMMA];
  readonly selectedTags = signal<Tag[]>([]);
  availableTags: Tag[] | undefined = undefined;
  readonly currentTag = model('');

  canDelete = false;
  project?: Project;

  form = new FormGroup({
    name: new FormControl<string>('', Validators.required),
    description: new FormControl<string>(''),
    visibility: new FormControl(''),
    type: new FormControl(''),
  });

  ngOnInit(): void {
    this.projectService.project$
      .pipe(untilDestroyed(this), filter(Boolean))
      .subscribe((project) => {
        this.project = project;
        this.selectedTags.set(project.tags || []);

        this.form.controls.name.setAsyncValidators(
          this.projectService.asyncSlugValidator(project),
        );
        this.form.patchValue(project);
      });
    this.tagsService.getTags().subscribe((tags) => {
      this.availableTags = tags;
    });
  }

  ngOnChanges(_changes: SimpleChanges): void {
    if (this.project) {
      this.projectService.loadProjectBySlug(this.project.slug);
    }
  }

  updateProject() {
    if (this.form.valid && this.project) {
      this.projectService
        .updateProject(this.project.slug, {
          ...this.form.value,
          tags: this.selectedTags().map((tag) => tag.id),
        } as PatchProject)
        .subscribe((project) => {
          this.router.navigateByUrl(`/project/${project.slug}`);
          this.toastService.showSuccess(
            'Project updated',
            `The new name is: '${project.name}' and the new description is '${
              project.description || ''
            }'`,
          );
        });
    }
  }

  addTag(event: MatAutocompleteSelectedEvent): void {
    this.selectedTags.update((selectedTags) => [
      ...selectedTags,
      event.option.value,
    ]);
    event.option.deselect();
  }

  removeTag(tag: Tag): void {
    this.selectedTags.update((tags) => {
      const index = tags.indexOf(tag);
      if (index < 0) {
        return tags;
      }

      tags.splice(index, 1);
      return [...tags];
    });
  }
}
