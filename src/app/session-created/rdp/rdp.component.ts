import { Component, Input, OnInit } from '@angular/core';
import { Session } from 'src/app/schemes';
import { SessionService } from 'src/app/services/session/session.service';

@Component({
  selector: 'app-rdp',
  templateUrl: './rdp.component.html',
  styleUrls: ['./rdp.component.css'],
})
export class RDPComponent implements OnInit {
  @Input()
  session: Session | undefined = undefined;

  constructor() {}

  ngOnInit(): void {}
}
