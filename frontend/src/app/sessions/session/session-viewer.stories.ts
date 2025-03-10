/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { SafeResourceUrl } from '@angular/platform-browser';
import {
  componentWrapperDecorator,
  Meta,
  moduleMetadata,
  StoryObj,
} from '@storybook/angular';
import { BehaviorSubject } from 'rxjs';
import { SessionPreparationState, SessionState } from 'src/app/openapi';
import {
  SessionViewerService,
  ViewerSession,
} from 'src/app/sessions/session/session-viewer.service';
import { mockFullscreenServiceProvider } from 'src/storybook/fullscreen';
import {
  mockPersistentSession,
  mockReadonlySession,
} from 'src/storybook/session';
import { mockHttpConnectionMethod } from 'src/storybook/tool';
import { SessionViewerComponent } from './session-viewer.component';

// Add some margin that usually used for the navbar in non-fullscreen mode
const nonFullscreenWrapper = componentWrapperDecorator(
  (story) =>
    `<div class="mx-3 mb-2 md:mt-[100px] mt-[58px] md:mx-5">
      ${story}
    </div>`,
);

const nonFullscreenDecorators = [
  moduleMetadata({
    providers: [mockFullscreenServiceProvider(false)],
  }),
  nonFullscreenWrapper,
];

const meta: Meta<SessionViewerComponent> = {
  title: 'Session Components/Session Viewer',
  component: SessionViewerComponent,
  parameters: {
    layout: 'fullscreen',
  },
  decorators: [
    moduleMetadata({
      providers: [mockFullscreenServiceProvider(true)],
    }),
  ],
};

export default meta;
type Story = StoryObj<SessionViewerComponent>;

class MockSessionViewerService implements Partial<SessionViewerService> {
  private _sessions = new BehaviorSubject<ViewerSession[] | undefined>(
    undefined,
  );
  public readonly sessions$ = this._sessions.asObservable();
  public readonly allSessions$ = this._sessions.asObservable();

  constructor(sessions: ViewerSession[] | undefined) {
    this._sessions.next(sessions);
  }

  // eslint-disable-next-line @typescript-eslint/no-empty-function
  clearSessions(): void {}
}

const mockPersistentViewerSession: ViewerSession = {
  ...mockPersistentSession,
  safeResourceURL: 'about:blank' as SafeResourceUrl,
  focused: true,
  reloadToResize: false,
  fullscreen: false,
  disabled: false,
  connectionInfo: {
    local_storage: {},
    t4c_token: 'token',
    redirect_url: 'about:blank',
  },
};

const mockReadOnlyViewerSession: ViewerSession = {
  ...mockReadonlySession,
  safeResourceURL: 'about:blank' as SafeResourceUrl,
  focused: false,
  reloadToResize: false,
  fullscreen: false,
  disabled: false,
};

const mockSessionServiceProvider = (sessions: ViewerSession[] | undefined) => {
  return {
    provide: SessionViewerService,
    useValue: new MockSessionViewerService(sessions),
  };
};

export const Loading: Story = {};

export const OneSuccessfulSessionNonFullscreen: Story = {
  decorators: [
    ...nonFullscreenDecorators,
    moduleMetadata({
      providers: [mockSessionServiceProvider([mockPersistentViewerSession])],
    }),
  ],
};

export const OneSuccessfulSession: Story = {
  decorators: [
    moduleMetadata({
      providers: [
        mockSessionServiceProvider([mockPersistentViewerSession]),
        mockFullscreenServiceProvider(true),
      ],
    }),
  ],
};

export const TwoSessionsTiling: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        mockSessionServiceProvider([
          {
            ...mockPersistentViewerSession,
            connection_method: {
              ...mockHttpConnectionMethod,
              sharing: { enabled: true },
            },
            version: {
              ...mockPersistentViewerSession.version,
              name: 'with sharing',
              tool: {
                ...mockPersistentViewerSession.version.tool,
                name: 'Tool',
              },
            },
          },
          mockReadOnlyViewerSession,
        ]),
      ],
    }),
  ],
};

export const TwoSessionsTilingPending: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        mockSessionServiceProvider([
          {
            ...mockPersistentViewerSession,
            preparation_state: SessionPreparationState.Pending,
            state: SessionState.Pending,
            connectionInfo: undefined,
            connection_method: {
              ...mockHttpConnectionMethod,
              sharing: { enabled: true },
            },
            version: {
              ...mockPersistentViewerSession.version,
              name: 'with sharing',
              tool: {
                ...mockPersistentViewerSession.version.tool,
                name: 'Tool',
              },
            },
          },
          {
            ...mockReadOnlyViewerSession,
            connectionInfo: undefined,
            preparation_state: SessionPreparationState.Completed,
            state: SessionState.Failed,
          },
        ]),
      ],
    }),
  ],
};

export const OneSessionTilingPending: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        mockSessionServiceProvider([
          {
            ...mockPersistentViewerSession,
            preparation_state: SessionPreparationState.Completed,
            state: SessionState.Pending,
          },
        ]),
      ],
    }),
  ],
};
