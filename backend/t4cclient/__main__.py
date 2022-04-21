# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import uvicorn
from t4cclient import app

if __name__ == "__main__":
    uvicorn.run(app)