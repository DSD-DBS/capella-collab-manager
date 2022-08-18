import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-staged-projects-overview',
  templateUrl: './staged-projects-overview.component.html',
  styleUrls: ['./staged-projects-overview.component.css'],
})
export class StagedProjectsOverviewComponent implements OnInit {
  constructor(private projectService: ProjectService) {}

  ngOnInit(): void {}
}
