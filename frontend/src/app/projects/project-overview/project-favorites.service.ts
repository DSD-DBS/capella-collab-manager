/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { z } from 'zod';

const projectFavoriteSchema = z.object({
  projectId: z.number().int(),
  addedAt: z.coerce.date(),
});

const projectFavoritesArraySchema = z.array(projectFavoriteSchema);
export type ProjectFavorite = z.infer<typeof projectFavoriteSchema>;

@Injectable({
  providedIn: 'root',
})
export class ProjectFavoritesService {
  private LOCAL_STORAGE_FAVORITES_KEY = 'projectFavorites';
  favorites = new BehaviorSubject<ProjectFavorite[] | undefined>(undefined);

  getFavorites(): ProjectFavorite[] {
    const currentFavorites = localStorage.getItem(
      this.LOCAL_STORAGE_FAVORITES_KEY,
    );
    if (!currentFavorites) {
      return [];
    }

    try {
      const result = projectFavoritesArraySchema.safeParse(
        JSON.parse(currentFavorites),
      );
      return result.success ? result.data : [];
    } catch (e) {
      console.error(e);
      return [];
    }
  }

  loadFavorites() {
    this.favorites.next(this.getFavorites());
  }

  toggleFavorite(projectId: number) {
    const currentFavorites = this.getFavorites();
    const existingIndex = currentFavorites.findIndex(
      (f) => f.projectId === projectId,
    );

    if (existingIndex >= 0) {
      currentFavorites.splice(existingIndex, 1);
    } else {
      currentFavorites.push({ projectId, addedAt: new Date() });
    }

    this.favorites.next(currentFavorites);
    localStorage.setItem(
      this.LOCAL_STORAGE_FAVORITES_KEY,
      JSON.stringify(currentFavorites),
    );
  }

  isFavorite(projectId: number): boolean {
    return this.getFavorites().some((f) => f.projectId === projectId);
  }
}
