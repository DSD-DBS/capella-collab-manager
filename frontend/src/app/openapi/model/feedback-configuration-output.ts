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

import { FeedbackIntervalConfigurationOutput } from './feedback-interval-configuration-output';


export interface FeedbackConfigurationOutput { 
    /**
     * Enable or disable the feedback system. If enabled, SMTP configuration is required.
     */
    enabled: boolean;
    /**
     * If a feedback form is shown after terminating a session.
     */
    after_session: boolean;
    /**
     * Should a general feedback button be shown.
     */
    on_footer: boolean;
    /**
     * Should a feedback button be shown on the session cards.
     */
    on_session_card: boolean;
    /**
     * Request feedback at regular intervals.
     */
    interval: FeedbackIntervalConfigurationOutput;
    /**
     * Email addresses to send feedback to.
     */
    recipients: Array<string>;
    /**
     * Text to display as a hint in the feedback form.
     */
    hint_text: string;
}

