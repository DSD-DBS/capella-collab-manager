import { Component, OnInit } from '@angular/core';
import { AbstractControl, AsyncValidatorFn, FormControl, FormGroup, ValidationErrors, Validators } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { merge, Observable } from 'rxjs';
import { GitService } from 'src/app/services/git/git.service';
import { GitModel, ModelService } from 'src/app/services/model/model.service';
import { ProjectService } from '../../service/project.service';

@Component({
  selector: 'app-create-coworking-method',
  templateUrl: './create-coworking-method.component.html',
  styleUrls: ['./create-coworking-method.component.css']
})
export class CreateCoworkingMethodComponent implements OnInit {

  public gitForm = new FormGroup({
    info: new FormGroup({
      name: new FormControl('', Validators.required),
      description: new FormControl(''),
    }),
    credentials: new FormGroup({
      url: new FormControl('', Validators.required),
      username: new FormControl(''),
      password: new FormControl(''),
    }),
    revision: new FormControl('', Validators.required),
    path: new FormControl('', Validators.required),
    entrypoint: new FormControl('', Validators.required),
  }, );

  constructor(
    private route: ActivatedRoute,
    public projectService: ProjectService,
    public modelService: ModelService,
    private gitService: GitService,
  ) { }

  ngOnInit(): void {
    this.route.params.subscribe(params => {
      this.projectService.init(params.project).subscribe(project => {
        this.modelService.init_all(project.slug)
      })
    });

    this.gitForm.controls.credentials.addAsyncValidators(this.validateCredentials);

    // initialization : disable fields
    ['revision', 'path', 'entrypoint']
    .forEach(field => this.gitForm.controls[field].disable());
    this.chainDependencies(this.gitForm, ['credentials'], ['revision'], ['path', 'entrypoint'])
  }


  createDependency(form: FormGroup, sources: string[], targets: string[], ): void {
    merge(
      ...sources
      .map(field => form.controls[field].valueChanges)
    )
    .subscribe(_ => {
      if (
        sources
        .map(field => form.controls[field].valid)
        .every(Boolean)
      ) {
        targets.forEach(field => form.controls[field].enable())
      } else {
        targets.forEach(field => form.controls[field].disable())
      }
    })
  }

  chainDependencies(form: FormGroup, ...chain: string[][]) {
    for (let i = 0; i < chain.length; i++) {
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

  validateCredentials: AsyncValidatorFn = (control: AbstractControl): Observable<ValidationErrors | null> => {
    let credentials = {
      url: control.get('url')?.value,
      username: control.get('username')?.value,
      password: control.get('password')?.value,
    }
    return new Observable<ValidationErrors | null>(subscriber => {
      this.gitService.fetch(credentials).subscribe({
        next: () => subscriber.next(null),
        error: (e) => subscriber.next({credentials: {value: e.name}}),
      })
    })
  }

}
