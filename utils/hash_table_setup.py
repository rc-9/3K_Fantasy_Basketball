### HOW TO USE: Import & instantiate class with size parameter and insert elements into table via class method

import logging
import pandas as pd

class HashTable(object):
    """Implements a hashtable that can insert, search, delete items through OPEN ADDRESSING & LINEAR PROBING."""

    def __init__(self, size):
        """Instantiates a hashtable & status-tracking list with corresponding values based on given size parameter."""
        self.size = size
        self.table = [None for i in range(self.size)]
        self.status = ["Empty" for i in range(self.size)]
        self.elem_position = None

    def __str__(self):
        """Returns the string representation of the hashtable."""
        logging.debug(f'status list: {self.status}')
        return str(self.table)

    def insert(self, elem):
        """Performs hash function to determine appropriate location & adds the new element to the table."""
        hash_fx = ord(elem[0]) % self.size

        inserted = False
        while not inserted:
            if self.table[hash_fx] is None:
                # Inserts element at respective position & updates corresponding status accordingly
                self.table[hash_fx] = elem
                self.status[hash_fx] = "Filled"
                inserted = True
            else:
                # Linearly iterates through hashtable (wraps around end) to find empty position to insert element
                hash_fx = (hash_fx + 1) % self.size

    def member(self, elem):
        """Performs hash function, searches for element & returns corresponding boolean value if element exists."""
        hash_fx = ord(elem[0]) % self.size

        i = 0
        while i < self.size:
            # Checks table starting as hash position, & iterates until it hits an "Empty" slot within status list
            if self.table[hash_fx] == elem:
                self.elem_position = hash_fx
                return True
            elif self.table[hash_fx] is None and self.status[hash_fx] == "Empty":
                return False
            else:
                hash_fx = (hash_fx + 1) % self.size
                i += 1
        # If element not found after iterating through entirely filled table once, returns corresponding boolean
        return False

    def delete(self, elem):
        """If element exists (based on position attribute), replaces to None value & updates status accordingly."""

        if self.member(elem):
            self.table[self.elem_position] = None
            self.status[self.elem_position] = "Deleted"
        else:
            logging.info('This element does not currently exist in the hashtable. No deletion executed.')
