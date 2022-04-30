CREATE TABLE IF NOT EXISTS regexp
(
    id     uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    regexp text NOT NULL
);

CREATE TABLE IF NOT EXISTS website_checker
(
    id              uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    url             text    NOT NULL,
    update_interval integer NOT NULL, -- in seconds
    regexp_id       uuid,
    is_run          boolean NOT NULL,
    FOREIGN KEY (regexp_id) REFERENCES regexp (id)
);

CREATE TABLE IF NOT EXISTS metric
(
    id            uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    website_checker_id    uuid      NOT NULL,
    status_code   integer   NOT NULL,
    response_time integer   NOT NULL, -- in ms
    is_match      boolean,
    date_time     timestamp NOT NULL,
    success       boolean   NOT NULL,
    FOREIGN KEY (website_checker_id) REFERENCES website_checker (id)
);
