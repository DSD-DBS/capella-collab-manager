import { Component, Input, OnInit } from '@angular/core';

@Component({
  selector: 'app-model-source',
  templateUrl: './model-source.component.html',
  styleUrls: ['./model-source.component.css'],
})
export class ModelSourceComponent implements OnInit {
  constructor() {}

  @Input()
  repository = '';

  ngOnInit(): void {}
}
