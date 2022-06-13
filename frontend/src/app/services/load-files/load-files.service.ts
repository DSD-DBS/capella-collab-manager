// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
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

  getCurrentFiles(id: string): Observable<FileTree> {
    return this.http.get<FileTree>(this.BACKEND_URL_PREFIX + id + '/files');
  }
}

export interface FileTree {
  path: string;
  name: string;
  type: 'file' | 'directory';
  children: FileTree[] | null;
  newFile: boolean;
}
