/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { AsyncPipe } from '@angular/common';
import { Component, Inject } from '@angular/core';
import {
  FormControl,
  FormGroup,
  FormsModule,
  ReactiveFormsModule,
  Validators,
} from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCheckbox } from '@angular/material/checkbox';
import {
  MAT_DIALOG_DATA,
  MatDialogActions,
  MatDialogClose,
  MatDialogContent,
  MatDialogRef,
  MatDialogTitle,
} from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIcon } from '@angular/material/icon';
import { MatInput } from '@angular/material/input';
import { MetadataService } from '../../../general/metadata/metadata.service';
import {
  AnonymizedSession,
  Feedback,
  FeedbackService as OpenAPIFeedbackService,
  Session,
} from '../../../openapi';
import { FeedbackService } from '../feedback.service';

interface DialogData {
  sessions: Session[];
  trigger: string;
}

@Component({
  selector: 'app-feedback',
  standalone: true,
  imports: [
    MatButtonModule,
    MatIcon,
    MatFormFieldModule,
    MatCheckbox,
    MatDialogTitle,
    MatDialogContent,
    MatDialogActions,
    MatInput,
    MatDialogClose,
    ReactiveFormsModule,
    FormsModule,
    AsyncPipe,
  ],
  templateUrl: './feedback-dialog.component.html',
})
export class FeedbackDialogComponent {
  feedbackForm = new FormGroup({
    rating: new FormControl<'good' | 'okay' | 'bad' | undefined>(
      undefined,
      Validators.required,
    ),
    feedbackText: new FormControl<string>(''),
    shareContact: new FormControl<boolean>(false),
  });

  constructor(
    @Inject(MAT_DIALOG_DATA) public data: DialogData,
    public dialogRef: MatDialogRef<FeedbackDialogComponent>,
    public metadataService: MetadataService,
    public openApiFeedbackService: OpenAPIFeedbackService,
    public feedbackService: FeedbackService,
  ) {}

  setRating(rating: 'good' | 'okay' | 'bad') {
    this.feedbackForm.get('rating')?.setValue(rating);
    this.feedbackForm.get('rating')?.markAsTouched();
    this.feedbackForm.get('rating')?.markAsDirty();
    if (rating === 'good') {
      this.feedbackForm.get('feedbackText')?.reset();
      this.feedbackForm.get('shareContact')?.reset();
    }
  }

  submitButton = {
    disabled: false,
    text: 'Submit',
  };

  submit() {
    if (this.feedbackForm.invalid) {
      return;
    }

    this.submitButton.text = 'Submitting...';
    this.submitButton.disabled = true;

    const _sessionData: AnonymizedSession[] = this.data.sessions.map(
      (session) => ({
        ...session,
        owner: null,
        shared_with: null,
      }),
    );

    const feedback: Feedback = {
      rating: this.feedbackForm.get('rating')!.value!,
      feedback_text: this.feedbackForm.get('feedbackText')?.value || null,
      share_contact: this.feedbackForm.get('shareContact')?.value || false,
      sessions: _sessionData,
      trigger: this.data.trigger,
    };

    this.openApiFeedbackService.submitFeedback(feedback).subscribe({
      next: () => {
        this.dialogRef.close();
      },
      error: () => {
        this.submitButton.text = 'Try again.';
        this.submitButton.disabled = false;
      },
    });
  }
}
