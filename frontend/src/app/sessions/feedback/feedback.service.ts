/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Injectable } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import {
  FeedbackConfigurationOutput,
  FeedbackService as OpenAPIFeedbackService,
  Session,
} from '../../openapi';
import { FeedbackDialogComponent } from './feedback-dialog/feedback-dialog.component';

@Injectable({
  providedIn: 'root',
})
export class FeedbackWrapperService {
  constructor(
    private feedbackService: OpenAPIFeedbackService,
    public dialog: MatDialog,
  ) {
    this.loadFeedbackConfig().subscribe();
  }

  private _feedbackConfig = new BehaviorSubject<
    FeedbackConfigurationOutput | undefined
  >(undefined);

  public readonly feedbackConfig$ = this._feedbackConfig.asObservable();

  loadFeedbackConfig(): Observable<FeedbackConfigurationOutput> {
    return this.feedbackService
      .getFeedbackConfiguration()
      .pipe(tap((feedbackConf) => this._feedbackConfig.next(feedbackConf)));
  }

  public showDialog(sessions: Session[], trigger: string) {
    this.dialog.open(FeedbackDialogComponent, {
      data: { sessions, trigger },
      autoFocus: 'dialog',
    });
  }

  public shouldShowIntervalPrompt() {
    if (!this._feedbackConfig.value?.interval?.enabled) return false;
    const lastPrompt = localStorage.getItem('feedbackPrompt');
    if (!lastPrompt) {
      return true;
    }
    const lastPromptDate = new Date(parseInt(lastPrompt));

    const hoursInterval =
      this._feedbackConfig.value.interval.hours_between_prompt;
    const diff = new Date().getTime() - lastPromptDate.getTime();
    const hours = diff / (1000 * 60 * 60);
    if (hours >= hoursInterval) {
      return true;
    }
    return false;
  }

  public saveFeedbackPromptDate() {
    localStorage.setItem('feedbackPrompt', Date.now().toString());
  }

  public shouldShowPostSessionPrompt() {
    if (this._feedbackConfig.value?.after_session) return true;
    return false;
  }
}
