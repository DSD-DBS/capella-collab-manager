import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { DeleteSessionDialogComponent } from '../delete-session-dialog/delete-session-dialog.component';
import { Session } from '../schemes';
import { OwnSessionService } from '../services/own-session/own-session.service';
import { UserService } from '../services/user/user.service';
import { ReconnectDialogComponent } from './reconnect-dialog/reconnect-dialog.component';

@Component({
  selector: 'app-active-sessions',
  templateUrl: './active-sessions.component.html',
  styleUrls: ['./active-sessions.component.css'],
})
export class ActiveSessionsComponent implements OnInit {
  showSpinner = false;

  constructor(
    public ownSessionService: OwnSessionService,
    private dialog: MatDialog
  ) {}

  ngOnInit(): void {
    this.refreshSessions();
  }

  refreshSessions() {
    this.showSpinner = true;
    this.ownSessionService.refreshSessions().subscribe(() => {
      this.showSpinner = false;
    });
  }

  openDeletionDialog(sessions: Array<Session>): void {
    const dialogRef = this.dialog.open(DeleteSessionDialogComponent, {
      data: sessions,
    });

    dialogRef.afterClosed().subscribe((_) => {
      this.refreshSessions();
    });
  }

  openReconnectDialog(session: Session): void {
    this.dialog.open(ReconnectDialogComponent, {
      data: session,
    });
  }

  beatifyDate(date: string): string {
    const newDate = new Date(date);
    const now = new Date();
    let newDateString = '';
    if (
      newDate.getFullYear() == now.getFullYear() &&
      newDate.getMonth() == now.getMonth() &&
      newDate.getDate() == now.getDate()
    ) {
      newDateString = 'today';
    } else {
      newDateString =
        'on ' +
        newDate.toLocaleDateString(undefined, {
          year: 'numeric',
          month: 'numeric',
          day: 'numeric',
        });
    }

    return (
      newDateString +
      ' at ' +
      newDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    );
  }

  beatifyState(state: string): SessionState {
    let text = state;
    let css = 'warning';
    switch (state) {
      case '404':
        text = 'Error: Session not found';
        css = 'error';
        break;
      case 'pending':
        text = 'Waiting for resources';
        css = 'warning';
        break;
      case 'ImagePullBackOff':
      case 'ErrImagePull':
        text = 'Failed to pull image';
        css = 'error';
        break;
      case 'ContainerCreating':
        text = 'Creating session';
        css = 'warning';
        break;
      case 'Running':
        text = 'Running';
        css = 'success';
        break;
    }

    return {
      text: text,
      css: css,
    };
  }
}

interface SessionState {
  text: string;
  css: string;
}
