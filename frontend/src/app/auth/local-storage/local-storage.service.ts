import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class LocalStorageService {
  constructor() {}

  getValue(key: string): string {
    return localStorage.getItem(key) || '';
  }

  setValue(key: string, value: any) {
    localStorage.setItem(key, value);
  }
}
