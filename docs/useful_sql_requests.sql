SELECT distinct data.section_file_id, section_file.file_name FROM data, section_file where data.section_file_id=section_file.id

CREATE INDEX data_index on data (section_file_id, aoa, reynolds, ncrit, mach);