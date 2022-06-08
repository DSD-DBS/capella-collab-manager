import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root'
})
export class LoadFilesService {

  BACKEND_URL_PREFIX = environment.backend_url + '/sessions/';

  constructor(private http: HttpClient) { }

  upload(id: string, files: FormData): Observable<any> {
    return this.http.post<any>(
      this.BACKEND_URL_PREFIX + id,
      files,
      {
        reportProgress: true,
        observe: 'events'
      }
    );
  }

  getCurrentFiles(id: string): Observable<string> {
    return this.http.get<string>(this.BACKEND_URL_PREFIX + id);
  }

  download(file: string) {

  }

}
