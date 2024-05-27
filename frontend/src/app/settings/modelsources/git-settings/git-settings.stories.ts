/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { AsyncValidatorFn, ValidationErrors } from '@angular/forms';
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import { Observable, of } from 'rxjs';
import {
  GitInstance,
  GitInstancesService,
} from 'src/app/settings/modelsources/git-settings/service/git-instances.service';
import { GitSettingsComponent } from './git-settings.component';

const meta: Meta<GitSettingsComponent> = {
  title: 'Settings Components / Modelsources / Git Instances',
  component: GitSettingsComponent,
};

export default meta;
type Story = StoryObj<GitSettingsComponent>;

class MockGitInstancesService implements Partial<GitInstancesService> {
  public readonly gitInstances$: Observable<GitInstance[] | undefined> =
    of(undefined);

  constructor(gitInstances?: GitInstance[] | undefined) {
    this.gitInstances$ = of(gitInstances);
  }

  asyncNameValidator(): AsyncValidatorFn {
    return (): Observable<ValidationErrors | null> => {
      return of(null);
    };
  }
}

export const General: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: GitInstancesService,
          useFactory: () =>
            new MockGitInstancesService([
              {
                id: 1,
                name: 'GitLab example',
                url: 'https://gitlab.com',
                apiURL: 'https://gitlab.com/api/v4',
                type: 'gitlab',
              },
              {
                id: 2,
                name: 'GitHub example',
                url: 'https://github.com',
                apiURL: 'https://api.github.com',
                type: 'github',
              },
              {
                id: 3,
                name: 'General example',
                url: 'https://example.com',
                type: 'general',
              },
            ]),
        },
      ],
    }),
  ],
};
