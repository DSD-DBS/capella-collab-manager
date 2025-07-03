/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

export type Theme = 'light' | 'dark';

@Injectable({
  providedIn: 'root',
})
export class ThemeService {
  private readonly THEME_STORAGE_KEY = 'CCM_THEME';
  private readonly THEME_CLASS_LIGHT = 'light-theme';
  private readonly THEME_CLASS_DARK = 'dark-theme';

  private themeSubject = new BehaviorSubject<Theme>(this.getInitialTheme());
  public theme$ = this.themeSubject.asObservable();

  constructor() {
    this.applyTheme(this.themeSubject.value);
  }

  private getInitialTheme(): Theme {
    // Check localStorage first
    const storedTheme = localStorage.getItem(this.THEME_STORAGE_KEY) as Theme;
    if (storedTheme === 'light' || storedTheme === 'dark') {
      return storedTheme;
    }

    // Fall back to system preference
    if (
      window.matchMedia &&
      window.matchMedia('(prefers-color-scheme: dark)').matches
    ) {
      return 'dark';
    }

    return 'light';
  }

  public getCurrentTheme(): Theme {
    return this.themeSubject.value;
  }

  public toggleTheme(): void {
    const newTheme: Theme =
      this.themeSubject.value === 'light' ? 'dark' : 'light';
    this.setTheme(newTheme);
  }

  public setTheme(theme: Theme): void {
    this.themeSubject.next(theme);
    this.applyTheme(theme);
    localStorage.setItem(this.THEME_STORAGE_KEY, theme);
  }

  private applyTheme(theme: Theme): void {
    const body = document.body;
    
    // Remove existing theme classes
    body.classList.remove(this.THEME_CLASS_LIGHT, this.THEME_CLASS_DARK);
    
    // Add the new theme class
    if (theme === 'dark') {
      body.classList.add(this.THEME_CLASS_DARK);
    } else {
      body.classList.add(this.THEME_CLASS_LIGHT);
    }
  }
}