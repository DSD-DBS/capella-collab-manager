/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Injectable } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { BehaviorSubject, combineLatest, map, Observable, tap } from 'rxjs';
import {
  FeedbackAnonymityPolicy,
  FeedbackConfigurationOutput,
  FeedbackService as OpenAPIFeedbackService,
  Session,
} from '../../openapi';
import { FeedbackDialogComponent } from './feedback-dialog/feedback-dialog.component';

@Injectable({
  providedIn: 'root',
})
export class FeedbackService {
  constructor(
    private feedbackService: OpenAPIFeedbackService,
    public dialog: MatDialog,
  ) {
    this.loadFeedbackConfig().subscribe();
  }

  private _feedbackConfig = new BehaviorSubject<
    FeedbackConfigurationOutput | undefined
  >(undefined);

  loadFeedbackConfig(): Observable<FeedbackConfigurationOutput> {
    return this.feedbackService
      .getFeedback()
      .pipe(tap((feedbackConf) => this._feedbackConfig.next(feedbackConf)));
  }

  public showDialog(sessions: Session[], trigger: string) {
    this.dialog.open(FeedbackDialogComponent, {
      data: { sessions, trigger },
      autoFocus: 'dialog',
    });
  }

  // Observable for the feedback configuration
  get feedbackConfig$(): Observable<FeedbackConfigurationOutput | undefined> {
    return this._feedbackConfig.asObservable();
  }

  get enabled$(): Observable<boolean | undefined> {
    return this.feedbackConfig$.pipe(map((config) => config?.enabled));
  }

  get showOnFooter$(): Observable<boolean> {
    return combineLatest([this.enabled$, this.feedbackConfig$]).pipe(
      map(([enabled, config]) => !!enabled && !!config?.on_footer),
    );
  }

  get showOnSessionCard$(): Observable<boolean> {
    return combineLatest([this.enabled$, this.feedbackConfig$]).pipe(
      map(([enabled, config]) => !!enabled && !!config?.on_session_card),
    );
  }

  get anonymityPolicy$(): Observable<FeedbackAnonymityPolicy | undefined> {
    return this.feedbackConfig$.pipe(map((config) => config?.anonymity_policy));
  }

  public shouldShowIntervalPrompt() {
    if (!this.enabled$) return false;
    if (!this._feedbackConfig.value?.interval?.enabled) return false;
    const lastPrompt = localStorage.getItem('feedbackPrompt');
    if (!lastPrompt) {
      return true;
    }
    const lastPromptDate = new Date(parseInt(lastPrompt));

    const hoursInterval =
      this._feedbackConfig.value.interval.hours_between_prompt;
    const now = new Date();
    const diff = now.getTime() - lastPromptDate.getTime();
    const hours = diff / (1000 * 60 * 60);
    if (hours >= hoursInterval) {
      return true;
    } else {
      return false;
    }
  }

  public saveFeedbackPromptDate() {
    localStorage.setItem('feedbackPrompt', Date.now().toString());
  }

  public shouldShowPostSessionPrompt() {
    if (!this.enabled$) return false;
    if (
      !this._feedbackConfig.value?.after_session?.enabled ||
      this._feedbackConfig.value?.after_session?.percentage === 0
    ) {
      return false;
    }

    return (
      Math.random() * 100 <
      this._feedbackConfig.value?.after_session?.percentage
    );
  }
}
