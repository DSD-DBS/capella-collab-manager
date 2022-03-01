import { Component, OnInit } from '@angular/core';
import { SessionsUsage } from 'src/app/schemes';
import { SessionService } from 'src/app/services/session/session.service';

@Component({
  selector: 'app-licences',
  templateUrl: './licences.component.html',
  styleUrls: ['./licences.component.css'],
})
export class LicencesComponent implements OnInit {
  constructor(private sessionService: SessionService) {}

  ngOnInit(): void {
    this.sessionService.getSessionsUsage().subscribe((res) => {
      this.sessionsUsage = res;
    });
  }

  sessionsUsage: SessionsUsage | undefined = undefined;

  getErrorMessage(error: string): string {
    switch (error) {
      case 'T4C_ERROR':
        return 'Internal server error in the license server.';
      case 'TIMEOUT':
        return 'The connection to the license server timed out.';
      case 'CONNECTION_ERROR':
        return 'The connection to the license server failed.';
      case 'NO_STATUS':
        return 'No status is available. This can happend during license server restarts.';
      case 'DECODE_ERROR':
        return 'License server response could not be decoded.';
      default:
        return 'Unknown error. Please contact your system administrator.';
    }
  }
}
