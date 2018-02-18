#!/usr/bin/env bash

sqlite3 bot.db "create table conceitos (id integer primary key, lowername text, name text, rank integer)"
