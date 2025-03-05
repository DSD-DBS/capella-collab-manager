/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 *
 * Capella Collaboration Manager API
 *
 * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).
 * Do not edit the class manually.
 + To generate a new version, run `make openapi` in the root directory of this repository.
 */



export interface AdminScopesOutput { 
    /**
     * Manage all users of the application. CREATE/UPDATE can be used to change the role of a user / escalate privileges. Use with caution!
     */
    users: Array<AdminScopesOutput.UsersEnum>;
    /**
     * Grant permission to all sub-resources of ALL projects. Use with caution! If possible, use project scopes instead.
     */
    projects: Array<AdminScopesOutput.ProjectsEnum>;
    /**
     * Manage all tools, including its versions and natures
     */
    tools: Array<AdminScopesOutput.ToolsEnum>;
    /**
     * Manage all announcements
     */
    announcements: Array<AdminScopesOutput.AnnouncementsEnum>;
    /**
     * Allow access to monitoring dashboards, Prometheus and Grafana
     */
    monitoring: Array<AdminScopesOutput.MonitoringEnum>;
    /**
     * See and update the global configuration
     */
    configuration: Array<AdminScopesOutput.ConfigurationEnum>;
    /**
     * Manage links to Git server instances
     */
    git_servers: Array<AdminScopesOutput.GitServersEnum>;
    /**
     * Manage Team4Capella servers and license servers
     */
    t4c_servers: Array<AdminScopesOutput.T4cServersEnum>;
    /**
     * Manage Team4Capella repositories
     */
    t4c_repositories: Array<AdminScopesOutput.T4cRepositoriesEnum>;
    /**
     * pure::variants license configuration
     */
    pv_configuration: Array<AdminScopesOutput.PvConfigurationEnum>;
    /**
     * See all events
     */
    events: Array<AdminScopesOutput.EventsEnum>;
    /**
     * See all sessions
     */
    sessions: Array<AdminScopesOutput.SessionsEnum>;
    /**
     * See user workspaces
     */
    workspaces: Array<AdminScopesOutput.WorkspacesEnum>;
    /**
     * Revoke personal access tokens of ALL users.
     */
    personal_access_tokens: Array<AdminScopesOutput.PersonalAccessTokensEnum>;
}
export namespace AdminScopesOutput {
    export type UsersEnum = 'GET' | 'CREATE' | 'UPDATE' | 'DELETE';
    export const UsersEnum = {
        Get: 'GET' as UsersEnum,
        Create: 'CREATE' as UsersEnum,
        Update: 'UPDATE' as UsersEnum,
        Delete: 'DELETE' as UsersEnum
    };
    export type ProjectsEnum = 'GET' | 'CREATE' | 'UPDATE' | 'DELETE';
    export const ProjectsEnum = {
        Get: 'GET' as ProjectsEnum,
        Create: 'CREATE' as ProjectsEnum,
        Update: 'UPDATE' as ProjectsEnum,
        Delete: 'DELETE' as ProjectsEnum
    };
    export type ToolsEnum = 'GET' | 'CREATE' | 'UPDATE' | 'DELETE';
    export const ToolsEnum = {
        Get: 'GET' as ToolsEnum,
        Create: 'CREATE' as ToolsEnum,
        Update: 'UPDATE' as ToolsEnum,
        Delete: 'DELETE' as ToolsEnum
    };
    export type AnnouncementsEnum = 'CREATE' | 'UPDATE' | 'DELETE';
    export const AnnouncementsEnum = {
        Create: 'CREATE' as AnnouncementsEnum,
        Update: 'UPDATE' as AnnouncementsEnum,
        Delete: 'DELETE' as AnnouncementsEnum
    };
    export type MonitoringEnum = 'GET';
    export const MonitoringEnum = {
        Get: 'GET' as MonitoringEnum
    };
    export type ConfigurationEnum = 'GET' | 'UPDATE';
    export const ConfigurationEnum = {
        Get: 'GET' as ConfigurationEnum,
        Update: 'UPDATE' as ConfigurationEnum
    };
    export type GitServersEnum = 'CREATE' | 'UPDATE' | 'DELETE';
    export const GitServersEnum = {
        Create: 'CREATE' as GitServersEnum,
        Update: 'UPDATE' as GitServersEnum,
        Delete: 'DELETE' as GitServersEnum
    };
    export type T4cServersEnum = 'GET' | 'CREATE' | 'UPDATE' | 'DELETE';
    export const T4cServersEnum = {
        Get: 'GET' as T4cServersEnum,
        Create: 'CREATE' as T4cServersEnum,
        Update: 'UPDATE' as T4cServersEnum,
        Delete: 'DELETE' as T4cServersEnum
    };
    export type T4cRepositoriesEnum = 'GET' | 'CREATE' | 'UPDATE' | 'DELETE';
    export const T4cRepositoriesEnum = {
        Get: 'GET' as T4cRepositoriesEnum,
        Create: 'CREATE' as T4cRepositoriesEnum,
        Update: 'UPDATE' as T4cRepositoriesEnum,
        Delete: 'DELETE' as T4cRepositoriesEnum
    };
    export type PvConfigurationEnum = 'GET' | 'UPDATE' | 'DELETE';
    export const PvConfigurationEnum = {
        Get: 'GET' as PvConfigurationEnum,
        Update: 'UPDATE' as PvConfigurationEnum,
        Delete: 'DELETE' as PvConfigurationEnum
    };
    export type EventsEnum = 'GET';
    export const EventsEnum = {
        Get: 'GET' as EventsEnum
    };
    export type SessionsEnum = 'GET';
    export const SessionsEnum = {
        Get: 'GET' as SessionsEnum
    };
    export type WorkspacesEnum = 'GET' | 'DELETE';
    export const WorkspacesEnum = {
        Get: 'GET' as WorkspacesEnum,
        Delete: 'DELETE' as WorkspacesEnum
    };
    export type PersonalAccessTokensEnum = 'DELETE';
    export const PersonalAccessTokensEnum = {
        Delete: 'DELETE' as PersonalAccessTokensEnum
    };
}


