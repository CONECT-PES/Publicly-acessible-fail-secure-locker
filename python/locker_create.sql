USE locker_db;
drop table locker;
CREATE TABLE locker (id int NOT NULL AUTO_INCREMENT,
    phone varchar(16),
    password varchar(256),
    created_on timestamp default current_timestamp,
    status enum('occupied','available') not null default 'Available',
    primary key (id)
    );

    
