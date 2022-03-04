import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { GitModelService } from 'src/app/services/modelsources/git-model/git-model.service';
import { T4CRepoService } from 'src/app/services/modelsources/t4c-repos/t4c-repo.service';

@Component({
  selector: 'app-create-ease-backup',
  templateUrl: './create-ease-backup.component.html',
  styleUrls: ['./create-ease-backup.component.css'],
})
export class CreateEASEBackupComponent implements OnInit {
  constructor(
    public gitModelService: GitModelService,
    public t4cRepoService: T4CRepoService
  ) {}

  ngOnInit(): void {}

  createGitBackupForm = new FormGroup({
    gitmodel: new FormControl('', Validators.required),
    t4cmodel: new FormControl('', Validators.required),
  });

  createGitBackup() {}
}
