import { Component, Input, OnInit } from '@angular/core';

@Component({
  selector: 'app-backup-settings',
  templateUrl: './backup-settings.component.html',
  styleUrls: ['./backup-settings.component.css'],
})
export class BackupSettingsComponent implements OnInit {
  constructor() {}

  ngOnInit(): void {}

  @Input()
  project: string = '';
}
