/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Injectable, NgZone } from '@angular/core';
import { SwUpdate } from '@angular/service-worker';
import { interval, Subscription } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class ApplicationUpdateService {
  constructor(
    private swUpdate: SwUpdate,
    private zone: NgZone,
  ) {
    this.checkForUpdate();
  }

  isNewVersionAvailable = false;
  intervalSource = interval(15 * 60 * 1000); // every 15 mins
  intervalSubscription: Subscription | undefined;

  checkForUpdate(): void {
    this.intervalSubscription?.unsubscribe();
    if (!this.swUpdate.isEnabled) {
      return;
    }

    this.zone.runOutsideAngular(() => {
      this.intervalSubscription = this.intervalSource.subscribe(async () => {
        try {
          this.isNewVersionAvailable = await this.swUpdate.checkForUpdate();
          console.log(
            this.isNewVersionAvailable
              ? 'A new version is available.'
              : 'Already on the latest version.',
          );
        } catch (error) {
          console.error('Failed to check for updates:', error);
        }
      });
    });
  }

  applyUpdate(): void {
    // Reload the page to update to the latest version after the new version is activated
    this.swUpdate
      .activateUpdate()
      .then(() => document.location.reload())
      .catch((error) => console.error('Failed to apply updates:', error));
  }
}
