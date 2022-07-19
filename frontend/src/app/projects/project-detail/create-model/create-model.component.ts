import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { Observable } from 'rxjs';
import { NavBarService } from 'src/app/navbar/service/nav-bar.service';
import { EmptyModel, ModelService } from 'src/app/services/model/model.service';
import { CreateGitModel, GitModelService } from 'src/app/services/modelsources/git-model/git-model.service';
import { GitReferences, GitSettings, GitSettingsService } from 'src/app/services/settings/git-settings.service';
import { NewModel } from 'src/app/services/model/model.service';
import { ProjectService } from '../../service/project.service';
import { ToolService } from 'src/app/services/tools/tool.service';

@Component({
  selector: 'app-create-model',
  templateUrl: './create-model.component.html',
  styleUrls: ['./create-model.component.css']
})
export class CreateModelComponent implements OnInit {

  createModelBaseForm = new FormGroup({
    name: new FormControl('', Validators.required),
    description: new FormControl(''),
  })

  newModelForm = new FormGroup({
    tool: new FormControl('', Validators.required),
    version: new FormControl('', Validators.required),
    type: new FormControl('', Validators.required),
  })

  existingOfflineModelForm = new FormGroup({
    file: new FormControl('', Validators.required),
  })

  existingGitModelForm = new FormGroup({
    url: new FormControl('', Validators.required),
    username: new FormControl('', Validators.required),
    password: new FormControl('', Validators.required),
    reference: new FormControl(''),
    path: new FormControl(''),
  })

  currentNextForm: string;
  srcResult = "";
  eventSet = false;

  gitModelForm = new FormGroup({
    name: new FormControl('', Validators.required),
    instance: new FormControl('', Validators.required),
    slug: new FormControl('', Validators.required),
    revision: new FormControl('', Validators.required),
    path: new FormControl('', Validators.required),
    entrypoint: new FormControl('', Validators.required),
  })

  tools = ["Capella", "Papyrus"];
  versions = {
    Capella: ["6.0", "5.2", "5.0"],
    Papyrus: ["6.2 (latest)", "6.0 (latest)"],
  };
  selected_versions: string[] = [];
  types = {
    Capella: ["model", "library"],
    Papyrus: ["UML 2.5", "SysML 1.4", "SysML 1.1"],
  };
  selected_types: string[] = [];
  slugs: string[];
  revisions: GitReferences;
  filteredRevisions: GitReferences;
  file_reader = new FileReader();

  constructor(
    private navbarService: NavBarService,
    private gitModelService: GitModelService,
    private gitSettingsService: GitSettingsService,
    private modelService: ModelService,
    public projectService: ProjectService,
    public toolService: ToolService,
    private route: ActivatedRoute,
    private router: Router,
  ) { 
    this.slugs = [];
    this.revisions = {branches: [], tags: []};
    this.filteredRevisions = {branches: [], tags: []};
    this.currentNextForm = '';
  }

