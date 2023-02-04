"""
------------------------------------------ Read file and Extract Columns Required------------------------------------
"""

# Read the output file from the metaphlan run
with open("2AD-2m_S6.metaphlan.txt", mode="r") as f:
    output = f.readlines()

filtered = output[5:]
splits = [entry.split("\t") for entry in filtered]

"""
CLASSIFICATION_TO_SUBSPECIES_LEVEL = 8
CLASSIFICATION_TO_SPECIES_LEVEL = 7
CLASSIFICATION_TO_GENUS_LEVEL = 6
"""

# Taxonomic classifications
subSpeciesLevelLevelClassification = list()
speciesLevelClassification = list()
genusLevelClassification = list()

"""
------------------------------------------------------Algorithm Section------------------------------------------------
"""

# For each row in the metaphlan output file
for row in splits:

    # Split the "clade_name" by | and check the length.
    # Also ensure the maximum split is 8 (Kingdom --> Subspecies level == 8 steps)
    check = row[0].split("|", 8)

    # Run some checks to determine which one it is
    # We will only check for subspecies(8), species and genus
    if len(check) == 8:
        # print(check)
        subSpeciesLevelLevelClassification.append(row)

    elif len(check) == 7:
        # print(check)
        speciesLevelClassification.append(row)

    elif len(check) == 6:
        genusLevelClassification.append(row)

    else:
        # print(f'This has not been classified: {row}')
        pass

""" 
  The logic in this block of the algorithm since we have extracted all the species into one list --> 
        speciesLevelClassification, we can now proceed to loop through the list. When we loop through 
            the list, we will verify some conditions and perform some condition mapping.

                 -------------------------------Kingdom ------------------------------- Level 1
                                                   |
                        -------------------------Phylum ------------------------- Level 2
                                                   | 
                        ------------------------ Class ---------------------- Level 3
                                                   |
                            --------------------- Order -------------------- Level 4
                                                   |
                                   ------------  Family ------------ Level 5
                                                   |
                                      ---------- Genus ----------  Level 6
                                                   |
                                        -------- Species ------- Level 7
                                                   |
                                           --- Sub-species--- Level 8                 


        Every level encompasses all the other levels that come before it. Therefore, species level for example contains
                                    {Genus, Family, Order, Class, Phylum, Kingdom}
                
    So in the code block in the next section, what we will do is, loop through the species list and run some checks
      for the presence of '_unclassified' in the genus [-2] and in the species[-1] in the clade_name 
                                            after we split by (|)

"""

# Instantiate new list that will keep the filtered outputs

filteredSpecies = list()
filteredGenus = list()
classifiedGenusandSpecies = list()
allUnclassified = list()

for taxa in speciesLevelClassification:
    verify = taxa[0].split("|")

    # First check if genus contains unclassified but the species is classified, then we append to speciesList
    # Here, we end up with a list in which the species are classified.
    if verify[-2].__contains__("_unclassified") and not verify[-1].__contains__(
        "_unclassified"
    ):
        # print(specie)
        filteredSpecies.append(taxa)

    # Here, normally we should end up with a list in which the genus is classified but the species is unclassified.
    # The logic here is that, if the genus is classified and the species is not, we can consider it as genus classified,
    # and then we can add that to the filteredGenus list. However, there is a problem here since there is nothing like
    # in the file. Therefore, we need to review the logic or simply ignore this and use the list in which both the genus
    # and the species are classified --> classifiedGenusandSpecies
    elif verify[-1].__contains__("_unclassified") and not verify[-2].__contains__(
        "_unclassified"
    ):
        # print(taxa) ---> Nothing prints out
        # There is a problem here because if we try to check for the ones in which the genus is classified
        # but not the species then we end up with nothing
        pass

    # This will give us a list that contains classification for both the genus and the species.
    elif not verify[-1].__contains__("_unclassified") and not verify[-2].__contains__(
        "_unclassified"
    ):
        classifiedGenusandSpecies.append(taxa)

    else:
        pass


def extractionProcessor(extract: list):
    body = list()
    for line in extract:
        lineToString = " ".join(line)
        stringSeperator = lineToString.split(" ")
        extraction = [
            stringSeperator[0],
            stringSeperator[2],
            stringSeperator[4].replace("\n", ""),
        ]
        body.append(extraction)

    return body

# This is simply for colored output
class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def csvWriter(extract: list, filename: str):
    import csv
    from time import sleep

    # Call the extractionProcessor function on the extracted taxa
    extract = extractionProcessor(extract)

    def progres():
        for i in range(4):
            print(
                f"\r{bcolors.HEADER}Saving as {filename} Please wait{'.' * i}{bcolors.ENDC}",
                end="",
            )
            sleep(0.5)

    # The headers of interest
    headers = [
        "clade_name",
        "relative_abundance",
        "estimated_number_of_reads_from_the_clade",
    ]
    progres()
    with open(filename, "w", newline="") as file:
        csvwriter = csv.writer(file)
        csvwriter.writerow(headers)
        csvwriter.writerows(extract)

    # print(classifiedGenusandSpecies)

    print(
        f"\n{bcolors.OKGREEN}Successfully wrote the extraction to a CSV file: {filename}{bcolors.ENDC}"
    )


csvWriter(classifiedGenusandSpecies, "classifiedGenusandSpecies.csv")
