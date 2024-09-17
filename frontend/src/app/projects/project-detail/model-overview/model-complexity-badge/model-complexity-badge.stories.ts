/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, StoryObj } from '@storybook/angular';
import { base64ModelBadge } from 'src/storybook/model-badge';
import { ModelComplexityBadgeComponent } from './model-complexity-badge.component';

const meta: Meta<ModelComplexityBadgeComponent> = {
  title: 'Model Components/Model Complexity Badge',
  component: ModelComplexityBadgeComponent,
  parameters: {
    chromatic: { viewports: [500] },
    screenshot: {
      viewport: {
        height: 150,
        width: 500,
      },
      viewports: [],
    },
  },
};

export default meta;
type Story = StoryObj<ModelComplexityBadgeComponent>;

export const Successful: Story = {
  args: {
    complexityBadge: base64ModelBadge,
    loadingComplexityBadge: false,
  },
};

export const NoJobConfigured: Story = {
  args: {
    errorCode: 'FILE_NOT_FOUND',
    errorMessage:
      "No file with the name 'model badge' found in the linked Git repository.",
    loadingComplexityBadge: false,
  },
};

export const Loading: Story = {
  args: {
    loadingComplexityBadge: true,
  },
};

export const GitInstanceEndpointUndefined: Story = {
  args: {
    errorCode: 'GIT_INSTANCE_NO_API_ENDPOINT_DEFINED',
    errorMessage:
      'The used Git instance has no API endpoint defined. Please contact your administrator.',
    loadingComplexityBadge: false,
  },
};

export const PipelineJobNotFound: Story = {
  args: {
    errorCode: 'PIPELINE_JOB_NOT_FOUND',
    errorMessage:
      "There was no job with the name 'generate-model-badge' in the last 20 runs of the pipelines with revision 'main'. Please contact your administrator.",
    loadingComplexityBadge: false,
  },
};
