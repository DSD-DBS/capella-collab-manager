/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { NgClass, AsyncPipe } from '@angular/common';
import {
  ChangeDetectionStrategy,
  Component,
  Input,
  inject,
} from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatButton, MatIconButton } from '@angular/material/button';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatDialog } from '@angular/material/dialog';
import { MatIcon } from '@angular/material/icon';
import { MatTooltip } from '@angular/material/tooltip';
import { RouterLink } from '@angular/router';
import { addMinutes, differenceInMinutes } from 'date-fns';
import { NgxSkeletonLoaderModule } from 'ngx-skeleton-loader';
import { RelativeTimeComponent } from 'src/app/general/relative-time/relative-time.component';
import { Session } from 'src/app/openapi';
import { OwnUserWrapperService } from 'src/app/services/user/user.service';
import { DeleteSessionDialogComponent } from 'src/app/sessions/delete-session-dialog/delete-session-dialog.component';
import { FeedbackWrapperService } from 'src/app/sessions/feedback/feedback.service';
import {
  isPersistentSession,
  isReadonlySession,
  SessionService,
} from 'src/app/sessions/service/session.service';
import { UserSessionService } from 'src/app/sessions/service/user-session.service';
import { SessionWithSelection } from 'src/app/sessions/user-sessions-wrapper/active-sessions/active-sessions.component';
import { ConnectionDialogComponent } from 'src/app/sessions/user-sessions-wrapper/active-sessions/connection-dialog/connection-dialog.component';
import { FileBrowserDialogComponent } from 'src/app/sessions/user-sessions-wrapper/active-sessions/file-browser-dialog/file-browser-dialog.component';
import { SessionSharingDialogComponent } from 'src/app/sessions/user-sessions-wrapper/active-sessions/session-sharing-dialog/session-sharing-dialog.component';

@Component({
  selector: 'app-session-card',
  standalone: true,
  imports: [
    NgxSkeletonLoaderModule,
    RouterLink,
    MatIcon,
    NgClass,
    MatButton,
    AsyncPipe,
    MatIconButton,
    MatTooltip,
    MatCheckboxModule,
    FormsModule,
    RelativeTimeComponent,
  ],
  templateUrl: './session-card.component.html',
  styles: `
    @reference '../../../../../styles.css';

    .error {
      @apply bg-error;
    }

    .warning {
      @apply bg-warning;
    }

    .success {
      @apply bg-success;
    }

    .primary {
      @apply bg-primary;
    }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SessionCardComponent {
  sessionService = inject(SessionService);
  feedbackService = inject(FeedbackWrapperService);
  private userSessionService = inject(UserSessionService);
  private userWrapperService = inject(OwnUserWrapperService);
  private dialog = inject(MatDialog);

  @Input({ required: true }) session!: SessionWithSelection;
  @Input() hideActions = false;

  isReadonlySession = isReadonlySession;
  isPersistentSession = isPersistentSession;

  uploadFileDialog(session: Session): void {
    this.dialog.open(FileBrowserDialogComponent, { data: session });
  }

  openDeletionDialog(sessions: Session[]): void {
    const dialogRef = this.dialog.open(DeleteSessionDialogComponent, {
      data: sessions,
    });

    dialogRef.afterClosed().subscribe((result: boolean) => {
      if (result) {
        if (this.feedbackService.shouldShowPostSessionPrompt()) {
          this.feedbackService.showDialog(
            sessions,
            'After session termination',
          );
        }

        this.userSessionService.loadSessions();
      }
    });
  }

  openShareDialog(session: Session): void {
    this.dialog.open(SessionSharingDialogComponent, {
      data: session,
      maxWidth: '100%',
    });
  }

  isSessionShared(session: Session): boolean {
    return session.owner.id != this.userWrapperService.user?.id;
  }

  openConnectDialog(session: Session): void {
    this.dialog.open(ConnectionDialogComponent, {
      data: session,
    });
  }

  minutesUntilSessionTermination(session: Session): number | null {
    if (session.idle_state.available) {
      if (session.idle_state.idle_for_minutes === -1) {
        // session was never connected to, use creation time
        return (
          session.idle_state.terminate_after_minutes -
          differenceInMinutes(session.created_at, Date.now())
        );
      } else {
        return (
          session.idle_state.terminate_after_minutes -
          session.idle_state.idle_for_minutes!
        );
      }
    } else {
      return null;
    }
  }

  protected readonly Date = Date;
  protected readonly addMinutes = addMinutes;
  protected readonly differenceInMinutes = differenceInMinutes;
}
