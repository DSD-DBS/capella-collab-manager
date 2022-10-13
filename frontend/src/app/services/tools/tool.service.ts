/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import { environment } from 'src/environments/environment';

export type Tool = {
  id: number;
  name: string;
};

export type ToolVersion = {
  id: number;
  name: string;
  is_recommended: boolean;
  is_deprecated: boolean;
};

export type ToolType = {
  id: number;
  name: string;
};

@Injectable({
  providedIn: 'root',
})
export class ToolService {
  constructor(private http: HttpClient) {}

  base_url = environment.backend_url + '/tools/';

  _tools = new BehaviorSubject<Tool[] | undefined>(undefined);
  get tools(): Tool[] | undefined {
    return this._tools.getValue();
  }

  init(): void {
    this.getTools().subscribe();
  }

  getTools(): Observable<Tool[]> {
    return this.http.get<Tool[]>(this.base_url.toString()).pipe(
      tap((tools: Tool[]) => {
        this._tools.next(tools);
      })
    );
  }

  getVersionsForTool(toolId: number): Observable<ToolVersion[]> {
    return this.http.get<ToolVersion[]>(`${this.base_url}${toolId}/versions/`);
  }

  getTypesForTool(toolId: number): Observable<ToolType[]> {
    return this.http.get<ToolVersion[]>(`${this.base_url}${toolId}/types/`);
  }
}
