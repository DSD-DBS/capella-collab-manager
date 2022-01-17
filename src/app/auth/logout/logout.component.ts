import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { LocalStorageService } from '../local-storage/local-storage.service';

@Component({
  selector: 'app-logout',
  templateUrl: './logout.component.html',
  styleUrls: ['./logout.component.css'],
})
export class LogoutComponent implements OnInit {
  reason = '';
  autoLogin = false;

  constructor(
    private localStorageService: LocalStorageService,
    private route: ActivatedRoute
  ) {}

  ngOnInit(): void {
    this.localStorageService.setValue('access_token', '');
    this.localStorageService.setValue('refresh_token', '');
    this.localStorageService.setValue('GUAC_AUTH', '');
    this.route.queryParams.subscribe((params) => {
      this.reason = params['reason'];
      if (this.reason === 'session-expired') {
        this.autoLogin = true;
      }
    });
  }
}
