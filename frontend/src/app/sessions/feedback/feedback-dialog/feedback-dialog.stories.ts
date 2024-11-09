/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import { userEvent, within } from '@storybook/test';
import { dialogWrapper } from 'src/storybook/decorators';
import { mockPersistentSession } from '../../../../storybook/session';
import { FeedbackDialogComponent } from './feedback-dialog.component';

const meta: Meta<FeedbackDialogComponent> = {
  title: 'Session Components/Feedback',
  component: FeedbackDialogComponent,
  decorators: [dialogWrapper],
};

export default meta;
type Story = StoryObj<FeedbackDialogComponent>;

export const NoSessions: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: MAT_DIALOG_DATA,
          useValue: { sessions: [], trigger: 'storybook' },
        },
      ],
    }),
  ],
};

export const RatingSelected: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: MAT_DIALOG_DATA,
          useValue: { sessions: [], trigger: 'storybook' },
        },
      ],
    }),
  ],
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const badRating = canvas.getByTestId('rating-bad');
    await userEvent.click(badRating);
  },
};

export const OneSession: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: MAT_DIALOG_DATA,
          useValue: {
            sessions: [mockPersistentSession],
            trigger: 'storybook',
          },
        },
      ],
    }),
  ],
};

export const OneSessionWithUserInformation: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: MAT_DIALOG_DATA,
          useValue: {
            sessions: [mockPersistentSession],
            trigger: 'storybook',
          },
        },
      ],
    }),
  ],
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const goodRating = canvas.getByTestId('rating-good');
    await userEvent.click(goodRating);
    const feedbackText = canvas.getByTestId('feedback-text');
    await userEvent.type(
      feedbackText,
      'I absolutely love the Capella Collaboration Manager! Such a great tool!',
    );
    const shareUserInformationCheckbox = canvas.getByTestId(
      'share-user-information',
    );
    await userEvent.click(shareUserInformationCheckbox);
  },
};

export const TwoSessions: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: MAT_DIALOG_DATA,
          useValue: {
            sessions: [mockPersistentSession, mockPersistentSession],
            trigger: 'storybook',
          },
        },
      ],
    }),
  ],
};
