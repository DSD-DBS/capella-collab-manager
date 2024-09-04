/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import { BehaviorSubject } from 'rxjs';
import { dialogWrapper } from 'src/storybook/decorators';
import { createPersistentSessionWithState } from '../../../../storybook/session';
import { FeedbackAnonymityPolicy } from '../../../openapi';
import { FeedbackService } from '../feedback.service';
import { FeedbackDialogComponent } from './feedback-dialog.component';

const meta: Meta<FeedbackDialogComponent> = {
  title: 'Session Components / Feedback',
  component: FeedbackDialogComponent,
  decorators: [dialogWrapper],
};

export default meta;
type Story = StoryObj<FeedbackDialogComponent>;

class mockFeedbackService implements Partial<FeedbackService> {
  readonly anonymityPolicy$ = new BehaviorSubject<FeedbackAnonymityPolicy>(
    'ask_user',
  );
}

export const NoSessions: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: MAT_DIALOG_DATA,
          useValue: { sessions: [], trigger: 'storybook' },
        },
        {
          provide: FeedbackService,
          useFactory: () => new mockFeedbackService(),
        },
      ],
    }),
  ],
};

export const OneSession: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: MAT_DIALOG_DATA,
          useValue: {
            sessions: [createPersistentSessionWithState('running')],
            trigger: 'storybook',
          },
        },
      ],
    }),
  ],
};

export const TwoSessions: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: MAT_DIALOG_DATA,
          useValue: {
            sessions: [
              createPersistentSessionWithState('running'),
              createPersistentSessionWithState('running'),
            ],
            trigger: 'storybook',
          },
        },
      ],
    }),
  ],
};
