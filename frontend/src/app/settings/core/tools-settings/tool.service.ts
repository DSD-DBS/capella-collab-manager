/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import { environment } from 'src/environments/environment';

export type CreateTool = {
  name: string;
};

export type Tool = CreateTool & {
  id: number;
};

export type ToolVersion = {
  id: number;
  name: string;
  is_recommended: boolean;
  is_deprecated: boolean;
};

export interface ToolType {
  id: number;
  name: string;
}

export type ToolExtended = {
  types: ToolType[];
  versions: ToolVersion[];
};

export type ToolDockerimages = {
  persistent: string;
  readonly: string;
};

@Injectable({
  providedIn: 'root',
})
export class ToolService {
  constructor(private http: HttpClient) {}

  baseURL = environment.backend_url + '/tools';

  _tools = new BehaviorSubject<Tool[] | undefined>(undefined);
  get tools(): Tool[] | undefined {
    return this._tools.getValue();
  }

  init(): void {
    this.getTools().subscribe();
  }

  getTools(): Observable<Tool[]> {
    return this.http.get<Tool[]>(this.baseURL).pipe(
      tap((tools: Tool[]) => {
        this._tools.next(tools);
      })
    );
  }

  createTool(name: string): Observable<Tool> {
    return this.http.post<Tool>(this.baseURL, { name });
  }

  updateTool(toolId: number, toolName: string): Observable<Tool> {
    return this.http.put<Tool>(`${this.baseURL}/${toolId}`, {
      name: toolName,
    });
  }

  deleteTool(tool_id: number): Observable<void> {
    return this.http.delete<void>(`${this.baseURL}/${tool_id}`);
  }

  getVersionsForTool(toolId: number): Observable<ToolVersion[]> {
    return this.http.get<ToolVersion[]>(`${this.baseURL}/${toolId}/versions`);
  }

  createVersionForTool(toolId: number, name: string): Observable<ToolVersion> {
    return this.http.post<ToolVersion>(`this.baseURL/${toolId}/versions`, {
      name,
    });
  }

  deleteVersionForTool(
    toolId: number,
    toolVersion: ToolVersion
  ): Observable<void> {
    return this.http.delete<void>(
      `${this.baseURL}/${toolId}/versions/${toolVersion.id}`
    );
  }

  getTypesForTool(toolId: number): Observable<ToolType[]> {
    return this.http.get<ToolVersion[]>(`${this.baseURL}/${toolId}/types`);
  }

  createTypeForTool(toolId: number, name: string): Observable<ToolType> {
    return this.http.post<ToolType>(`this.baseURL/${toolId}/types`, {
      name,
    });
  }

  deleteTypeForTool(toolId: number, toolType: ToolType): Observable<void> {
    return this.http.delete<void>(
      `${this.baseURL}/${toolId}/types/${toolType.id}`
    );
  }

  getDockerimagesForTool(toolId: number): Observable<ToolDockerimages> {
    return this.http.get<ToolDockerimages>(
      `${this.baseURL}/${toolId}/dockerimages`
    );
  }

  updateDockerimagesForTool(
    toolId: number,
    dockerimages: ToolDockerimages
  ): Observable<ToolDockerimages> {
    return this.http.put<ToolDockerimages>(
      `${this.baseURL}/${toolId}/dockerimages`,
      dockerimages
    );
  }
}
