import { Component, OnInit } from '@angular/core';
import { RepositoryUser } from 'src/app/schemes';
import { RepositoryService } from 'src/app/services/repository/repository.service';

@Component({
  selector: 'app-repository-manager-settings',
  templateUrl: './repository-manager-settings.component.html',
  styleUrls: ['./repository-manager-settings.component.css'],
})
export class RepositoryManagerSettingsComponent implements OnInit {
  constructor(public repositoryService: RepositoryService) {}

  ngOnInit(): void {
    this.repositoryService.refreshRepositories();
  }
}
