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
      `${environment.backend_url}/projects/${project}/extensions/backups/git`
    );
  }
}

export interface EASEBackupJob {
  id: string;
  date: string;
  state: string;
}

export interface EASEBackup {
  id: number;
  t4cmodel: string;
  gitmodel: string;
  lastrun: EASEBackupJob;
}
