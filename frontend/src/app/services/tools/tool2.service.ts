/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject, merge, Observable } from 'rxjs';
import { environment } from 'src/environments/environment';

export type Tool = {
  id: number;
  name: string;
};

export type Version = {
  id: number;
  name: string;
  tool_id: number;
  is_recommended: boolean;
  is_deprecated: boolean;
};

export type Type = {
  id: number;
  name: string;
  tool_id: number;
};

@Injectable({
  providedIn: 'root',
})
export class ToolService {
  constructor(private http: HttpClient) {}

  base_url = new URL('tools/', environment.backend_url + '/');

  _tools = new BehaviorSubject<Tool[] | undefined>(undefined);
  get tools(): Tool[] | undefined {
    return this._tools.getValue();
  }
  _versions = new BehaviorSubject<Version[] | undefined>(undefined);
  get versions() {
    return this._versions.getValue();
  }
  _types = new BehaviorSubject<Type[] | undefined>(undefined);
  get types() {
    return this._types.getValue();
  }

  init(): void {
    this.get_tools().subscribe();
    this.get_versions().subscribe();
    this.get_types().subscribe();
  }

  get_tools(): Observable<Tool[]> {
    let url = this.base_url;
    return this.http.get<Tool[]>(url.toString());
  }

  get_versions(): Observable<Version[]> {
    let url = new URL('versions/', this.base_url);
    return this.http.get<Version[]>(url.toString());
  }

  get_types(): Observable<Type[]> {
    let url = new URL('types/', this.base_url);
    return this.http.get<Version[]>(url.toString());
  }
}
