import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

@Component({
  selector: 'app-repository-settings',
  templateUrl: './repository-settings.component.html',
  styleUrls: ['./repository-settings.component.css'],
})
export class RepositorySettingsComponent implements OnInit {
  repository: string = '';

  constructor(private route: ActivatedRoute) {}

  ngOnInit(): void {
    this.route.params.subscribe((params) => {
      this.repository = params['repository'];
    });
  }
}
