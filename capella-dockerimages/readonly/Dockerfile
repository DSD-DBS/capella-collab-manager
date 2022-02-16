# Copyright 2021 DB Netz AG
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
ARG BASE_IMAGE=capella/ease/remote
FROM $BASE_IMAGE

USER root
RUN apt-get update && \
    apt-get install -y git-lfs && \
    rm -rf /var/lib/apt/lists/*

COPY prepare_workspace.py /opt/scripts/prepare_workspace.py
RUN chown -R techuser /opt/capella
ENV EASE_LOG_LOCATION=/proc/1/fd/1

COPY startup.sh /home/techuser/.startup.sh
RUN chmod +x /home/techuser/.startup.sh

COPY git_askpass.py /etc/git_askpass.py
ENV GIT_ASKPASS=/etc/git_askpass.py
RUN chmod +x /etc/git_askpass.py

USER techuser
ENTRYPOINT [ "/home/techuser/.startup.sh" ]
