import { THIS_EXPR } from '@angular/compiler/src/output/output_ast';
import { Component, Input, OnInit } from '@angular/core';
import { Subscription, timer } from 'rxjs';
import { map } from 'rxjs/operators';
import { Session } from '../schemes';
import { BeautifyService } from '../services/beatify/beautify.service';
import { OwnSessionService } from '../services/own-session/own-session.service';

@Component({
  selector: 'app-session-creation-progress',
  templateUrl: './session-creation-progress.component.html',
  styleUrls: ['./session-creation-progress.component.css'],
})
export class SessionCreationProgressComponent implements OnInit {
  @Input()
  sessionType = '';

  @Input()
  session: Session | undefined = undefined;

  refreshSessionsSubscription: Subscription;

  containerReady = false;

  constructor(
    private ownSessionService: OwnSessionService,
    public beautifyService: BeautifyService
  ) {
    this.refreshSessionsSubscription = timer(0, 2000)
      .pipe(
        map(() => {
          if (this.session !== undefined) {
            this.ownSessionService
              .refreshSessions()
              .subscribe((res: Array<Session>) => {
                const session = res.find(
                  (session: Session) => session.id === this.session?.id
                );

                if (session !== undefined) {
                  this.session = JSON.parse(JSON.stringify(session));
                }

                if (this.session?.state === 'Running') {
                  this.containerReady = true;
                  this.refreshSessionsSubscription.unsubscribe();
                }
              });
          }
        })
      )
      .subscribe();
  }

  ngOnInit(): void {}
}
