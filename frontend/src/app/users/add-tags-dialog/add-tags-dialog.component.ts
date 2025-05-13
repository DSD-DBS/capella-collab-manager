/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Component, inject, signal } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import {
  MatAutocompleteModule,
  MatAutocompleteSelectedEvent,
} from '@angular/material/autocomplete';
import { MatButtonModule } from '@angular/material/button';
import { MatChipsModule } from '@angular/material/chips';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatTooltipModule } from '@angular/material/tooltip';
import { TagDisplayComponent } from 'src/app/helpers/tag-display/tag-display.component';
import { TagHelperService } from 'src/app/helpers/tag/tag.service';
import { Tag, TagsService, User, UsersService } from 'src/app/openapi';

@Component({
  selector: 'app-add-tags-dialog',
  imports: [
    MatTooltipModule,
    FormsModule,
    ReactiveFormsModule,
    MatInputModule,
    MatIconModule,
    MatFormFieldModule,
    MatChipsModule,
    MatAutocompleteModule,
    TagDisplayComponent,
    MatButtonModule,
  ],
  templateUrl: './add-tags-dialog.component.html',
  styles: `
    :host {
      display: block;
    }
  `,
})
export class AddTagsDialogComponent {
  readonly selectedTags = signal<Tag[]>([]);
  tagHelperService = inject(TagHelperService);

  user = inject<User>(MAT_DIALOG_DATA);
  private matDialogRef =
    inject<MatDialogRef<AddTagsDialogComponent>>(MatDialogRef);
  availableTags: Tag[] | undefined = undefined;
  tagsService = inject(TagsService);
  userService = inject(UsersService);

  loading = signal<boolean>(false);

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

  constructor() {
    this.selectedTags.set(structuredClone(this.user.tags) || []);
    this.tagsService.getTags().subscribe((tags) => {
      this.availableTags = tags.filter((tag) => tag.scope === 'user');
    });
  }

  closeDialog(result: boolean) {
    this.matDialogRef.close(result);
  }

  updateUser() {
    this.loading.set(true);
    this.userService
      .updateUser(this.user.id, {
        tags: this.selectedTags().map((tag) => tag.id),
      })
      .subscribe({
        next: () => {
          this.loading.set(false);
          this.closeDialog(true);
        },
        error: () => {
          this.loading.set(false);
        },
      });
  }
}
