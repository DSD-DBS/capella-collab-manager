# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import logging
import smtplib
from email.mime import multipart, text

import pydantic

from capellacollab.config import config

from . import exceptions, models


def send_email(
    recipients: list[pydantic.EmailStr],
    email: models.EMailContent,
    logger: logging.LoggerAdapter,
):
    if not (config.smtp and config.smtp.enabled):
        raise exceptions.SMTPNotConfiguredError()

    try:
        with smtplib.SMTP(
            config.smtp.host.split(":")[0], int(config.smtp.host.split(":")[1])
        ) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            smtp.login(config.smtp.user, config.smtp.password)

            logger.info(
                "Sending emails to recipients %s", ", ".join(recipients)
            )

            for recipient in recipients:
                msg = multipart.MIMEMultipart()
                msg["From"] = config.smtp.sender
                msg["To"] = recipient
                msg["Subject"] = email.subject
                msg.attach(text.MIMEText(email.message, "plain"))

                logger.info(
                    "Sending email to '%s' with subject '%s'",
                    recipient,
                    email.subject,
                )

                smtp.sendmail(config.smtp.sender, recipient, msg.as_string())
    except Exception:
        logger.exception("Error while sending email(s).")
