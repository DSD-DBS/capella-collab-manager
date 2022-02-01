import { Component, OnInit } from '@angular/core';
import {
  Repository,
  RepositoryService,
} from '../services/repository/repository.service';
import { SessionService } from '../services/session/session.service';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css'],
})
export class HomeComponent implements OnInit {
  repositories: Array<Repository> = [];
  showSpinner = true;

  constructor(
    public sessionService: SessionService,
    private repositoryService: RepositoryService
  ) {}

  ngOnInit() {
    this.showSpinner = true;
    this.repositoryService.getRepositories().subscribe(
      (res: Array<Repository>) => {
        this.repositories = res;
        this.showSpinner = false;
      },
      (err) => {
        this.showSpinner = false;
      }
    );
  }
}
