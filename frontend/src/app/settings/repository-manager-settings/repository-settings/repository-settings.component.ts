import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { RepositoryProject } from 'src/app/services/repository-project/repository-project.service';

@Component({
  selector: 'app-repository-settings',
  templateUrl: './repository-settings.component.html',
  styleUrls: ['./repository-settings.component.css'],
})
export class RepositorySettingsComponent implements OnInit {
  repository: string = '';
  projects: Array<RepositoryProject> = [];

  constructor(private route: ActivatedRoute) {}

  ngOnInit(): void {
    this.route.params.subscribe((params) => {
      this.repository = params['repository'];
    });
  }

  setProject(projects: Array<RepositoryProject>): void {
    this.projects = projects;
  }
}
