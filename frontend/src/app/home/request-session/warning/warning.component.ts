import { Component, Input, OnInit } from '@angular/core';

@Component({
  selector: 'app-warning',
  templateUrl: './warning.component.html',
  styleUrls: ['./warning.component.css'],
})
export class WarningComponent implements OnInit {
  constructor() {}

  ngOnInit(): void {}

  @Input()
  persistent = true;

  @Input()
  warning = '';
}
