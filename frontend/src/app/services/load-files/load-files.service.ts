/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { HttpClient, HttpEvent } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { PathNode } from 'src/app/sessions/service/session.service';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root',
})
export class LoadFilesService {
  BACKEND_URL_PREFIX = environment.backend_url + '/sessions';

  constructor(private http: HttpClient) {}

  upload(id: string, files: FormData): Observable<HttpEvent<UploadResponse>> {
    return this.http.post<UploadResponse>(
      `${this.BACKEND_URL_PREFIX}/${id}/files`,
      files,
      {
        reportProgress: true,
        observe: 'events',
      },
    );
  }

  getCurrentFiles(id: string, showHiddenFiles: boolean): Observable<PathNode> {
    return this.http.get<PathNode>(
      `${this.BACKEND_URL_PREFIX}/${id}/files?show_hidden=${showHiddenFiles}`,
    );
  }

  download(id: string, filename: string): Observable<Blob> {
    return this.http.get(`${this.BACKEND_URL_PREFIX}/${id}/files/download`, {
      params: { filename: filename },
      responseType: 'blob',
    });
  }
}

export type UploadResponse = {
  message: string;
};
