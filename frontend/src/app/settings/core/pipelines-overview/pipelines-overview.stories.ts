/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import { BehaviorSubject, Observable } from 'rxjs';
import {
  mockGeneralHealthBad,
  mockGeneralHealthGood,
  mockProjectStatusesBad,
  mockProjectStatusesGood,
  mockToolmodelStatusesBad,
  mockToolmodelStatusesGood,
} from '../../../../storybook/monitoring';
import { PipelinesOverviewComponent } from './pipelines-overview.component';
import {
  GeneralHealth,
  MonitoringService,
  ProjectStatus,
  ToolmodelStatus,
} from './service/monitoring.service';

const meta: Meta<PipelinesOverviewComponent> = {
  title: 'Settings Components/Pipelines Overview',
  component: PipelinesOverviewComponent,
};

export default meta;
type Story = StoryObj<PipelinesOverviewComponent>;

class MockMonitoringService {
  private _generalHealth = new BehaviorSubject<GeneralHealth | undefined>(
    undefined,
  );
  private _toolmodelStatuses = new BehaviorSubject<
    ToolmodelStatus[] | undefined
  >(undefined);
  private _projectStatuses = new BehaviorSubject<ProjectStatus[] | undefined>(
    undefined,
  );

  public readonly generalHealth$ = this._generalHealth.asObservable();
  public readonly toolmodelStatuses$ = this._toolmodelStatuses.asObservable();
  public readonly projectStatuses$ = this._projectStatuses.asObservable();

  constructor(
    generalHealth: GeneralHealth | undefined,
    toolmodelStatuses: ToolmodelStatus[] | undefined,
    projectStatuses: ProjectStatus[] | undefined,
  ) {
    this._generalHealth.next(generalHealth);
    this._toolmodelStatuses.next(toolmodelStatuses);
    this._projectStatuses.next(projectStatuses);
  }

  fetchGeneralHealth(): Observable<GeneralHealth | undefined> {
    return this.generalHealth$;
  }

  fetchModelHealth(): Observable<ToolmodelStatus[] | undefined> {
    return this.toolmodelStatuses$;
  }

  fetchProjectHealth(): Observable<ProjectStatus[] | undefined> {
    return this.projectStatuses$;
  }
}

export const Loading: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: MonitoringService,
        },
      ],
    }),
  ],
};

export const GoodHealth: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: MonitoringService,
          useFactory: () =>
            new MockMonitoringService(
              mockGeneralHealthGood,
              mockToolmodelStatusesGood,
              mockProjectStatusesGood,
            ),
        },
      ],
    }),
  ],
};

export const BadHealth: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: MonitoringService,
          useFactory: () =>
            new MockMonitoringService(
              mockGeneralHealthBad,
              mockToolmodelStatusesBad,
              mockProjectStatusesBad,
            ),
        },
      ],
    }),
  ],
};
