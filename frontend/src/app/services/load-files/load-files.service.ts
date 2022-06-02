import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from 'src/environments/environment';
import { MatProgressBarModule } from '@angular/material/progress-bar';


@Injectable({
  providedIn: 'root'
})
export class LoadFilesService {

  BACKEND_URL_PREFIX = environment.backend_url + '/sessions/';

  constructor(private http: HttpClient) {}

  upload(id: string, file: FormData): Observable<any> {
    return this.http.post<any>(
      this.BACKEND_URL_PREFIX + id,
      file,
      {
        reportProgress: true,
        observe: 'events'
      }
    );
  }


  getCurrentFiles(){

  }

  download(file: string){

  }

}
