import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from "src/environments/environment";

export interface Tool {
  id: number;
  name: string;
}

export interface Version {
  id: number;
  name: string;
  tool_id: number;
  is_recommended: boolean;
  is_deprecated: boolean;
}

type NestedVersion = {[id: number]: Version[]}

export interface Type {
  id: number;
  name: string;
  tool_id: number;
}

type NestedType = {[id: number]: Type[]}

@Injectable({
  providedIn: 'root'
})
export class ToolService {

  constructor(
    private http: HttpClient,
  ) { }
  
  base_url = new URL('tools/', environment.backend_url + '/')

  tools: Tool[] | null = null;
  versions: NestedVersion | null = null;
  types: NestedType | null = null;

  init() {
    if (!this.tools) {
      this.get_tools().subscribe();
    }
    if (!this.versions) {
      this.get_versions().subscribe();
    }
    if (!this.types) {
      this.get_types().subscribe();
    }
  }

  get_tools(): Observable<Tool[]> {
    let url = this.base_url;
    return new Observable<Tool[]>(subscriber => {
      this.http.get<Tool[]>(url.toString()).subscribe(tools => {
        this.tools = tools;
        subscriber.next(tools);
        subscriber.complete();
      })
    })
  }

  get_versions(): Observable<NestedVersion> {
    let url = new URL('versions/', this.base_url);
    return new Observable<NestedVersion>(subscriber => {
      this.http.get<Version[]>(url.toString()).subscribe(versions => {
        this.versions = {}
        versions.forEach(version => {
          if (this.versions) {
            if (version.tool_id in this.versions) {
              this.versions[version.tool_id].push(version)
            } else {
              this.versions[version.tool_id] = [version]
            }
          }
        })
        subscriber.next(this.versions);
        subscriber.complete();
      })
    })
  }
  
  get_types(): Observable<NestedType> {
    let url = new URL('types/', this.base_url);
    return new Observable<NestedType>(subscriber => {
      this.http.get<Version[]>(url.toString()).subscribe(types => {
        this.types = {}
        types.forEach(tool_type => {
          if (this.types) {
            if (tool_type.tool_id in this.types) {
              this.types[tool_type.tool_id].push(tool_type)
            } else {
              this.types[tool_type.tool_id] = [tool_type]
            }
          }
        })
        subscriber.next(this.types);
        subscriber.complete();
      })
    })
  }

}