  ngOnInit(): void {
    this.route.params.subscribe((params) => {
      this.projectService.init(params.project).subscribe();
    })
    this.toolService.init()
    
    this.existingGitModelForm.controls['username'].disable()
    this.existingGitModelForm.controls['password'].disable()
    this.existingGitModelForm.controls['reference'].disable()
    this.existingGitModelForm.controls['path'].disable()

    Array.from(document.getElementsByClassName("form-radio-button")).forEach(button => {
      if (button.id != "git-model-button") {
        button.addEventListener('click', () => this.eventSet = false)
      }
    })

    this.newModelForm.controls['tool'].valueChanges
    .subscribe(value => {
      this.selected_versions = this.versions[value as ("Capella" | "Papyrus")]
      this.newModelForm.controls['version'].setValue(
        this.versions[value as ("Capella" | "Papyrus")][0]
      )
      this.selected_types = this.types[value as ("Capella" | "Papyrus")]
    })

    this.existingGitModelForm.controls['url'].valueChanges
    .subscribe(value => {
      this.bindToFocusout();
      this.existingGitModelForm.controls['username'].disable();
      this.existingGitModelForm.controls['password'].disable();
      if (value) {
        this.existingGitModelForm.controls['username'].enable();
        this.existingGitModelForm.controls['password'].enable();
      }
    })
    
    this.existingGitModelForm.controls['username'].valueChanges
    .subscribe(value => {
      this.bindToFocusout();
      this.existingGitModelForm.controls['reference'].disable();
      this.existingGitModelForm.controls['path'].disable();
      if (value && (this.existingGitModelForm.get('password') as FormControl).value) {
        this.existingGitModelForm.controls['reference'].enable();
        this.existingGitModelForm.controls['path'].enable();
      }
    })

    this.existingGitModelForm.controls['password'].valueChanges
    .subscribe(value => {
      this.bindToFocusout();
      this.existingGitModelForm.controls['reference'].disable();
      this.existingGitModelForm.controls['path'].disable();
      if (value && (this.existingGitModelForm.get('password') as FormControl).value) {
        this.existingGitModelForm.controls['reference'].enable();
        this.existingGitModelForm.controls['path'].enable();
      }
    })

    this.existingGitModelForm.controls['reference'].valueChanges.subscribe(value => {
      console.log(value)
      console.log(this.filteredRevisions);
      this.filteredRevisions = {
        branches: this.revisions.branches.filter(branch => branch.startsWith(value)),
        tags: this.revisions.tags.filter(tag => tag.startsWith(value))
      }
    })
  }

  getForToolId<Type>(nested_list: {[id:number]: Type[]} | null): Type[] {
    let tool_id: number = (this.newModelForm.get('tool') as FormControl).value
    if (tool_id && nested_list) {
      return nested_list[tool_id]
    }
    return []
  }

  bindToFocusout() {
    if (!this.eventSet){
      this.eventSet = true;
      document.getElementById('username-field')?.addEventListener(
        'focusout',
        () => this.setRevisions()
      )
      document.getElementById('password-field')?.addEventListener(
        'focusout',
        () => this.setRevisions()
      )
    }
  }

  setRevisions() {
    if (this.existingGitModelForm.valid) {
      this.gitSettingsService.getRevisions(
        (this.existingGitModelForm.get('url') as FormControl).value,
        (this.existingGitModelForm.get('username') as FormControl).value,
        (this.existingGitModelForm.get('password') as FormControl).value
      ).subscribe(revisions => {
        this.revisions = revisions;
      })
    }
  }

  getValue(field: string): any {
    return (this.gitModelForm.get(field) as FormControl).value
  }

  onFileSelected() {
    const inputNode: any = document.querySelector('#file');
  
    if (typeof (FileReader) !== 'undefined') {
      const reader = new FileReader();
  
      reader.onload = (e: any) => {
        this.srcResult = e.target.result;
      };
  
      reader.readAsArrayBuffer(inputNode.files[0]);
    }
  }

  filter(val: string): GitReferences {
    return {
      branches: this.revisions.branches.filter(option => {
        option.toLowerCase().indexOf(val.toLowerCase()) === 0;
      }),
      tags: this.revisions.tags.filter(option => {
        option.toLowerCase().indexOf(val.toLowerCase()) === 0;
      })
    }
  }

  onSubmit(): void {
    
    if (this.currentNextForm === 'newModelForm') {
      let name = (this.createModelBaseForm.get('name') as FormControl).value;
      let description = (this.createModelBaseForm.get('description') as FormControl).value;
      let new_model = {
        name,
        description,
        tool_id: (this.newModelForm.get('tool') as FormControl).value,
        version_id: (this.newModelForm.get('version') as FormControl).value,
        type_id: (this.newModelForm.get('type') as FormControl).value,
      } as EmptyModel
      if (this.projectService.project?.slug) {
        this.modelService.createEmpty(this.projectService.project?.slug, new_model)
        .subscribe(result => {
          this.router.navigate([
            '/create-coworking-method',
            this.projectService.project?.slug,
            result.slug,
          ])
        })
      }
    }
  }
  

}
