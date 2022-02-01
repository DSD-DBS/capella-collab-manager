import { Component, Input, OnInit } from '@angular/core';
import { Session } from '../schemes';
import { SessionService } from '../services/session/session.service';

@Component({
  selector: 'app-session-created',
  templateUrl: './session-created.component.html',
  styleUrls: ['./session-created.component.css'],
})
export class SessionCreatedComponent implements OnInit {
  @Input()
  session: Session | undefined = undefined;
  constructor() {}

  ngOnInit(): void {}
}
