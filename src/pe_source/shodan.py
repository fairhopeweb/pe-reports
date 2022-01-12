"""Collect Shodan data."""

# Standard Python Libraries
import threading

# Third-Party Libraries
import numpy

from .data.pe_db.db_query import get_orgs
from .data.shodan.config import api_init
from .data.shodan.shodan_search import run_shodan_thread


class Shodan:
    """Fetch shodan data."""

    def __init__(self, orgs_list):
        """Initialize cybersixgill class."""
        self.orgs_list = orgs_list

    def run_shodan(self):
        """Run shodan calls."""
        orgs_list = self.orgs_list

        # Get orgs from PE database
        pe_orgs = get_orgs()

        # Filter orgs if specified
        if orgs_list == "all":
            pe_orgs_final = pe_orgs
        else:
            pe_orgs_final = []
            for pe_org in pe_orgs:
                if pe_org[2] in orgs_list:
                    pe_orgs_final.append(pe_org)
                else:
                    continue

        # Get list of initialized API objects
        api_list = api_init()

        # Split orgs into groups. # of groups = # of valid API keys = # of threads
        chunk_size = len(api_list)
        chunked_orgs_list = numpy.array_split(numpy.array(pe_orgs_final), chunk_size)

        i = 0
        thread_list = []
        while i < len(chunked_orgs_list):
            thread_name = f"Thread {i+1}:"
            # Start thread
            t = threading.Thread(
                target=run_shodan_thread,
                args=(api_list[i], chunked_orgs_list[i], thread_name),
            )
            t.start()
            thread_list.append(t)
            i += 1

        # Wait until all threads finish to coninue
        for thread in thread_list:
            thread.join()
