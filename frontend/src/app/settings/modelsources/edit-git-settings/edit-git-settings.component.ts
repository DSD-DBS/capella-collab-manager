import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { NavBarService } from 'src/app/navbar/service/nav-bar.service';
import { GitSettings, GitSettingsService, GitType } from 'src/app/services/settings/git-settings.service';

@Component({
  selector: 'app-edit-git-settings',
  templateUrl: './edit-git-settings.component.html',
  styleUrls: ['./edit-git-settings.component.css']
})
export class EditGitSettingsComponent implements OnInit {

  instance: GitSettings = {} as GitSettings;
  gitSettingsForm = new FormGroup({
    type: new FormControl('', Validators.required),
    name: new FormControl('', Validators.required),
    url: new FormControl('', Validators.required),
  })

  constructor(
    private gitSettingsService: GitSettingsService,
    private navbarService: NavBarService,
    private route: ActivatedRoute,
    private router: Router,
  ) { }

  ngOnInit(): void {
    this.route.params.subscribe((params) => {
      this.gitSettingsService.getGitSettings(params['id']).subscribe(instance => {
        this.instance = instance;
        this.gitSettingsForm.patchValue(this.instance);
      });
      this.navbarService.title =
        'Settings / Modelsources / T4C / Instances / ' + params['id'];
    });
  }

  editGitSettings(): void {
    if (this.gitSettingsForm.valid) {
      this.gitSettingsService.editGitSettings(
        this.instance['id'],
        (this.gitSettingsForm.get('name') as FormControl).value,
        (this.gitSettingsForm.get('url') as FormControl).value,
        (this.gitSettingsForm.get('type') as FormControl).value,
      ).subscribe(_ => {
        this.router.navigate(['settings/modelsources/git']);
      })
    }
  }

}
