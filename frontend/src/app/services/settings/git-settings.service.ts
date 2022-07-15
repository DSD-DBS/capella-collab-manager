// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';
import { environment } from 'src/environments/environment';

@Injectable({
    providedIn: 'root',
})
export class GitSettingsService {
    constructor(private http: HttpClient) { }
    BACKEND_URL_PREFIX = environment.backend_url + '/sources/git-settings/';

    listGitSettings(): Observable<GitSettings[]> {
        return of([
            {id: 1, type: GitType.GitHub, name: "First instance " + Math.random(), url: "https://github.com/machin-bidule"},
            {id: 2, type: GitType.GitHub, name: "Second instance", url: "https://github.com/truc"}
        ])
        return this.http.get<GitSettings[]>(this.BACKEND_URL_PREFIX)
    }

    getGitSettings(id: number): Observable<GitSettings> {
        return of({
            id: 2,
            type: GitType.GitHub,
            name: "Second instance",
            url: "https://github.com/DSD-DBS"
        })
        return this.http.post<GitSettings>(this.BACKEND_URL_PREFIX + id, {})
    }

    createGitSettings(name: string, url: string, type: GitType): Observable<GitSettings> {
        return of({id: Math.floor(Math.random()* 1000), name, url, type} as GitSettings)
        return this.http.post<GitSettings>(this.BACKEND_URL_PREFIX, {
            type,
            name,
            url,
        });
    }

    editGitSettings(id: number, name: string, url: string, type: GitType): Observable<GitSettings> {
        return of({id, name, url, type})
        return this.http.put<GitSettings>(this.BACKEND_URL_PREFIX + id, {
            type,
            name,
            url,
        })
    }

    deleteGitSettings(id: number) {
        return of({});
        return this.http.delete(this.BACKEND_URL_PREFIX + id)
    }

    getRevisions(url: string, username: string, password: string): Observable<GitReferences>{
        return of({branches: ['main', 'develop', 'staging'], tags: ['v0.1', 'v1.0', 'v2.0', 'v2.1']})
        return this.http.get<GitReferences>(
            this.BACKEND_URL_PREFIX + 'list-repository', {params: {
                url, username, password
            }}
        )
    }
}

export interface GitSettings {
    id: number;
    name: string;
    url: string;
    type: GitType;
}

export enum GitType {
    General,
    GitLab,
    GitHub,
    AzureDevOps,
}

export interface GitReferences {
    branches: string[];
    tags: string[];
}

export type EditingMode = 't4c' | 'git';
export type ProjectType = 'project' | 'library';
