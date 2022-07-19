import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { single } from 'rxjs';
import { Model, ModelService } from 'src/app/services/model/model.service';
import { Project, ProjectService } from '../../service/project.service';

@Component({
  selector: 'app-create-coworking-method',
  templateUrl: './create-coworking-method.component.html',
  styleUrls: ['./create-coworking-method.component.css']
})
export class CreateCoworkingMethodComponent implements OnInit {

  method = "new-git";
  project_slug = "";
  model_slug = "";
  project: Project | undefined = undefined;
  model: Model | undefined = undefined;
  newGitForm = new FormGroup({
    instance: new FormControl('', Validators.required),
    slug: new FormControl('', Validators.required),
  });
  existingGitForm = new FormGroup({
    url: new FormControl('', Validators.required),
    username: new FormControl('', Validators.required),
    password: new FormControl('', Validators.required),
  });

  constructor(
    private route: ActivatedRoute,
    public projectService: ProjectService,
    public modelService: ModelService
  ) { }

  ngOnInit(): void {
    this.route.params.subscribe(params => {
      this.project_slug = params.project;
      this.model_slug = params.model;
      this.projectService.init(this.project_slug).pipe(single())
      .subscribe(project => {this.project = project;})
      this.modelService.init(this.project_slug, this.model_slug).pipe(single())
      .subscribe(model => {this.model = model;})
    })
  }

}
