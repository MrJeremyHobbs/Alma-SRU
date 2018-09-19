# Alma-SRU
A module for requesting and parsing SRU data from Alma.

# Example - Single Zone Request
```
from alma.sru import client

isbn = '0738-0895'

# Build SRU request
iz_query = client.make_url(zone="IZ", query=f"alma.isbn={isbn}")

# Make SRU request
iz_query_resp = client.search(iz_query)

# Create SRU response objects
iz = client.parse(iz_query_resp, zone="IZ")
```

# Example - Multi-Zone Async Request

```
from alma.sru import client

issn = '0738-0895'

# Build SRU requests
iz_query = client.make_url(zone="IZ", query=f"alma.issn={issn}")
nz_query = client.make_url(zone="NZ", query=f"alma.issn={issn}")

# make multiple SRU requests at once
urls = [
    iz_query,
    nz_query,
]

(iz_query_resp,
nz_query_resp) = client.searches(urls, 2)

# create SRU response objects
iz = client.parse(iz_query_resp, zone="IZ")
nz = client.parse(nz_query_resp, zone="NZ")
```
# How to Parse Output
The SRU client will return an SRU object that can be called to get various information about the search result.

# How to Parse Search Results

## sru_object.numberOfRecords
Returns the number of records found.

## sru_object.ok
Is either TRUE (no errors encountered) or FALSE (some errors encountered)

## sru_object.errors
Returns any errors encountered.

## sru_object.xml
Returns XML representation of SRU response.

## sru_object.dict
Returns a dictionary of the SRU response.

## sru_object.call_number
Returns the call number.

## sru_object.print_holdings
Returns print holdings (if any) for the item as a list, else a blank list.

## sru_object.have_e_holdings
Is either TRUE or FALSE.

## sru_object.e_holdings
Returns e-holdings (if any) for the item as a list, else a blank list.
