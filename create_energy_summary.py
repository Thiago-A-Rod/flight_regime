# This module creates an energy summary.

import energy_summary
import read_flights

def main():
    data = read_flights.read()
    energy_summary.create_energy_summary(data)

if __name__ == '__main__':
    main()
