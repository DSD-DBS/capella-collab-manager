/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 *
 * Capella Collaboration
 *
 * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).
 * Do not edit the class manually.
 + To generate a new version, run `make openapi` in the root directory of this repository.
 */



export interface AdminScopesInput { 
    /**
     * Manage all users of the application. CREATE/UPDATE can be used to change the role of a user / escalate privileges. Use with caution!
     */
    users?: Set<AdminScopesInput.UsersEnum>;
    /**
     * Grant permission to all sub-resources of ALL projects. Use with caution! If possible, use project scopes instead.
     */
    projects?: Set<AdminScopesInput.ProjectsEnum>;
    /**
     * Manage all tools, including it\'s versions and natures
     */
    tools?: Set<AdminScopesInput.ToolsEnum>;
    /**
     * Manage all announcements
     */
    announcements?: Set<AdminScopesInput.AnnouncementsEnum>;
    /**
     * Allow access to monitoring dashboards, Prometheus and Grafana
     */
    monitoring?: Set<AdminScopesInput.MonitoringEnum>;
    /**
     * See and update the global configuration
     */
    configuration?: Set<AdminScopesInput.ConfigurationEnum>;
    /**
     * Manage Team4Capella servers and license servers
     */
    t4c_servers?: Set<AdminScopesInput.T4cServersEnum>;
    /**
     * Manage Team4Capella repositories
     */
    t4c_repositories?: Set<AdminScopesInput.T4cRepositoriesEnum>;
    /**
     * pure::variants license configuration
     */
    pv_configuration?: Set<AdminScopesInput.PvConfigurationEnum>;
    /**
     * See all events
     */
    events?: Set<AdminScopesInput.EventsEnum>;
}
export namespace AdminScopesInput {
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
    export type AnnouncementsEnum = 'CREATE' | 'DELETE';
    export const AnnouncementsEnum = {
        Create: 'CREATE' as AnnouncementsEnum,
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
    export type PvConfigurationEnum = 'UPDATE' | 'DELETE';
    export const PvConfigurationEnum = {
        Update: 'UPDATE' as PvConfigurationEnum,
        Delete: 'DELETE' as PvConfigurationEnum
    };
    export type EventsEnum = 'GET';
    export const EventsEnum = {
        Get: 'GET' as EventsEnum
    };
}

