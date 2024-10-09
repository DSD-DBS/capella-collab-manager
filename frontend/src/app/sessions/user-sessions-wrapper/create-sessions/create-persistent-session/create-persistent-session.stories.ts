/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import {
  componentWrapperDecorator,
  Meta,
  moduleMetadata,
  StoryObj,
} from '@storybook/angular';
import { BehaviorSubject, Observable } from 'rxjs';
import { mockTool } from '../../../../../storybook/tool';
import { Tool } from '../../../../openapi';
import { ToolWrapperService } from '../../../../settings/core/tools-settings/tool.service';
import { MockLicenseUsageWrapperService } from '../../../license-indicator/license-indicator.stories';
import { LicenseUsageWrapperService } from '../../../license-indicator/license-usage.service';
import { CreatePersistentSessionComponent } from './create-persistent-session.component';

const meta: Meta<CreatePersistentSessionComponent> = {
  title: 'Session Components/Create Persistent Session',
  component: CreatePersistentSessionComponent,
  decorators: [
    componentWrapperDecorator(
      (story) =>
        `<div class="w-[360px] sm:w-[450px]">
          ${story}
        </div>`,
    ),
  ],
};

export default meta;
type Story = StoryObj<CreatePersistentSessionComponent>;

class MockToolWrapperService implements Partial<ToolWrapperService> {
  _tools = new BehaviorSubject<Tool[] | undefined>(undefined);
  get tools(): Tool[] | undefined {
    return this._tools.getValue();
  }
  get tools$(): Observable<Tool[] | undefined> {
    return this._tools.asObservable();
  }

  constructor(tools: Tool[]) {
    this._tools.next(tools);
  }
}

export const Default: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: LicenseUsageWrapperService,
          useFactory: () =>
            new MockLicenseUsageWrapperService([
              {
                id: 1,
                name: 'Test',
                usage: {
                  free: 0,
                  total: 30,
                },
                license_server_version: '',
                license_key: '',
                usage_api: '',
                instances: [],
                warnings: [],
              },
            ]),
        },
        {
          provide: ToolWrapperService,
          useFactory: () => new MockToolWrapperService([mockTool]),
        },
      ],
    }),
  ],
};
