import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { UserService } from './services/user/user.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
})
export class AppComponent implements OnInit {
  title = 'Capella Collaboration Plattform';
  header = true;
  footer = true;
  notice = true;

  constructor(private router: Router) {}

  ngOnInit(): void {}

  updateComponents(): void {
    switch (this.router.url.split('?')[0]) {
      case '/auth':
      case '/logout': {
        this.header = false;
        this.footer = false;
        this.notice = false;
        break;
      }
      default: {
        this.header = true;
        this.footer = true;
        this.notice = true;
      }
    }
  }

  updateTitle(): void {
    switch (this.router.url) {
      case '/settings': {
        this.title = 'Settings';
        break;
      }
      case '/': {
        this.title = 'Workspaces';
        break;
      }
      case '/overview': {
        this.title = 'Session Overview';
        break;
      }
      default: {
        this.title = 'Capella Collaboration Manager';
      }
    }
  }

  changedRoute(): void {
    this.updateTitle();
    this.updateComponents();
  }
}
