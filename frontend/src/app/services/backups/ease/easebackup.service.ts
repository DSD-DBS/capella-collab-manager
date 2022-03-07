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

  getBackups(project: string): Observable<Array<EASEBackup>> {
    return this.http.get<Array<EASEBackup>>(
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
