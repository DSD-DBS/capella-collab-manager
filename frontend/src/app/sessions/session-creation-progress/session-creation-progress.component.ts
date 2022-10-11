/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Input, OnDestroy, OnInit } from '@angular/core';
import { Subscription, timer } from 'rxjs';
import { map } from 'rxjs/operators';
import { Session } from '../../schemes';
import { BeautifyService } from '../../services/beatify/beautify.service';
import { OwnSessionService } from '../../services/own-session/own-session.service';
import { SessionService } from '../../services/session/session.service';

@Component({
  selector: 'app-session-creation-progress',
  templateUrl: './session-creation-progress.component.html',
  styleUrls: ['./session-creation-progress.component.css'],
})
export class SessionCreationProgressComponent implements OnInit, OnDestroy {
  @Input()
  sessionType = '';

  @Input()
  session: Session | undefined = undefined;

  failure = false;

  refreshSessionsSubscription: Subscription;

  containerReady = false;

  constructor(
    private ownSessionService: OwnSessionService,
    public beautifyService: BeautifyService,
    public sessionService: SessionService
  ) {
    this.refreshSessionsSubscription = timer(0, 2000)
      .pipe(
        map(() => {
          if (this.session !== undefined) {
            this.ownSessionService.refreshSessions().subscribe(
              (res: Session[]) => {
                const session = res.find(
                  (session: Session) => session.id === this.session?.id
                );

                if (session !== undefined) {
                  this.session = JSON.parse(JSON.stringify(session));
                }

                if (
                  this.session?.state === 'Started' ||
                  this.session?.state === 'START_SESSION'
                ) {
                  this.containerReady = true;
                  this.refreshSessionsSubscription.unsubscribe();
                }
              },
              (err) => {
                this.refreshSessionsSubscription.unsubscribe();
                this.failure = true;
              }
            );
          }
        })
      )
      .subscribe();
  }

  evaluateStep(step: string): string {
    const splittedState = this.session?.state.split('_');
    if (splittedState != null && splittedState.length >= 2) {
      const type = splittedState[0];
      const detectedStep = splittedState.slice(1).join('_');
      const stepOrder = [
        'INITIAL',
        'LOAD_MODEL',
        'PREPARE_WORKSPACE',
        'SESSION',
      ];
      if (stepOrder.indexOf(step) < stepOrder.indexOf(detectedStep)) {
        return 'success';
      } else if (step === detectedStep) {
        switch (type) {
          case 'START':
            return 'running';
          case 'FAILURE':
            this.refreshSessionsSubscription.unsubscribe();
            return 'error';
          case 'FINISH':
            return 'success';
          default:
            return 'error';
        }
      } else {
        return 'pending';
      }
    } else {
      if (step == 'INITIAL') {
        return 'running';
      } else {
        return 'pending';
      }
    }
  }

  ngOnInit(): void {}

  ngOnDestroy(): void {
    this.refreshSessionsSubscription.unsubscribe();
  }
}
