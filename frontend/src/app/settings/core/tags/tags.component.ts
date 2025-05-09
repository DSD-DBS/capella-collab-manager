/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import {
  ChangeDetectionStrategy,
  Component,
  inject,
  signal,
} from '@angular/core';
import {
  FormControl,
  FormGroup,
  FormsModule,
  ReactiveFormsModule,
  Validators,
} from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatChipsModule } from '@angular/material/chips';
import { MatDialog } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { ConfirmationDialogComponent } from 'src/app/helpers/confirmation-dialog/confirmation-dialog.component';
import { TagComponent } from 'src/app/helpers/tag/tag.component';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import { CreateTag, Tag, TagsService } from 'src/app/openapi';

@Component({
  selector: 'app-tags',
  imports: [
    MatChipsModule,
    MatButtonModule,
    MatIconModule,
    TagComponent,
    MatFormFieldModule,
    FormsModule,
    ReactiveFormsModule,
    MatInputModule,
    TagComponent,
    ConfirmationDialogComponent,
  ],
  templateUrl: './tags.component.html',
  styles: `
    :host {
      display: block;
    }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class TagsComponent {
  tags = signal<Tag[] | undefined>(undefined);

  private tagsService = inject(TagsService);
  private toastService = inject(ToastService);
  private dialog = inject(MatDialog);

  newTagForm = new FormGroup({
    name: new FormControl<string>('', [Validators.required]),
    hex_color: new FormControl<string | undefined>('#ccf3ff', [
      Validators.required,
      Validators.pattern(/^#[0-9A-F]{6}$/i),
    ]),
    icon: new FormControl<string | undefined>('info'),
    description: new FormControl<string | undefined>(''),
  });

  updateTags() {
    this.tagsService.getTags().subscribe((tags) => {
      this.tags.set(tags);
    });
  }

  constructor() {
    this.updateTags();
  }

  deleteTag(tag: Tag) {
    this.dialog
      .open(ConfirmationDialogComponent, {
        data: {
          title: 'Remove tag',
          text: `Do you really want to remove the tag '${tag.name}'? It will be removed from all projects.`,
        },
      })
      .afterClosed()
      .subscribe((result) => {
        if (!result) return;
        this.tagsService.deleteTag(tag.id).subscribe(() => {
          this.toastService.showSuccess(
            'Tag deleted',
            `Tag '${tag.name}' deleted from all projects successfully`,
          );
          this.tags()!.splice(
            this.tags()!.findIndex((t) => t.id === tag.id),
            1,
          );
          this.updateTags();
        });
      });
  }

  createNewTag() {
    this.tagsService
      .createTag(this.newTagForm.value as CreateTag)
      .subscribe((tag) => {
        this.tags.set([...(this.tags() || []), tag]);
        this.updateTags();
      });
  }
}
