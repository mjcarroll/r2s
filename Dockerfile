FROM ros:kilted-ros-core

RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /r2s

COPY pyproject.toml poetry.lock* ./

RUN /root/.local/bin/poetry install --no-root

COPY . .

RUN /root/.local/bin/poetry install

RUN echo "PATH=/root/.local/bin:${PATH}" >> ${HOME}/.bash_aliases \
    echo "source /opt/ros/kilted/setup.bash" >> ${HOME}/.bash_aliases \
    echo "alias r2s='cd /r2s && poetry run r2s'" >> ${HOME}/.bash_aliases
