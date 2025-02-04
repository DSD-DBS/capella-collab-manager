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

import { FeedbackRating } from './feedback-rating';
import { AnonymizedSession } from './anonymized-session';


export interface Feedback { 
    /**
     * The rating of the feedback
     */
    rating: FeedbackRating;
    feedback_text: string | null;
    /**
     * Whether the user wants to share their contact information
     */
    share_contact: boolean;
    /**
     * The sessions the feedback is for
     */
    sessions: Array<AnonymizedSession>;
    trigger: string | null;
}
export namespace Feedback {
}


