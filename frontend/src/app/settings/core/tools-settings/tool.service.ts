/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { HttpContext } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import { SKIP_ERROR_HANDLING } from 'src/app/general/error-handling/error-handling.interceptor';
import {
  Tool,
  ToolSessionConnectionOutputMethodsInner,
  ToolVersion,
  ToolsService,
} from 'src/app/openapi';

// The generator has a pretty long name, so we're going to shorten it.
export type ConnectionMethod = ToolSessionConnectionOutputMethodsInner;

@Injectable({
  providedIn: 'root',
})
export class ToolWrapperService {
  private toolsService = inject(ToolsService);

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

  getVersionForTool(
    toolId: number,
    versionId: number,
    skipErrorHandling: boolean,
  ): Observable<ToolVersion> {
    return this.toolsService.getToolVersion(
      toolId,
      versionId,
      undefined,
      undefined,
      {
        context: new HttpContext().set(SKIP_ERROR_HANDLING, skipErrorHandling),
      },
    );
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
