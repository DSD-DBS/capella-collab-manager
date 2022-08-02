import { Component, OnInit } from '@angular/core';
import { AbstractControl, AsyncValidatorFn, FormControl, FormGroup,
  ValidationErrors, Validators } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { merge, Observable } from 'rxjs';
import { GitModel, ModelService } from 'src/app/services/model/model.service';
import { ProjectService } from 'src/app/projects/service/project.service';
import { Credentials, GitService, Instance } from 'src/app/services/git/git.service';

@Component({
  selector: 'app-create-coworking-method',
  templateUrl: './create-coworking-method.component.html',
  styleUrls: ['./create-coworking-method.component.css']
})
export class CreateCoworkingMethodComponent implements OnInit {
  
  validateCredentials = (control: AbstractControl): Observable<ValidationErrors | null> => {
    let credentials = control.value as Credentials

    return new Observable<ValidationErrors | null>(subscriber => {
      setTimeout(() => {
        if (control.value as Credentials === credentials) {
          this.gitService.fetch('', credentials).subscribe({
            next: instance => {
              this.filteredRevisions = instance;
              subscriber.next(null);
              subscriber.complete();
            },
            error: (e) => {
              this.filteredRevisions = {branches:[], tags:[]}
              subscriber.next({credentials: {value: e.name}});
              subscriber.complete();
            }
          })
        }
      }, 500)
    })
  }

  public gitForm = new FormGroup({
    credentials: new FormGroup({
      url: new FormControl('', Validators.required),
      username: new FormControl(''),
      password: new FormControl(''),
    }, [], this.validateCredentials),
    revision: new FormControl('', Validators.required),
    entrypoint: new FormControl('/'),
  }, );

  public filteredRevisions: Instance = {branches: [], tags: []}

  constructor(
    private route: ActivatedRoute,
    public projectService: ProjectService,
    public modelService: ModelService,
    private gitService: GitService,
  ) { }

  ngOnInit(): void {
    this.route.params.subscribe(params => {
      this.modelService.init(params.project, params.model).subscribe()
    });
    
    this.gitForm.controls.revision.valueChanges.subscribe(value => {
      if (!this.gitService.instance) {
        this.filteredRevisions = {branches: [], tags: []}
      } else {
        this.filteredRevisions = {
          branches:
            this.gitService.instance.branches
            .filter(branch => branch.startsWith(value)),
          tags:
            this.gitService.instance.tags
            .filter(tag => tag.startsWith(value)),
        }
      }
    })
  }

  createDependency(form: FormGroup, sources: string[], targets: string[], ): void {
    merge(
      ...sources
      .map(field => form.controls[field].valueChanges)
    )
    .subscribe(_ => {
      if (
        sources
        .map(field => form.get(field)?.valid)
        .every(Boolean)
      ) {
        targets.forEach(field => form.controls[field].enable())
      } else {
        targets.forEach(field => form.controls[field].disable())
      } 
    })
  }

  chainDependencies(form: FormGroup, ...chain: string[][]) {
    for (let i = 0; i < chain.length - 1; i++) {
      this.createDependency(form, chain[i], chain[i + 1])
    }
  }

  onSubmit(): void {
    if (this.projectService.project && this.gitForm.valid) {
      this.modelService.addGitSource(
        this.projectService.project.slug,
        this.gitForm.value as GitModel,
      )
    }
  }

}
