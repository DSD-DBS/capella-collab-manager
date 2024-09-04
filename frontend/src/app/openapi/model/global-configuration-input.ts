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

import { NavbarConfigurationInput } from './navbar-configuration-input';
import { MetadataConfigurationInput } from './metadata-configuration-input';
import { FeedbackConfigurationInput } from './feedback-configuration-input';


/**
 * Global application configuration.
 */
export interface GlobalConfigurationInput { 
    metadata?: MetadataConfigurationInput;
    navbar?: NavbarConfigurationInput;
    feedback?: FeedbackConfigurationInput;
}

