/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Component, inject } from '@angular/core';
import { MatIconButton } from '@angular/material/button';
import { MatIcon } from '@angular/material/icon';
import { ThemeService } from 'src/app/services/theme/theme.service';

@Component({
  selector: 'app-theme-toggle',
  templateUrl: './theme-toggle.component.html',
  imports: [MatIconButton, MatIcon],
})
export class ThemeToggleComponent {
  private themeService = inject(ThemeService);

  toggleTheme(): void {
    this.themeService.toggleTheme();
  }

  isDarkMode(): boolean {
    return this.themeService.getCurrentTheme() === 'dark';
  }
}