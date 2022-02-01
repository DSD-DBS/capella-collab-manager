import { Component, OnInit } from '@angular/core';
import { UserService } from 'src/app/services/user/user.service';

@Component({
  selector: 'app-no-repository',
  templateUrl: './no-repository.component.html',
  styleUrls: ['./no-repository.component.css'],
})
export class NoRepositoryComponent implements OnInit {
  constructor(public userService: UserService) {}

  ngOnInit(): void {}
}
