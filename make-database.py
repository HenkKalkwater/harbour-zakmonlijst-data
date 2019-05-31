#!/bin/python
# Tested for Python 3.7.3
import argparse
import csv
import os
import sqlite3
import sys

parser = argparse.ArgumentParser(description="Generate the SQLITE database from the PokéApi files");
parser.add_argument("-o", "--output", help="The location of the generated SQLite database", default="database.sqlite");
parser.add_argument("-v", "--verbose", help="Make the output verbose", action="store_true");
parser.add_argument("-i", "--input-dir", help="Root folder of the CSV files", default="data/v2/csv/", dest="input_dir")
args = parser.parse_args();

def logd(message):
    if args.verbose:
        print(message)

if not args.input_dir.endswith("/"):
    args.input_dir += "/"

try:
    os.remove(args.output)
    # ugly as heck, but hey, it's a script, not a fully-fletched program running in production
    logd(f"{args.output} already exists, removing...")
except OSError:
    logd(f"Created {args.output}")

con = sqlite3.connect(args.output);


####################################################################################################
# TABLE CREATION                                                                                   #
####################################################################################################

logd("Creating tables...")
c = con.cursor();

# Languages
c.execute('''CREATE TABLE IF NOT EXISTS languages (
                id                  INTEGER PRIMARY KEY,
                iso639              TEXT NOT NULL,
                iso3166             TEXT NOT NULL,
                identifier          TEXT NOT NULL,
                official            INTEGER NOT NULL,
                "order"             INTEGER NOT NULL )''');
logd(" - Created language table");

# Regions
c.execute('''CREATE TABLE IF NOT EXISTS regions (
                id                  INTEGER PRIMARY KEY,
                identifier          TEXT NOT NULL)''');
logd(" - Created regions table");

# Region names
c.execute('''CREATE TABLE IF NOT EXISTS region_names (
                region_id          INTEGER NOT NULL,
                local_language_id   INTEGER NOT NULL,
                name                TEXT NOT NULL,
                FOREIGN KEY(region_id) REFERENCES regions(id),
                FOREIGN KEY(local_language_id) REFERENCES languages(id),
                PRIMARY KEY(region_id, local_language_id))''');

logd(" - Created region_names table");

# Versions
c.execute('''CREATE TABLE IF NOT EXISTS versions (
                id                  INTEGER PRIMARY KEY,
                version_group_id    INTEGER NOT NULL,
                identifier          TEXT NOT NULL)''');
logd(" - Created versions table");

# Version Names
c.execute('''CREATE TABLE IF NOT EXISTS version_names (
                version_id          INTEGER NOT NULL,
                local_language_id   INTEGER NOT NULL,
                name                TEXT NOT NULL,
                FOREIGN KEY(version_id) REFERENCES versions(id),
                FOREIGN KEY(local_language_id) REFERENCES languages(id),
                PRIMARY KEY(version_id, local_language_id))''');

logd(" - Created version names table");

# Generations
c.execute('''CREATE TABLE IF NOT EXISTS generations (
                id                  INTEGER PRIMARY KEY,
                main_region_id      INTEGER NOT NULL,
                identifier          TEXT NOT NULL,
                FOREIGN KEY(main_region_id) REFERENCES regions(id))''');
logd(" - Created generations table")

# Types
c.execute('''CREATE TABLE IF NOT EXISTS types (
                id                  INTEGER PRIMARY KEY,
                identifier          TEXT NOT NULL,
                generation_id       INTEGER NOT NULL,
                damage_class_id     INTEGER NOT NULL,
                FOREIGN KEY(generation_id) REFERENCES generations(id))''')
                # Foreign key for damage id missing
logd(" - Created types table")

# Type names
c.execute('''CREATE TABLE IF NOT EXISTS type_names (
                type_id             INTEGER NOT NULL,
                local_language_id   INTEGER NOT NULL,
                name                TEXT NOT NULL,
                FOREIGN KEY(local_language_id) REFERENCES languages(id),
                FOREIGN KEY(type_id) REFERENCES types(id),
                PRIMARY KEY(type_id, local_language_id))''');

logd(" - Created type names table");


# Pokedexes
c.execute('''CREATE TABLE IF NOT EXISTS pokedexes (
                id                  INTEGER PRIMARY KEY,
                region_id           INTEGER,
                identifier          TEXT NOT NULL,
                is_main_series      INTEGER NOT NULL,
                FOREIGN KEY(region_id) REFERENCES regions(id))''');
