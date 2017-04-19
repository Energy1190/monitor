FROM fluent/fluentd:edge

USER root
RUN apk update \
    && apk upgrade \
    && apk add --no-cache ca-certificates ruby ruby-irb \
    && apk add --no-cache --virtual .build-deps build-base ruby-dev curl-dev libffi-dev \
    && fluent-gem install fluent-plugin-mongo \
    && gem install fluent-plugin-systemd -v 0.2.0

USER fluent
WORKDIR /home/fluent

EXPOSE 24224 5140

CMD exec fluentd -c /fluentd/etc/$FLUENTD_CONF -p /fluentd/plugins $FLUENTD_OPT