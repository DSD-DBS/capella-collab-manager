import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { RepositoryService } from 'src/app/services/repository/repository.service';

@Component({
  selector: 'app-create-repository',
  templateUrl: './create-repository.component.html',
  styleUrls: ['./create-repository.component.css'],
})
export class CreateRepositoryComponent implements OnInit {
  createRepositoryForm = new FormGroup({
    title: new FormControl('', Validators.required),
  });

  constructor(private repositoryService: RepositoryService) {}

  ngOnInit(): void {}

  createRepository(): void {
    if (this.createRepositoryForm.valid) {
      this.repositoryService
        .createRepository(this.createRepository.name)
        .subscribe(() => {
          this.repositoryService.refreshRepositories();
        });
    }
  }
}
