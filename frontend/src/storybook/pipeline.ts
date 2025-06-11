/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { BehaviorSubject } from 'rxjs';
import { PipelineRun } from 'src/app/openapi';
import {
  PageWrapperPipelineRun,
  PipelineRunWrapperService,
} from 'src/app/projects/models/backup-settings/pipeline-runs/service/pipeline-run.service';

class MockPipelineRunWrapperService
  implements Partial<PipelineRunWrapperService>
{
  private _pipelineRun = new BehaviorSubject<PipelineRun | undefined>(
    undefined,
  );
  public readonly pipelineRun$ = this._pipelineRun.asObservable();

  private _pipelineRunPages = new BehaviorSubject<PageWrapperPipelineRun>({
    pages: [],
    total: undefined,
  });
  public readonly pipelineRunPages$ = this._pipelineRunPages.asObservable();

  constructor(
    pipelineRun: PipelineRun | undefined = undefined,
    pipelineRuns: PipelineRun[] | undefined = undefined,
  ) {
    this._pipelineRun.next(pipelineRun);

    if (pipelineRuns === undefined) {
      this._pipelineRunPages.next({
        pages: [],
        total: undefined,
      });
      return;
    }
    this._pipelineRunPages.next({
      pages: [
        {
          items: pipelineRuns,
          total: null,
          page: null,
          size: null,
          pages: null,
        },
        'loading',
      ],
      total: undefined,
    });
  }
}

export const mockPipelineRunWrapperServiceProvider = (
  pipelineRun: PipelineRun | undefined = undefined,
  pipelineRuns: PipelineRun[] | undefined = undefined,
) => {
  return {
    provide: PipelineRunWrapperService,
    useValue: new MockPipelineRunWrapperService(pipelineRun, pipelineRuns),
  };
};
