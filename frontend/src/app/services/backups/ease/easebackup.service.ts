/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { ObserversModule } from '@angular/cdk/observers';
import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root',
})
export class EASEBackupService {
  constructor(private http: HttpClient) {}

  getBackups(project: string): Observable<EASEBackup[]> {
    return this.http.get<EASEBackup[]>(
      `${environment.backend_url}/projects/${project}/extensions/backups/ease`
    );
  }

  createBackup(project: string, body: PostEASEBackup): Observable<EASEBackup> {
    return this.http.post<EASEBackup>(
      `${environment.backend_url}/projects/${project}/extensions/backups/ease`,
      body
    );
  }

  removeBackup(project: string, backup_id: number): Observable<void> {
    return this.http.delete<void>(
      `${environment.backend_url}/projects/${project}/extensions/backups/ease/${backup_id}`
    );
  }

  triggerRun(project: string, backup_id: number): Observable<EASEBackupJob> {
    return this.http.post<EASEBackupJob>(
      `${environment.backend_url}/projects/${project}/extensions/backups/ease/${backup_id}/jobs`,
      null
    );
  }

  getLogs(
    project: string,
    backup_id: number,
    job_id: string
  ): Observable<string> {
    return this.http.get<string>(
      `${environment.backend_url}/projects/${project}/extensions/backups/ease/${backup_id}/jobs/${job_id}/logs`
    );
  }

  beatifyState(state: string | undefined): EASEBackupState {
    /* Possible states are (and a few more states):
    https://github.com/kubernetes/kubernetes/blob/master/pkg/kubelet/events/event.go */

    let text = state;
    let css = 'warning';
    switch (state) {
      case 'Created':
        text = 'Created job';
        css = 'warning';
        break;
      case 'Started':
        text = 'Started job';
        css = 'success';
        break;
      case 'Failed':
      case 'FailedCreatePodContainer':
        text = 'Failed to create job';
        css = 'error';
        break;
      case 'Killing':
        text = 'Stopping job';
        css = 'error';
        break;
      case 'Preempting':
        text = 'Job is waiting in the queue';
        css = 'error';
        break;
      case 'BackOff':
        text = 'Job crashed unexpectedly';
        css = 'error';
        break;
      case 'ExceededGracePeriod':
        text = 'The job stopped.';
        css = 'error';
        break;

      case 'FailedKillPod':
        text = 'Failed to stop job';
        css = 'error';
        break;
      case 'NetworkNotReady':
        text = 'Backend network issues';
        css = 'error';
        break;
      case 'Pulling':
        text = 'Preparation of the job';
        css = 'warning';
        break;
      case 'Pulled':
        text = 'Preparation finished';
        css = 'warning';
        break;

      // Some additional reasons that came up
      case 'Scheduled':
        text = 'Next run is scheduled';
        css = 'warning';
        break;

      // Custom messages
      case 'NoJob':
        text = 'No job started yet';
        css = 'warning';
        break;

      case 'unknown':
        text = 'Unknown State';
        css = 'primary';
        break;
    }

    return {
      text: text || '',
      css,
    };
  }
}

export interface EASEBackupJob {
  id: string;
  date: string;
  state: string;
}

export interface EASEBackup extends PostEASEBackup {
  id: number;
  lastrun: EASEBackupJob;
}

export interface PostEASEBackup {
  t4cmodel: string;
  gitmodel: string;
}

export interface EASEBackupState {
  text: string;
  css: string;
}
