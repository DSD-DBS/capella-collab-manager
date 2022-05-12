import { Component, OnInit } from '@angular/core';
import { Repository } from 'src/app/schemes';
import { RepositoryService } from 'src/app/services/repository/repository.service';
import { UserService } from 'src/app/services/user/user.service';
import { Router } from '@angular/router';
import { ActivatedRoute } from '@angular/router';

@Component({
  selector: 'app-delete-repository',
  templateUrl: './delete-repository.component.html',
  styleUrls: ['./delete-repository.component.css'],
})
export class DeleteRepositoryComponent implements OnInit {

  constructor(
    public userService: UserService,
    public repoService: RepositoryService,
    private router: Router,
    private route: ActivatedRoute
  ) {}

  repository_name = ''
  repository = {} as Repository
  isStaged = false;

  ngOnInit(): void {
    this.route.params.subscribe((params) => {
    this.repository_name = params['repository'];
    });
    this.getCurrentRepository();
  }

  stageStatus(): void{
    console.log(this.repository)
    if (this.repository.staged_by !=  null){
      this.isStaged = true;
    }
    else {
      this.isStaged = false;
    }
  }

  getCurrentRepository(): void {
    this.repoService.getRepositories().subscribe((res: Array<Repository>) => {
      this.repository =
      res.filter((r) => r.repository_name == this.repository_name)[0];
      this.stageStatus();
    });
  }

  deleteRepository(): void {
    if (this.repository.staged_by === this.userService.getUsernameFromLocalStorage()){
      	throw new Error('The repository can not staged and deleted by the same person.')
    }
    this.repoService.deleteRepository(this.repository_name).subscribe(() => {
      this.repoService.refreshRepositories();
      this.router.navigateByUrl('/settings');
      }
  )}

  stageForProjectDeletion(): void {
    this.repoService.stageForProjectDeletion(
      this.repository_name,
      this.userService.getUsernameFromLocalStorage()
      )
        .subscribe(() => {
        this.repoService.refreshRepositories();
        this.router.navigateByUrl('/settings');
      }
  )}

  goBack(): void {
    this.router.navigateByUrl('/settings/projects/' + this.repository_name);
  }
}