logd(" - Created pokedexes table");


# Pokédexes proses
c.execute('''CREATE TABLE IF NOT EXISTS pokedex_prose (
                pokedex_id          INTEGER NOT NULL,
                local_language_id   INTEGER NOT NULL,
                name                TEXT NOT NULL,
                description         TEXT,
                FOREIGN KEY(pokedex_id) REFERENCES pokedexes(id),
                FOREIGN KEY(local_language_id) REFERENCES languages(id),
                PRIMARY KEY(pokedex_id, local_language_id))''');
logd(" - Created pokedex_proses table")


##############
# Pookiemans #
##############

# Colours
c.execute('''CREATE TABLE IF NOT EXISTS pokemon_colors (
                id                  INTEGER PRIMARY KEY,
                identifier          TEXT NOT NULL)''');
logd(" - Created pokemon_colors table")

# Colour names
c.execute('''CREATE TABLE IF NOT EXISTS pokemon_color_names (
                pokemon_color_id    INTEGER NOT NULL,
                local_language_id   INTEGER NOT NULL,
                name                TEXT NOT NULL,
                FOREIGN KEY(pokemon_color_id) REFERENCES pokemon_colors(id),
                FOREIGN KEY(local_language_id) REFERENCES languages(id),
                PRIMARY KEY(pokemon_color_id, local_language_id))''');
logd(" - Created pokemon_color_names table");

# Evolution Chains
c.execute('''CREATE TABLE IF NOT EXISTS evolution_chains (
                id                  INTEGER PRIMARY KEY,
                baby_trigger_item_id    INTEGER)''')
                # Missing foreign key reference to items
logd(" - Created evolution_chains table");

# Species
c.execute('''CREATE TABLE IF NOT EXISTS pokemon_species (
                id                  INTEGER PRIMARY KEY,
                identifier          TEXT NOT NULL,
                generation_id       INTEGER NOT NULL,
                evolves_from_species_id INTEGER,
                evolution_chain_id  INTEGER,
                color_id            INTEGER NOT NULL,
                shape_id            INTEGER NOT_NULL,
                habitat_id          INTEGER,
                gender_rate         INTEGER,
                capture_rate        INTEGER,
                base_happiness      INTEGER,
                is_baby             INTEGER NOT NULL,
                hatch_counter       INTEGER,
                has_gender_differences  INTEGER,
                growth_rate_id      INTEGER,
                forms_switchable    INTEGER,
                "order"             INTEGER,
                conquest_order      INTEGER,
                FOREIGN KEY(generation_id) REFERENCES generations(id),
                FOREIGN KEY(color_id) REFERENCES pokemon_colors(id))''');
                # Missign foreign keys from shape_id, habitat_id, growth_rate_id
logd(" - Created pokemon_species table")

c.execute('''CREATE TABLE IF NOT EXISTS pokemon (
                id                  INTEGER PRIMARY KEY,
                identifier          INTEGER NOT NULL,
                species_id          INTEGER NOT NULL,
                height              INTEGER NOT NULL,
                weight              INTEGER NOT NULL,
                base_experience     INTEGER NOT NULL,
                "order"             INTEGER NOT NULL,
                is_default          INTEGER,
                FOREIGN KEY(species_id) REFERENCES pokemon_species(id))''');
logd(" - Created pokemon table")

# Pokédex numbers
c.execute('''CREATE TABLE IF NOT EXISTS pokemon_dex_numbers (
                species_id          INTEGER NOT NULL,
                pokedex_id          INGEGER_NOT_NULL,
                pokedex_number      INTEGER NOT_NULL,
                FOREIGN KEY(species_id) REFERENCES pokemon_species(id),
                FOREIGN KEY(pokedex_id) REFERENCES pokedexes(id),
                PRIMARY KEY(species_id, pokedex_id))''')
logd(" - Created pokemon_dex_numbers table")

# Types
c.execute('''CREATE TABLE IF NOT EXISTS pokemon_types (
                pokemon_id          INTEGER NOT NULL,
                type_id             INTEGER_NOT_NULL,
                slot                INTEGER_NOT_NULL,
                FOREIGN KEY(pokemon_id) REFERENCES pokemon(id),
                FOREIGN KEY(type_id) REFERENCES types(id),
                PRIMARY KEY(pokemon_id, type_id))''')
