import { Component, OnInit } from '@angular/core';
import {
  Repository,
  RepositoryService,
} from '../services/repository/repository.service';
import { SessionService } from '../services/session/session.service';

@Component({
  selector: 'app-workspace',
  templateUrl: './workspace.component.html',
  styleUrls: ['./workspace.component.css'],
})
export class WorkspaceComponent implements OnInit {
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
