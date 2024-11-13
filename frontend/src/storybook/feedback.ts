/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { BehaviorSubject } from 'rxjs';
import { FeedbackConfigurationOutput } from 'src/app/openapi';
import { FeedbackWrapperService } from 'src/app/sessions/feedback/feedback.service';

export const mockFeedbackConfig: FeedbackConfigurationOutput = {
  enabled: true,
  after_session: true,
  on_footer: true,
  on_session_card: true,
  interval: {
    enabled: true,
    hours_between_prompt: 1,
  },
  recipients: [],
};

class MockFeedbackWrapperService implements Partial<FeedbackWrapperService> {
  private _feedbackConfig = new BehaviorSubject<
    FeedbackConfigurationOutput | undefined
  >(undefined);

  public readonly feedbackConfig$ = this._feedbackConfig.asObservable();

  constructor(feedbackConfig: FeedbackConfigurationOutput) {
    this._feedbackConfig.next(feedbackConfig);
  }
}

export const mockFeedbackWrapperServiceProvider = (
  feedbackConfig: FeedbackConfigurationOutput,
) => {
  return {
    provide: FeedbackWrapperService,
    useValue: new MockFeedbackWrapperService(feedbackConfig),
  };
};
