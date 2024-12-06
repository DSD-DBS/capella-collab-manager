/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Injectable } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { map, take } from 'rxjs';
import { filter } from 'rxjs/operators';
import { AuthenticationWrapperService } from 'src/app/services/auth/auth.service';
import { FeedbackConfigurationOutput, Session } from '../../openapi';
import { UnifiedConfigWrapperService } from '../../services/unified-config-wrapper/unified-config-wrapper.service';
import { FeedbackDialogComponent } from './feedback-dialog/feedback-dialog.component';

@Injectable({
  providedIn: 'root',
})
export class FeedbackWrapperService {
  constructor(
    public dialog: MatDialog,
    private authService: AuthenticationWrapperService,
    public unifiedConfigWrapperService: UnifiedConfigWrapperService,
  ) {
    this.unifiedConfigWrapperService.unifiedConfig$.subscribe(() => {
      this.triggerFeedbackPrompt();
    });
  }

  public readonly feedbackConfig$ =
    this.unifiedConfigWrapperService.unifiedConfig$.pipe(
      map((unifiedConfig) => unifiedConfig?.feedback),
    );

  triggerFeedbackPrompt(): void {
    if (!this.authService.isLoggedIn()) return;
    this.feedbackConfig$.pipe(filter(Boolean), take(1)).subscribe((config) => {
      if (this.shouldShowIntervalPrompt(config)) {
        this.showDialog([], 'On interval');
        this.saveFeedbackPromptDate();
      }
    });
  }

  public showDialog(sessions: Session[], trigger: string) {
    this.dialog.open(FeedbackDialogComponent, {
      data: { sessions, trigger },
      autoFocus: 'dialog',
    });
  }

  public shouldShowIntervalPrompt(config: FeedbackConfigurationOutput) {
    if (!config?.interval?.enabled) return false;
    const lastPrompt = localStorage.getItem('feedbackPrompt');
    if (!lastPrompt) {
      return true;
    }
    const lastPromptDate = new Date(parseInt(lastPrompt));

    const hoursInterval = config.interval.hours_between_prompt;
    const diff = new Date().getTime() - lastPromptDate.getTime();
    const hours = diff / (1000 * 60 * 60);
    return hours >= hoursInterval;
  }

  public saveFeedbackPromptDate() {
    localStorage.setItem('feedbackPrompt', Date.now().toString());
  }

  public shouldShowPostSessionPrompt() {
    return !!this.unifiedConfigWrapperService.unifiedConfig?.feedback
      ?.after_session;
  }
}
