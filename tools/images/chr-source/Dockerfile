ARG VERSION

FROM uazo/build-deps:$VERSION
ARG VERSION
ENV VERSION=$VERSION

#USER lg
WORKDIR /home/lg/working_dir

COPY prepare-build.sh .

RUN sudo chmod +x ./prepare-build.sh \
    && \
    ./prepare-build.sh

