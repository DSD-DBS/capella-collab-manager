/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import {
  ProjectStatus,
  StatusResponse,
  ToolmodelStatus,
} from 'src/app/openapi';

export const mockGeneralHealthGood: StatusResponse = {
  guacamole: true,
  database: true,
  operator: true,
};

export const mockGeneralHealthBad: StatusResponse = {
  guacamole: false,
  database: false,
  operator: false,
};

export const mockToolmodelStatusesGood: ToolmodelStatus[] = [
  {
    model_slug: 'mock-model-1',
    project_slug: 'mock-project-1',
    diagram_cache_status: 'success',
    model_badge_status: 'success',
    pipeline_status: 'success',
    primary_git_repository_status: 'accessible',
    warnings: [],
  },
];

export const mockToolmodelStatusesBad: ToolmodelStatus[] = [
  {
    model_slug: 'mock-model-1',
    project_slug: 'mock-project-1',
    diagram_cache_status: 'failure',
    model_badge_status: 'failure',
    pipeline_status: 'failure',
    primary_git_repository_status: 'inaccessible',
    warnings: ['Test Warning'],
  },
  {
    model_slug: 'mock-model-2',
    project_slug: 'mock-project-2',
    diagram_cache_status: 'unconfigured',
    model_badge_status: 'unconfigured',
    pipeline_status: 'pending',
    primary_git_repository_status: 'unset',
    warnings: [],
  },
  {
    model_slug: 'mock-model-3',
    project_slug: 'mock-project-3',
    diagram_cache_status: 'unsupported',
    model_badge_status: 'unsupported',
    pipeline_status: 'running',
    primary_git_repository_status: 'accessible',
    warnings: [],
  },
  {
    model_slug: 'mock-model-4',
    project_slug: 'mock-project-4',
    diagram_cache_status: 'unsupported',
    model_badge_status: 'unsupported',
    pipeline_status: 'timeout',
    primary_git_repository_status: 'accessible',
    warnings: [],
  },
  {
    model_slug: 'mock-model-5',
    project_slug: 'mock-project-5',
    diagram_cache_status: 'unsupported',
    model_badge_status: 'unsupported',
    pipeline_status: 'scheduled',
    primary_git_repository_status: 'accessible',
    warnings: [],
  },
  {
    model_slug: 'mock-model-6',
    project_slug: 'mock-project-6',
    diagram_cache_status: 'unsupported',
    model_badge_status: 'unsupported',
    pipeline_status: 'unknown',
    primary_git_repository_status: 'accessible',
    warnings: [],
  },
];

export const mockProjectStatusesGood: ProjectStatus[] = [
  {
    project_slug: 'mock-project-1',
    warnings: [],
  },
];

export const mockProjectStatusesBad: ProjectStatus[] = [
  {
    project_slug: 'mock-project-1',
    warnings: ['Test Warning'],
  },
];
