/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { HttpClient, HttpContext } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import { SKIP_ERROR_HANDLING } from 'src/app/general/error-handling/error-handling.interceptor';
import { environment } from 'src/environments/environment';

export type ConnectionMethod = {
  id: string;
  name: string;
  description?: string;
  type: 'http' | 'guacamole';
};

export type ToolSessionProvisioningConfiguration = {
  max_number_of_models?: number;
};

export type ToolSessionConnectionConfiguration = {
  methods: ConnectionMethod[];
};

export type ToolSessionConfiguration = {
  connection: ToolSessionConnectionConfiguration;
  provisioning: ToolSessionProvisioningConfiguration;
};

export type CreateTool = {
  name: string;
  integrations: ToolIntegrations;
  config: ToolSessionConfiguration;
};

export type Tool = {
  id: number;
} & CreateTool;

export type ToolIntegrations = {
  t4c: boolean | null;
  pure_variants: boolean | null;
  jupyter: boolean | null;
};

export type CreateToolVersion = {
  name: string;
  config: ToolVersionConfig;
};

export type ToolVersionConfig = {
  is_recommended: boolean;
  is_deprecated: boolean;
};

export type ToolVersion = {
  id: number;
} & CreateToolVersion;

export type ToolVersionWithTool = ToolVersion & { tool: Tool };

export type CreateToolNature = {
  name: string;
};

export type ToolNature = {
  id: number;
} & CreateToolNature;

export type ToolExtended = {
  natures: ToolNature[];
  versions: ToolVersion[];
};

export type ToolDockerimages = {
  persistent: string;
  readonly: string | undefined;
  backup: string | undefined;
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
      }),
    );
  }

  getToolByID(id: string): Observable<Tool> {
    return this.http.get<Tool>(`${this.baseURL}/${id}`);
  }

  getDefaultTool(): Observable<CreateTool> {
    return this.http.get<CreateTool>(`${this.baseURL}/default`);
  }

  createTool(tool: CreateTool): Observable<Tool> {
    return this.http.post<Tool>(this.baseURL, tool);
  }

  updateTool(toolId: number, value: Tool): Observable<Tool> {
    return this.http.put<Tool>(`${this.baseURL}/${toolId}`, value);
  }

  deleteTool(tool_id: number): Observable<void> {
    return this.http.delete<void>(`${this.baseURL}/${tool_id}`);
  }

  getVersionsForTool(
    toolId: number,
    skipErrorHandling: boolean,
  ): Observable<ToolVersion[]> {
    return this.http.get<ToolVersion[]>(`${this.baseURL}/${toolId}/versions`, {
      context: new HttpContext().set(SKIP_ERROR_HANDLING, skipErrorHandling),
    });
  }

  getVersionForTool(
    toolId: number,
    versionId: number,
    skipErrorHandling: boolean,
  ): Observable<ToolVersion> {
    return this.http.get<ToolVersion>(
      `${this.baseURL}/${toolId}/versions/${versionId}`,
      {
        context: new HttpContext().set(SKIP_ERROR_HANDLING, skipErrorHandling),
      },
    );
  }

  getDefaultVersion(): Observable<ToolVersion> {
    return this.http.get<ToolVersion>(`${this.baseURL}/-/versions/default`);
  }

  createVersionForTool(
    toolId: number,
    toolVersion: CreateToolVersion,
  ): Observable<ToolVersion> {
    return this.http.post<ToolVersion>(
      `${this.baseURL}/${toolId}/versions`,
      toolVersion,
    );
  }

  updateToolVersion(
    toolId: number,
    versionId: number,
    updatedToolVersion: CreateToolVersion,
  ) {
    return this.http.put<ToolVersion>(
      `${this.baseURL}/${toolId}/versions/${versionId}`,
      updatedToolVersion,
    );
  }

  deleteVersionForTool(
    toolId: number,
    toolVersion: ToolVersion,
  ): Observable<void> {
    return this.http.delete<void>(
      `${this.baseURL}/${toolId}/versions/${toolVersion.id}`,
    );
  }

  getNaturesForTool(toolId: number): Observable<ToolNature[]> {
    return this.http.get<ToolVersion[]>(`${this.baseURL}/${toolId}/natures`);
  }

  getDefaultNature(): Observable<ToolVersion> {
    return this.http.get<ToolVersion>(`${this.baseURL}/-/natures/default`);
  }

  createNatureForTool(
    toolId: number,
    toolNature: CreateToolNature,
  ): Observable<ToolNature> {
    return this.http.post<ToolNature>(
      `${this.baseURL}/${toolId}/natures`,
      toolNature,
    );
  }

  updateToolNature(
    toolId: number,
    natureID: number,
    updatedToolNature: CreateToolNature,
  ) {
    return this.http.put<ToolVersion>(
      `${this.baseURL}/${toolId}/natures/${natureID}`,
      updatedToolNature,
    );
  }

  deleteNatureForTool(
    toolId: number,
    toolNature: ToolNature,
  ): Observable<void> {
    return this.http.delete<void>(
      `${this.baseURL}/${toolId}/natures/${toolNature.id}`,
    );
  }

  patchToolIntegrations(
    toolId: number,
    toolIntegrations: ToolIntegrations,
  ): Observable<ToolIntegrations> {
    return this.http.put<ToolIntegrations>(
      `${this.baseURL}/${toolId}/integrations`,
      toolIntegrations,
    );
  }

  getConnectionIdForTool(
    tool: Tool,
    connectionMethodId: string,
  ): ConnectionMethod | undefined {
    return tool?.config.connection.methods.find(
      (cm) => cm.id === connectionMethodId,
    );
  }

  getCachedToolById(toolId: number): Tool | undefined {
    if (this._tools.value === undefined) return undefined;
    return this._tools.value.find((t) => t.id === toolId);
  }
}
