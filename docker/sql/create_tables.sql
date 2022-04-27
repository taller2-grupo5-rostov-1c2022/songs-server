CREATE TABLE songs (
    id serial NOT NULL,
    name character varying(50) NOT NULL,
    description character varying(150) NOT NULL,
    creator character varying(50) NOT NULL,
    artists character varying(150) NOT NULL
);

CREATE TABLE albums (
    id serial NOT NULL,
    name character varying(50) NOT NULL,
    description character varying(150) NOT NULL,
    genre integer NOT NULL
);