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

  constructor(private router: Router) {}

  ngOnInit(): void {}

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
    console.log(this.title);
  }
}
