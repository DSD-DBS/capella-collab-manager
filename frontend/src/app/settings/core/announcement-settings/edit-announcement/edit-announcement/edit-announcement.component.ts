/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Component, computed, effect, inject, input } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import {
  AbstractControl,
  FormControl,
  FormGroup,
  ReactiveFormsModule,
  ValidationErrors,
  ValidatorFn,
  Validators,
} from '@angular/forms';
import { MatOption } from '@angular/material/autocomplete';
import { MatButton } from '@angular/material/button';
import { MatCheckbox } from '@angular/material/checkbox';
import { MatError, MatFormField, MatLabel } from '@angular/material/form-field';
import { MatInput } from '@angular/material/input';
import { MatSelect } from '@angular/material/select';
import { AnnouncementWrapperService } from '../../../../../general/announcement/announcement.service';
import { AnnouncementComponent } from '../../../../../general/announcement/announcement/announcement.component';
import { ToastService } from '../../../../../helpers/toast/toast.service';
import {
  AnnouncementLevel,
  AnnouncementResponse,
  AnnouncementsService,
  CreateAnnouncementRequest,
} from '../../../../../openapi';

@Component({
  selector: 'app-edit-announcement',
  imports: [
    MatError,
    MatFormField,
    MatInput,
    MatLabel,
    MatOption,
    MatSelect,
    ReactiveFormsModule,
    AnnouncementComponent,
    MatButton,
    MatCheckbox,
  ],
  templateUrl: './edit-announcement.component.html',
})
export class EditAnnouncementComponent {
  public existingAnnouncement = input<AnnouncementResponse>();
  private announcementService = inject(AnnouncementsService);
  announcementWrapperService = inject(AnnouncementWrapperService);
  private toastService = inject(ToastService);

  announcementForm = new FormGroup(
    {
      title: new FormControl(''),
      message: new FormControl(''),
      level: new FormControl('', Validators.required),
      dismissible: new FormControl(true),
    },
    this.titleOrDescriptionRequired(),
  );
  title = toSignal(this.announcementForm.controls.title.valueChanges);
  message = toSignal(this.announcementForm.controls.message.valueChanges);
  level = toSignal(this.announcementForm.controls.level.valueChanges);
  dismissible = toSignal(
    this.announcementForm.controls.dismissible.valueChanges,
  );

  displayedAnnouncement = computed<AnnouncementResponse>(() => {
    return {
      id: this.existingAnnouncement()?.id || 0,
      title: this.title() ?? '',
      message:
        this.message() ??
        (!this.message() && !this.title()
          ? 'Write some text above to preview your announcement'
          : ''),
      level: (this.level() as AnnouncementLevel) ?? AnnouncementLevel.Info,
      dismissible: this.dismissible() ?? true,
    };
  });

  constructor() {
    effect(() => {
      if (this.existingAnnouncement()) {
        this.announcementForm.patchValue(this.existingAnnouncement()!);
      }
    });
  }

  announcementLevels = computed(() => {
    return Object.values(AnnouncementLevel);
  });

  titleOrDescriptionRequired(): ValidatorFn {
    return (control: AbstractControl): ValidationErrors | null => {
      if (control.get('title')?.value || control.get('message')?.value) {
        control.get('message')?.setErrors(null);
        return null;
      }
      control.get('message')?.setErrors({ titleOrDescriptionAvailable: true });
      return { titleOrDescriptionAvailable: true };
    };
  }

  createAnnouncement(): void {
    if (this.announcementForm.valid && !this.existingAnnouncement()) {
      this.announcementService
        .createAnnouncement(
          this.announcementForm.value as CreateAnnouncementRequest,
        )
        .subscribe({
          next: () => {
            this.toastService.showSuccess(
              'Announcement created',
              'The announcement has been created successfully',
            );
            this.announcementWrapperService.refreshAnnouncements();
            this.announcementForm.reset({
              title: '',
              message: '',
              level: '',
              dismissible: true,
            });
          },
        });
    }
  }

  updateAnnouncement(): void {
    if (this.announcementForm.valid && this.existingAnnouncement()) {
      this.announcementService
        .updateAnnouncement(
          this.existingAnnouncement()!.id,
          this.announcementForm.value as CreateAnnouncementRequest,
        )
        .subscribe({
          next: () => {
            this.toastService.showSuccess(
              'Announcement updated',
              'The announcement has been updated successfully',
            );
            this.announcementWrapperService.refreshAnnouncements();
          },
        });
    }
  }

  deleteAnnouncement(): void {
    if (this.existingAnnouncement()) {
      this.announcementService
        .deleteAnnouncement(this.existingAnnouncement()!.id)
        .subscribe({
          next: () => {
            this.toastService.showSuccess(
              'Announcement deleted',
              'The announcement has been deleted successfully',
            );
            this.announcementWrapperService.refreshAnnouncements();
          },
        });
    }
  }
}
