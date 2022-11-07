/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, tap } from 'rxjs';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root',
})
export class BackupSettingsService {
  backupSettings?: BackupSettings = undefined;

  constructor(private http: HttpClient) {}

  getBackupSettings(): Observable<BackupSettings> {
    return this.http
      .get<BackupSettings>(environment.backend_url + '/settings/backups')
      .pipe(
        tap((backups: BackupSettings) => {
          this.backupSettings = backups;
        })
      );
  }

  updateBackupSettings(
    backupSettings: BackupSettings
  ): Observable<BackupSettings> {
    return this.http
      .put<BackupSettings>(
        environment.backend_url + '/settings/backups',
        backupSettings
      )
      .pipe(
        tap((backups: BackupSettings) => {
          this.backupSettings = backups;
        })
      );
  }
}

export type BackupSettings = {
  docker_image: string;
};
