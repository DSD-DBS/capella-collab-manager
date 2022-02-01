import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { AuthService } from 'src/app/services/auth/auth.service';

@Component({
  selector: 'app-logout',
  templateUrl: './logout.component.html',
  styleUrls: ['./logout.component.css'],
})
export class LogoutComponent implements OnInit {
  reason = '';
  autoLogin = false;

  constructor(
    private authService: AuthService,
    private route: ActivatedRoute
  ) {}

  ngOnInit(): void {
    this.authService.logOut();
    this.route.queryParams.subscribe((params) => {
      this.reason = params['reason'];
      if (this.reason === 'session-expired') {
        this.autoLogin = true;
      }
    });
  }
}
