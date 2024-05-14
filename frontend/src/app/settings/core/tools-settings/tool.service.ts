/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { HttpClient, HttpContext } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import { SKIP_ERROR_HANDLING } from 'src/app/general/error-handling/error-handling.interceptor';
import {
  Tool,
  ToolNature,
  ToolSessionConnectionOutputMethodsInner,
  ToolVersion,
  ToolsService,
} from 'src/app/openapi';
import { environment } from 'src/environments/environment';

// The generator has a pretty long name, so we're going to shorten it.
export type ConnectionMethod = ToolSessionConnectionOutputMethodsInner;

export type ToolSessionProvisioningConfiguration = {
  max_number_of_models?: number;
};

export type ToolSessionConnectionConfiguration = {
  methods: ConnectionMethod[];
};

export type WorkspaceConfiguration = {
  mounting_enabled: boolean;
};

export type ToolSessionConfiguration = {
  connection: ToolSessionConnectionConfiguration;
  provisioning: ToolSessionProvisioningConfiguration;
  persistent_workspaces: WorkspaceConfiguration;
};

export type CreateTool = {
  name: string;
  integrations: ToolIntegrations;
  config: ToolSessionConfiguration;
};

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
  compatible_versions: number[];
};

export type ToolVersionWithTool = ToolVersion & { tool: Tool };

export type CreateToolNature = {
  name: string;
};

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
export class ToolWrapperService {
  constructor(
    private http: HttpClient,
    private toolsService: ToolsService,
  ) {}

  baseURL = environment.backend_url + '/tools';

  _tools = new BehaviorSubject<Tool[] | undefined>(undefined);
  get tools(): Tool[] | undefined {
    return this._tools.getValue();
  }
  get tools$(): Observable<Tool[] | undefined> {
    return this._tools.asObservable();
  }

  init(): void {
    this.getTools().subscribe();
  }

  getTools(): Observable<Tool[]> {
    return this.toolsService.getTools().pipe(
      tap((tools: Tool[]) => {
        this._tools.next(tools);
      }),
    );
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

  getVersionsForTools(): Observable<ToolVersionWithTool[]> {
    return this.http.get<ToolVersionWithTool[]>(`${this.baseURL}/*/versions`);
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

  getConnectionIdForTool(
    tool: Tool,
    connectionMethodId: string,
  ): ConnectionMethod | undefined {
    return tool?.config?.connection?.methods?.find(
      (cm) => cm.id === connectionMethodId,
    );
  }

  getCachedToolById(toolId: number): Tool | undefined {
    if (this._tools.value === undefined) return undefined;
    return this._tools.value.find((t) => t.id === toolId);
  }
}
