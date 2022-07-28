import { Component, OnInit } from '@angular/core';
import { AbstractControl, AsyncValidatorFn, FormControl, FormGroup,
  ValidationErrors, Validators } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { merge, Observable } from 'rxjs';
import { GitModel, ModelService } from 'src/app/services/model/model.service';
import { GitModelService, Instance } from 'src/app/services/modelsources/git-model/git-model.service';
import { ProjectService } from '../../service/project.service';

@Component({
  selector: 'app-create-coworking-method',
  templateUrl: './create-coworking-method.component.html',
  styleUrls: ['./create-coworking-method.component.css']
})
export class CreateCoworkingMethodComponent implements OnInit {
  
  validateCredentials: AsyncValidatorFn = (control: AbstractControl):
  Observable<ValidationErrors | null> => {
    let credentials = {
      url: control.get('url')?.value,
      username: control.get('username')?.value,
      password: control.get('password')?.value,
    }
    return new Observable<ValidationErrors | null>(subscriber => {
      console.log(credentials.url)
      this.gitModelService.fetch(credentials.url).subscribe({
        next: (value) => {
          console.log(value);
          subscriber.next(null);
          subscriber.complete();
        },
        error: (e) => {
          console.log(e);
          subscriber.next({credentials: {value: e.name}});
          subscriber.complete();
        },
      })
    })
  }

  public gitForm = new FormGroup({
    info: new FormGroup({
      name: new FormControl('', Validators.required),
      description: new FormControl(''),
    }),
    credentials: new FormGroup({
      url: new FormControl('', Validators.required),
      username: new FormControl(''),
      password: new FormControl(''),
    }, [], this.validateCredentials),
    revision: new FormControl('', Validators.required),
    path: new FormControl('', Validators.required),
    entrypoint: new FormControl('', Validators.required),
  }, );

  public filteredRevisions: Instance = {branches: [], tags: []}

  constructor(
    private route: ActivatedRoute,
    public projectService: ProjectService,
    public modelService: ModelService,
    private gitModelService: GitModelService,
  ) { }

  ngOnInit(): void {
    this.route.params.subscribe(params => {
      this.projectService.init(params.project).subscribe(project => {
        this.modelService.init_all(project.slug)
      })
    });

    // initialization : disable fields
    ['revision', 'path', 'entrypoint']
    .forEach(field => this.gitForm.controls[field].disable());

    this.createDependency(this.gitForm, ['credentials'], ['revision'])
    
    //this.chainDependencies(this.gitForm, ['credentials'], ['revision'],
    //  ['path', 'entrypoint'])

    this.gitForm.controls.credentials.valueChanges.subscribe(value => {
      ['url', 'username', 'password'].forEach(field => {
        console.log(field+ ' ' + this.gitForm.controls.credentials.get(field)?.valid)
      })
      console.log(this.gitForm.controls['credentials'].valid)
    })
    
    this.gitForm.controls.revision.valueChanges.subscribe(value => {
      console.log(this.gitModelService.instance)
      if (!this.gitModelService.instance) {
        this.filteredRevisions = {branches: [], tags: []}
      } else {
        this.filteredRevisions = {
          branches:
            this.gitModelService.instance.branches
            .filter(branch => branch.startsWith(value)),
          tags:
            this.gitModelService.instance.tags
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
      this.modelService.createWithSource(
        this.projectService.project.slug,
        this.gitForm.value as GitModel,
      )
    }
  }

}