logd(" - Created pokemon_types table")

# Species names
c.execute('''CREATE TABLE IF NOT EXISTS pokemon_species_names (
                pokemon_species_id  INTEGER NOT NULL,
                local_language_id   INTEGER NOT NULL,
                name                TEXT,
                genus               TEXT,
                FOREIGN KEY(pokemon_species_id) REFERENCES pokemon_species(id),
                FOREIGN KEY(local_language_id)  REFERENCES languages(id))''');
logd(" - Created pokemon_species_names table");

# Species text
c.execute('''CREATE TABLE IF NOT EXISTS pokemon_species_flavor_text (
                species_id          INTEGER NOT NULL,
                version_id          INTEGER NOT NULL,
                language_id         INTEGER NOT NULL,
                flavor_text         TEXT NOT NULL,
                FOREIGN KEY(species_id) REFERENCES pokemon_species(id),
                FOREIGN KEY(version_id) REFERENCES versions(id),
                FOREIGN KEY(language_id) REFERENCES languages(id),
                PRIMARY KEY(species_id, version_id, language_id))''');
logd(" - Created pokemon_species_flavor_text table")


####################################################################################################
# TABLE FILLING                                                                                    #
####################################################################################################
logd("Filling tables...")

def fill_table(table_name, field_names, file_name):
    with open(args.input_dir + file_name, "r") as csvfile:
        csvreader = csv.reader(csvfile)
        qmarks = "("
        for i in range(0, len(field_names)):
            qmarks += "?,"
        qmarks = qmarks[:-1]
        qmarks += ")"
        i = 0
        for row in csvreader:
            if i == 0:
                i += 1
                continue;
            # SQL injection lol
            c.execute(f"INSERT INTO {table_name} {str(field_names)}  VALUES {qmarks}", row)
    logd(f" - Filled {table_name} table")

fill_table("languages", ("id", "iso639", "iso3166", "identifier", "official", "order"), "languages.csv")
fill_table("regions", ("id", "identifier"), "regions.csv")
fill_table("region_names", ("region_id", "local_language_id", "name"), "region_names.csv")
fill_table("generations", ("id", "main_region_id", "identifier"), "generations.csv")
fill_table("versions", ("id", "version_group_id", "identifier"), "versions.csv")
fill_table("version_names", ("version_id", "local_language_id", "name"), "version_names.csv")
fill_table("types", ("id", "identifier", "generation_id", "damage_class_id"), "types.csv")
fill_table("type_names", ("type_id", "local_language_id", "name"), "type_names.csv")
fill_table("pokedexes", ("id", "region_id", "identifier", "is_main_series"), "pokedexes.csv")
fill_table("pokemon_colors", ("id", "identifier"), "pokemon_colors.csv")
fill_table("pokemon_color_names", ("pokemon_color_id", "local_language_id", "name"), "pokemon_color_names.csv")

fill_table("evolution_chains", ("id", "baby_trigger_item_id"), "evolution_chains.csv")
fill_table("pokemon_species", ("id", "identifier", "generation_id", "evolves_from_species_id", "evolution_chain_id", "color_id","shape_id","habitat_id", "gender_rate", "capture_rate", "base_happiness", "is_baby", "hatch_counter", "has_gender_differences", "growth_rate_id", "forms_switchable", "order", "conquest_order"), "pokemon_species.csv")
fill_table("pokemon_species_names", ("pokemon_species_id", "local_language_id", "name", "genus"), "pokemon_species_names.csv")
fill_table("pokemon", ("id", "identifier", "species_id", "height", "weight", "base_experience", "order", "is_default"), "pokemon.csv")
fill_table("pokemon_types", ("pokemon_id", "type_id", "slot"), "pokemon_types.csv")
fill_table("pokemon_species_flavor_text", ("species_id", "version_id", "language_id", "flavor_text"), "pokemon_species_flavor_text.csv")
fill_table("pokedex_prose", ("pokedex_id", "local_language_id", "name", "description"), "pokedex_prose.csv")
fill_table("pokemon_dex_numbers", ("species_id", "pokedex_id", "pokedex_number"), "pokemon_dex_numbers.csv")
logd("Done")
con.commit()
con.close()
