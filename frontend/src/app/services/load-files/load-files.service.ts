/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { PathNode } from 'src/app/schemes';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root',
})
export class LoadFilesService {
  BACKEND_URL_PREFIX = environment.backend_url + '/sessions/';

  constructor(private http: HttpClient) {}

  upload(id: string, files: FormData): Observable<any> {
    return this.http.post<any>(this.BACKEND_URL_PREFIX + id + '/files', files, {
      reportProgress: true,
      observe: 'events',
    });
  }

  getCurrentFiles(id: string, showHiddenFiles: boolean): Observable<PathNode> {
    return this.http.get<PathNode>(
      this.BACKEND_URL_PREFIX + id + '/files?show_hidden=' + showHiddenFiles
    );
  }

  download(id: string, name: string): Observable<FormData> {
    return this.http.get<FormData>(
      this.BACKEND_URL_PREFIX + id + '/files/download',
      { params: { filename: name } }
    );
  }
}
