/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { CdkCopyToClipboard } from '@angular/cdk/clipboard';
import {
  AfterViewInit,
  Component,
  Input,
  OnInit,
  Pipe,
  PipeTransform,
  forwardRef,
} from '@angular/core';
import { MatButton } from '@angular/material/button';
import {
  MatExpansionPanel,
  MatExpansionPanelHeader,
  MatExpansionPanelTitle,
} from '@angular/material/expansion';
import { MatIcon } from '@angular/material/icon';
import { MatTooltip } from '@angular/material/tooltip';
import hljs from 'highlight.js';
import { MetadataService } from 'src/app/general/metadata/metadata.service';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import {
  Metadata,
  Project,
  ToolModel,
  UsersTokenService,
} from 'src/app/openapi';
import { getPrimaryGitModel } from 'src/app/projects/models/service/model.service';
import { OwnUserWrapperService } from 'src/app/services/user/user.service';

@Component({
  selector: 'app-model-diagram-code-block',
  styles: [
    '::ng-deep .mat-expansion-indicator::after { border-color: black; }',
  ],
  templateUrl: './model-diagram-code-block.component.html',
  imports: [
    MatExpansionPanel,
    MatExpansionPanelHeader,
    MatExpansionPanelTitle,
    MatIcon,
    MatButton,
    MatTooltip,
    CdkCopyToClipboard,
    forwardRef(() => HighlightPipeTransform),
  ],
})
export class ModelDiagramCodeBlockComponent implements OnInit, AfterViewInit {
  passwordValue?: string;
  metadata?: Metadata;

  constructor(
    private metadataService: MetadataService,
    private userService: OwnUserWrapperService,
    private tokenService: UsersTokenService,
    private toastService: ToastService,
  ) {}

  ngOnInit(): void {
    this.metadataService.backendMetadata.subscribe((metadata) => {
      this.metadata = metadata;
    });
  }

  @Input({ required: true })
  model!: ToolModel;

  @Input({ required: true })
  project!: Project;

  @Input()
  jobId: string | undefined;

  @Input()
  expanded = false;

  ngAfterViewInit(): void {
    hljs.highlightAll();
  }

  get codeBlockContent(): string {
    const basePath = `${this.metadata?.protocol}://${this.metadata?.host}:${this.metadata?.port}`;
    let capellaMBSEFlags =
      '"path": "<Path to the .aird file on your host system>",';

    const primaryGitModel = getPrimaryGitModel(this.model);
    if (primaryGitModel) {
      capellaMBSEFlags = `path="git+${primaryGitModel.path}",
  entrypoint="${primaryGitModel.entrypoint}",
  revision="${primaryGitModel.revision}",`;
    }

    if (primaryGitModel?.password) {
      capellaMBSEFlags += `
  username=input("Please enter the username to access the Git repository."),
  password=getpass.getpass("Please enter the password or personal access token to access the Git repository."),`;
    }

    return `import capellambse
import getpass

model = capellambse.MelodyModel(
  ${capellaMBSEFlags}
  diagram_cache={
    "path": "${basePath}/api/v1/projects/${this.project!.slug}/models/${
      this.model.slug
    }/diagrams/%s${this.jobId ? '?job_id=' + this.jobId : ''}",
    "username": "${this.userService.user?.name}",
    "password": "${this.passwordValue ? this.passwordValue : '**************'}",
  }
)`;
  }

  async insertToken() {
    const expirationDate = new Date();
    expirationDate.setDate(expirationDate.getDate() + 30);
    this.tokenService
      .createTokenForUser({
        title: 'Diagram cache token',
        description: 'Token used to fetch diagrams from the diagram cache',
        expiration_date: expirationDate.toISOString().substring(0, 10),
        source: `diagram viewer of project ${this.project.slug})`,
        scopes: {
          projects: {
            [this.project.slug]: {
              diagram_cache: ['GET'],
            },
          },
        },
      })
      .subscribe((token) => {
        this.passwordValue = token.password;
      });
  }

  showClipboardMessage(): void {
    this.toastService.showSuccess(
      'Code snippet copied to clipboard',
      this.passwordValue
        ? "The code snippet contains a personal access token for the Collaboration Manager. Be careful with it and don't share it with others!"
        : "The code snippet doesn't contain a personal access token. You can insert one with 'Insert token'.",
    );
  }
}

@Pipe({
  name: 'highlight',
  standalone: true,
})
export class HighlightPipeTransform implements PipeTransform {
  transform(value: string, language: string): string {
    return hljs.highlight(value, { language }).value;
  }
}
