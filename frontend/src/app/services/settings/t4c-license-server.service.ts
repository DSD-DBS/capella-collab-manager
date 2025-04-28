/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Injectable, inject } from '@angular/core';
import {
  AbstractControl,
  AsyncValidatorFn,
  ValidationErrors,
} from '@angular/forms';
import { BehaviorSubject, map, Observable, take, tap } from 'rxjs';
import {
  SettingsModelsourcesT4CLicenseServersService,
  T4CLicenseServer,
} from '../../openapi';

@Injectable({
  providedIn: 'root',
})
export class T4CLicenseServerWrapperService {
  private licenseServerService = inject(
    SettingsModelsourcesT4CLicenseServersService,
  );

  private _licenseServers = new BehaviorSubject<T4CLicenseServer[] | undefined>(
    undefined,
  );
  public readonly licenseServers$ = this._licenseServers.asObservable();

  private _licenseServer = new BehaviorSubject<T4CLicenseServer | undefined>(
    undefined,
  );
  public readonly licenseServer$ = this._licenseServer.asObservable();

  loadLicenseServers(): void {
    this._licenseServers.next(undefined);
    this.licenseServerService.getT4cLicenseServers().subscribe({
      next: (servers) => this._licenseServers.next(servers),
      error: () => this._licenseServers.next(undefined),
    });
  }

  loadLicenseServer(serverId: number): void {
    this.licenseServerService.getT4cLicenseServer(serverId).subscribe({
      next: (server) => this._licenseServer.next(server),
      error: () => this._licenseServer.next(undefined),
    });
  }

  createLicenseServer(server: T4CLicenseServer): Observable<T4CLicenseServer> {
    return this.licenseServerService.createT4cLicenseServer(server).pipe(
      tap((server) => {
        this._licenseServer.next(server);
        this.loadLicenseServers();
      }),
    );
  }

  updateLicenseServer(
    serverId: number,
    server: T4CLicenseServer,
  ): Observable<T4CLicenseServer> {
    return this.licenseServerService
      .editT4cLicenseServer(serverId, server)
      .pipe(
        tap((server) => {
          this._licenseServer.next(server);
          this.loadLicenseServers();
        }),
      );
  }

  resetLicenseServer(): void {
    this._licenseServer.next(undefined);
  }

  reset(): void {
    this.resetLicenseServer();
    this._licenseServers.next(undefined);
  }

  asyncNameValidator(ignoreInstance?: T4CLicenseServer): AsyncValidatorFn {
    const ignoreLicenseServerId = ignoreInstance ? ignoreInstance.id : -1;
    return (control: AbstractControl): Observable<ValidationErrors | null> => {
      const licenseServerName = control.value;
      return this.licenseServers$.pipe(
        take(1),
        map((licenseServers) => {
          return licenseServers?.find(
            (licenseServer) =>
              licenseServer.name === licenseServerName &&
              licenseServer.id !== ignoreLicenseServerId,
          )
            ? { uniqueName: { value: licenseServerName } }
            : null;
        }),
      );
    };
  }
}
