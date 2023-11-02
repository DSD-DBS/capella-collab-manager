/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { HttpClient, HttpContext } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, tap, catchError, of } from 'rxjs';
import { SKIP_ERROR_HANDLING } from 'src/app/general/error-handling/error-handling.interceptor';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root',
})
export class PluginStoreService {
  BACKEND_URL_PREFIX = environment.backend_url + '/plugins';

  constructor(private httpClient: HttpClient) {
    this.fetchPluginsFromStore();
  }

  _plugins = new BehaviorSubject<Plugin[] | undefined>(undefined);
  readonly plugins = this._plugins.asObservable();

  _plugin = new BehaviorSubject<Plugin | undefined>(undefined);
  readonly plugin = this._plugin.asObservable();

  updatePlugin(pluginId: number, plugin: CreatePlugin): Observable<Plugin> {
    return this.httpClient
      .patch<Plugin>(`${this.BACKEND_URL_PREFIX}/${pluginId}`, plugin)
      .pipe(
        tap({
          next: (plugin) => {
            this.fetchPluginsFromStore();
            this._plugin.next(plugin);
          },
          error: () => this._plugin.next(undefined),
        }),
      );
  }

  deletePlugin(pluginId: number): Observable<void> {
    return this.httpClient
      .delete<void>(`${this.BACKEND_URL_PREFIX}/${pluginId}`)
      .pipe(
        tap(() => {
          this.fetchPluginsFromStore();
          this._plugin.next(undefined);
        }),
      );
  }

  fetchPluginsFromStore() {
    this._plugins.next(undefined);
    this.httpClient
      .get<Plugin[]>(`${environment.backend_url}/plugins`)
      .subscribe({ next: (plugins) => this._plugins.next(plugins) });
  }

  fetchPluginFromStoreById(id: number) {
    this.httpClient.get<Plugin>(`${this.BACKEND_URL_PREFIX}/${id}`).subscribe({
      next: (plugin) => this._plugin.next(plugin),
      error: () => this._plugin.next(undefined),
    });
  }

  fetchPluginContentFromRemote(plugin: Plugin): Observable<Plugin> {
    return this.httpClient
      .post<Plugin>(`${this.BACKEND_URL_PREFIX}/peek-plugin-content`, plugin, {
        context: new HttpContext().set(SKIP_ERROR_HANDLING, true),
      })
      .pipe(
        tap((fplugin) => {
          return fplugin;
        }),
        catchError((error) => {
          console.error('Error fetching plugin content:', error);
          return of({} as Plugin);
        }),
      );
  }

  registerPluginInStore(plugin: Plugin): Observable<Plugin> {
    this._plugin.next(undefined);
    return this.httpClient
      .post<Plugin>(`${environment.backend_url}/plugins`, plugin)
      .pipe(tap({ next: (plugin) => this._plugin.next(plugin) }));
  }

  clearPlugin(): void {
    this._plugin.next(undefined);
  }
}

export type PluginMetadata = {
  id: string;
  description: string;
  displayName: string;
  documentationURL: string;
};

export type CreatePlugin = {
  remote: string;
  username: string;
  password: string;
};

export type Plugin = CreatePlugin & {
  id: number;
  content?: PluginTemplateContent;
};

export type PluginTemplateContent = {
  trigger: PluginTrigger;
  metadata?: PluginMetadata;
  input?: PluginTemplateInput[];
};

export type PluginTrigger = {
  cron?: string;
  manual?: boolean;
};

export type PluginTemplateInput = {
  type: 'git' | 't4c' | 'environment';
};

export type PluginTemplateEnvironmentMapping = {
  type: 'environment';
  key: string;
};

export type PluginTemplateGitMapping = {
  url: PluginTemplateEnvironmentMapping;
  username: PluginTemplateEnvironmentMapping;
  password: PluginTemplateEnvironmentMapping;
  revision: PluginTemplateEnvironmentMapping;
};
