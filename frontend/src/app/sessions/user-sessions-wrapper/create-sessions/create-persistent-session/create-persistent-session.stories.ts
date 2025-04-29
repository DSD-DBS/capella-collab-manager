/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { HttpEvent, HttpResponse } from '@angular/common/http';
import {
  componentWrapperDecorator,
  Meta,
  moduleMetadata,
  StoryObj,
} from '@storybook/angular';
import { userEvent, within } from '@storybook/test';
import { BehaviorSubject, Observable, of } from 'rxjs';
import {
  defaultToolConfig,
  mockCapellaTool,
  mockCapellaToolVersion,
  mockHttpConnectionMethod,
} from '../../../../../storybook/tool';
import { Tool, ToolsService, ToolVersion } from '../../../../openapi';
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
        `<div class="w-full sm:w-[450px]">
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
          useFactory: () => new MockToolWrapperService([mockCapellaTool]),
        },
      ],
    }),
  ],
};

export const WithError: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: ToolWrapperService,
          useFactory: () => new MockToolWrapperService([mockCapellaTool]),
        },
      ],
    }),
  ],
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const requestSessionButton = canvas.getByTestId('create-session-button');
    await userEvent.click(requestSessionButton);
  },
};

class MockToolsService implements Partial<ToolsService> {
  public getToolVersions(toolId: number): Observable<ToolVersion[]>;
  public getToolVersions(
    toolId: number,
  ): Observable<HttpResponse<ToolVersion[]>>;
  public getToolVersions(toolId: number): Observable<HttpEvent<ToolVersion[]>>;
  // eslint-disable-next-line @typescript-eslint/no-unused-vars, @typescript-eslint/no-explicit-any
  public getToolVersions(toolId: number): Observable<any> {
    return of([mockCapellaToolVersion]);
  }
}

export const WithSelection: Story = {
  args: {
    versions: [mockCapellaToolVersion],
  },
  parameters: {
    screenshot: {
      delay: 1000,
    },
  },
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: ToolWrapperService,
          useValue: new MockToolWrapperService([
            {
              ...mockCapellaTool,
              config: {
                ...defaultToolConfig,
                connection: {
                  methods: [
                    {
                      ...mockHttpConnectionMethod,
                      name: 'Xpra',

                      description:
                        'This is the description of the Xpra connection method',
                    },
                    {
                      ...mockHttpConnectionMethod,
                      name: 'Guacamole',
                      id: 'guacamole',
                      description:
                        'This is the description of the Guacamole connection method',
                    },
                  ],
                },
              },
            },
          ]),
        },
        {
          provide: ToolsService,
          useValue: new MockToolsService(),
        },
      ],
    }),
  ],
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const toolSelection = canvas.getByTestId('tool-select');
    await userEvent.click(toolSelection);
    await new Promise((resolve) => setTimeout(resolve, 100));
    const capellaOption = document.querySelector(
      '[data-testid=tool-select-option-1]',
    );
    await userEvent.click(capellaOption!);
  },
};
