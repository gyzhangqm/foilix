-- Schema for to-do application examples.

-- sections are 2d foil sections
--create table section (
--    id              integer primary key autoincrement not null,
--    name            text UNIQUE,
--    description     text,
--    is_symmetrical  integer,
--    max_thickness   real,
--    max_thickness_x real,
--    le_radius       real
--);


-- possibly same file name but different origins
create table section_file (
    id              integer primary key autoincrement not null,
    file_name       text,
    file_sha256     text,
    origin          text,
    nb_points       integer,
    is_symmetrical  integer,
    max_thickness   real,
    max_thickness_x real,
    le_radius       real,
    closed_te       integer,
    UNIQUE (file_name, file_sha256, origin)
);

create table section_file_coords(
    section_file_id   integer REFERENCES section_file,
    point_order       integer,
    x                 real,
    y                 real,
    UNIQUE (section_file_id, point_order)
);


-- Source type can be simulation, experiment ...

create table source_type(
    id          integer primary key autoincrement not null,
    name        text,
    description text
);

-- source can be Xfoil, openfoam, wind tunnel experiment by x at location y ...

create table source(
    id              integer primary key autoincrement not null,
    name            text,
    description     text,
    source_type_id  integer REFERENCES source_type
);

-- characteristics should be computed from data
create table characteristics(
    section_file_id integer REFERENCES section_file,
    reynolds        integer,
    ncrit           real,
    mach            real,
    zero_lift_angle real,
    cl_max          real,
    cl_max_angle    real,
    cd_min          real,
    cd_min_angle    real,
    ld_max          real,
    ld_max_angle    real,
    source_id       integer REFERENCES source,
    UNIQUE (section_file_id, reynolds, ncrit, mach, source_id)
);

create table data(
    section_file_id integer REFERENCES section_file,
    aoa         real,
    reynolds    integer,
    ncrit       real,
    mach        real,
    status      integer,
    cl          real,
    cd          real,
    cdp         real,
    cm          real,
    top_xtr     real,
    bot_xtr     real,
    source_id   integer REFERENCES source,
    UNIQUE (section_file_id, aoa, reynolds, ncrit, mach, source_id)
);
