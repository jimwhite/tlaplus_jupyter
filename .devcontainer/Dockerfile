FROM quay.io/jupyter/minimal-notebook:python-3.13

USER root

RUN apt-get update \
    && apt-get install -y --no-install-recommends openjdk-21-jre-headless \
    && mkdir -p /opt/tlaplus_jupyter \
    && chown ${NB_UID}:${NB_GID} /opt/tlaplus_jupyter \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER ${NB_UID}

ENV TLAPLUS_JUPYTER_TLA2TOOLS_JAR=/opt/tlaplus_jupyter/tla2tools.jar

WORKDIR /workspaces/tlaplus_jupyter
COPY --chown=${NB_UID}:${NB_GID} . /workspaces/tlaplus_jupyter

RUN pip install -e .[dev] \
    && python -m tlaplus_jupyter.install --sys-prefix --tlc-exec-stats disable \
    && cp tlaplus_jupyter/vendor/tla2tools.jar "$TLAPLUS_JUPYTER_TLA2TOOLS_JAR"
