# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

FROM jupyter/minimal-notebook

ARG UID=1001

USER 0
RUN useradd -l -m -u $UID -G users techuser
RUN echo "techuser:tmp_passwd" | chpasswd
ENV HOME=/home/techuser
RUN chown techuser /home/techuser

USER techuser
