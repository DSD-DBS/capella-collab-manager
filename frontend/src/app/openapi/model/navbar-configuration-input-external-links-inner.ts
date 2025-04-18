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

import { BuiltInNavbarLink } from './built-in-navbar-link';
import { Role } from './role';
import { CustomNavbarLink } from './custom-navbar-link';
import { BuiltInLinkItem } from './built-in-link-item';


export interface NavbarConfigurationInputExternalLinksInner { 
    name: string;
    /**
     * Role required to see this link.
     */
    role: Role;
    /**
     * Built-in service to link to.
     */
    service: BuiltInLinkItem;
    /**
     * URL to link to.
     */
    href: string;
}
export namespace NavbarConfigurationInputExternalLinksInner {
}


