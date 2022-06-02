import { Component, OnInit } from '@angular/core';
import { RepositoryService } from 'src/app/services/repository/repository.service';
import { UserService } from 'src/app/services/user/user.service';
import { Repository } from 'src/app/schemes';


@Component({
  selector: 'app-staged-to-delete-overview',
  templateUrl: './staged-to-delete-overview.component.html',
  styleUrls: ['./staged-to-delete-overview.component.css']
})
export class StagedToDeleteOverviewComponent implements OnInit {

  search = '';

  constructor(
    public userService: UserService,
    public repoService: RepositoryService
  ) {}


  stagedRepositories: Array<Repository> = [];

  ngOnInit(): void {
    this.getStagedRepositories();
  }

  stringifyJSON(obj: any): any {
    console.log(obj)
    return JSON.parse(obj)
  }

  getStagedRepositories(){
    this.repoService.getRepositories().subscribe((res: Array<Repository>) => {
      this.stagedRepositories =
        res.filter((r) => !["", null].includes(r.staged_by));
    }
  )};
}
