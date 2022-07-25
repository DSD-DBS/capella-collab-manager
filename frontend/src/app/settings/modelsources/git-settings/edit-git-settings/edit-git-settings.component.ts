import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import {
  GitSettings,
  GitSettingsService,
  GitType,
} from 'src/app/services/settings/git-settings.service';

@Component({
  selector: 'app-edit-git-settings',
  templateUrl: './edit-git-settings.component.html',
  styleUrls: ['./edit-git-settings.component.css'],
})
export class EditGitSettingsComponent implements OnInit {
  instance: GitSettings;

  gitSettingsForm = new FormGroup({
    type: new FormControl('', Validators.required),
    name: new FormControl('', Validators.required),
    url: new FormControl('', Validators.required),
  });
  constructor(
    private router: Router,
    private route: ActivatedRoute,
    private gitSettingsService: GitSettingsService
  ) {
    this.instance = { id: 0, name: '', url: '', type: GitType.General };
  }

  ngOnInit(): void {
    /*this.route.params.subscribe((params) => {
      const id = params['instance_id'];
      if (!!id) {
        this.gitSettingsService
          .getGitSettings(id)
          .subscribe((instance: GitSettings) => {
            this.instance = instance;
          });
      }
    });*/
  }

  editGitSettings() {
    this.gitSettingsService.editGitSettings(
      this.instance?.id,
      (this.gitSettingsForm.get('name') as FormControl).value,
      (this.gitSettingsForm.get('url') as FormControl).value,
      (this.gitSettingsForm.get('type') as FormControl).value
    );
  }

  goBack(): void {
    this.router.navigateByUrl('/settings/modelsources/git');
  }
}
