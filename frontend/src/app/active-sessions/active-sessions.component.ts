import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { DeleteSessionDialogComponent } from '../delete-session-dialog/delete-session-dialog.component';
import { Session } from '../schemes';
import { SessionService } from '../services/session/session.service';
import { UserService } from '../services/user/user.service';
import { ReconnectDialogComponent } from './reconnect-dialog/reconnect-dialog.component';

@Component({
  selector: 'app-active-sessions',
  templateUrl: './active-sessions.component.html',
  styleUrls: ['./active-sessions.component.css'],
})
export class ActiveSessionsComponent implements OnInit {
  sessions: Array<Session> = [];
  showSpinner = false;

  constructor(private userService: UserService, private dialog: MatDialog) {}

  ngOnInit(): void {
    this.refreshSessions();
  }

  refreshSessions() {
    this.showSpinner = true;
    this.userService.getOwnActiveSessions().subscribe((res: Array<Session>) => {
      this.sessions = res;
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
}
